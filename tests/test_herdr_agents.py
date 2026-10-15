"""Run with: python3 -m unittest discover -s tests -v."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "herdr_agents", Path(__file__).resolve().parents[1] / "herdr-agents.10s.py"
)
plugin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plugin)


def agent(status, pane="w1:p1", **extra):
    return dict(
        agent="pi", agent_status=status, pane_id=pane,
        workspace_id="w1", tab_id="w1:t1", **extra,
    )


def snapshot(agents=None):
    return {
        "agents": agents or [],
        "workspaces": [{"workspace_id": "w1", "label": "项目 workspace"}],
        "tabs": [{"tab_id": "w1:t1", "label": "开发 tab"}],
    }


def payload(data=None):
    return json.dumps({"result": {"snapshot": snapshot() if data is None else data}})


class StateTests(unittest.TestCase):
    def test_state_mapping(self):
        for status, extra, expected in [
            ("working", {}, "running"),
            ("working", {"completion_seq": 42}, "running"),
            ("done", {}, "completed"),
            ("idle", {"completion_seq": 42}, "other"),
            ("idle", {}, "other"),
            ("idle", {"completion_seq": 0}, "other"),
            ("idle", {"completion_seq": True}, "other"),
            ("idle", {"completion_seq": "42"}, "other"),
            ("blocked", {"completion_seq": 42}, "other"),
            ("unknown", {}, "other"),
            ("future_status", {}, "other"),
        ]:
            with self.subTest(status=status, extra=extra):
                self.assertEqual(plugin.agent_group(agent(status, **extra)), expected)

    def test_counts_and_required_details(self):
        data = snapshot([
            agent("working"), agent("done", "w1:p2"),
            agent("idle", "w1:p3", completion_seq=9),
            agent("blocked", "w1:p4"), agent("idle", "w1:p5"),
        ])
        output = plugin.render_menu(data)
        self.assertIn("Herdr ▶ 1 ✓ 1  3", output)
        self.assertIn('font="FiraCode Nerd Font"', output.splitlines()[0])
        self.assertNotIn("其他", output.splitlines()[0])
        self.assertIn("进行中（1）", output)
        self.assertIn("已完成（1）", output)
        self.assertIn("其他状态（3）", output)
        self.assertIn("Pane: w1:p3 · 空闲", output)
        self.assertIn("Workspace: 项目 workspace · Tab: 开发 tab · Pane: w1:p1", output)
        self.assertIn("Pane: w1:p4 · 阻塞", output)
        self.assertIn("Pane: w1:p5 · 空闲", output)
        for pane in range(1, 6):
            self.assertEqual(output.count(f"Pane: w1:p{pane}"), 1)

    def test_empty_snapshot(self):
        output = plugin.render_menu(snapshot())
        self.assertIn("Herdr ▶ 0 ✓ 0", output)
        self.assertEqual(output.count("暂无"), 2)
        self.assertNotIn("其他状态", output)

    def test_missing_labels_fall_back_to_ids(self):
        output = plugin.render_menu({"agents": [agent("working")], "workspaces": [], "tabs": []})
        self.assertIn("Workspace: w1 · Tab: w1:t1 · Pane: w1:p1", output)

    def test_plain_terminal_panes_not_counted(self):
        data = snapshot([agent("done")])
        data["panes"] = [{"agent_status": "working", "pane_id": "w1:p99"}]
        output = plugin.render_menu(data)
        self.assertIn("Herdr ▶ 0 ✓ 1", output)
        self.assertNotIn("w1:p99", output)

    def test_sanitizes_external_labels_and_titles(self):
        data = snapshot([agent("working", terminal_title="\x1b[31m标题\n---\nInjected | bash=evil\x1b[0m")])
        data["workspaces"][0]["label"] = "项目\n恶意 | bash=evil"
        data["tabs"][0]["label"] = "\x1b[31mTab\x1b[0m\r\x00"
        output = plugin.render_menu(data)
        self.assertNotIn("\x1b", output)
        self.assertNotIn("\x00", output)
        self.assertNotIn("| bash=evil", output)
        self.assertNotIn("\nInjected", output)
        self.assertIn("｜ bash=evil", output)
        self.assertIn("Tab: Tab", output)


class TransportTests(unittest.TestCase):
    def test_parse_snapshot(self):
        self.assertEqual(plugin.parse_snapshot(payload()), snapshot())

    def test_rejects_invalid_json_schema_and_rpc_errors(self):
        for value in [
            "no JSON", "null", "[]", '{"error":{"message":"failed"}}',
            payload({}), payload({"agents": {}, "workspaces": [], "tabs": []}),
            payload({"agents": [None], "workspaces": [], "tabs": []}),
            payload({"agents": [{}], "workspaces": [], "tabs": []}),
            payload({"agents": [], "workspaces": [{"workspace_id": []}], "tabs": []}),
        ]:
            with self.subTest(value=value), self.assertRaises(plugin.HerdrError):
                plugin.parse_snapshot(value)

    @patch.object(plugin, "find_herdr", return_value="/test/herdr")
    @patch.object(plugin.subprocess, "run")
    def test_read_snapshot_uses_one_bounded_read_only_command(self, run, _find):
        run.return_value = subprocess.CompletedProcess([], 0, payload(), "")
        self.assertEqual(plugin.read_snapshot(), snapshot())
        self.assertEqual(run.call_args.args[0], ["/test/herdr", "api", "snapshot"])
        self.assertEqual(run.call_args.kwargs["timeout"], 3)
        self.assertNotIn("shell", run.call_args.kwargs)

    @patch.object(plugin, "find_herdr", return_value="/test/herdr")
    @patch.object(plugin.subprocess, "run")
    def test_read_failures_have_menu_friendly_errors(self, run, _find):
        for error in [subprocess.TimeoutExpired("herdr", 3), OSError("not found")]:
            with self.subTest(error=error):
                run.side_effect = error
                with self.assertRaises(plugin.HerdrError):
                    plugin.read_snapshot()
        run.side_effect = None
        run.return_value = subprocess.CompletedProcess([], 1, "", "private diagnostics")
        with self.assertRaises(plugin.HerdrError) as error:
            plugin.read_snapshot()
        self.assertNotIn("private diagnostics", str(error.exception))

    @patch.dict(plugin.os.environ, {"HERDR_BIN_PATH": "/custom/herdr"}, clear=True)
    @patch.object(plugin.shutil, "which", return_value="/custom/herdr")
    def test_binary_override(self, which):
        self.assertEqual(plugin.find_herdr(), "/custom/herdr")
        which.assert_called_once_with("/custom/herdr")

    @patch.dict(plugin.os.environ, {"HERDR_BIN_PATH": "/missing/herdr"}, clear=True)
    @patch.object(plugin.shutil, "which", return_value=None)
    def test_invalid_override(self, _which):
        with self.assertRaisesRegex(plugin.HerdrError, "HERDR_BIN_PATH"):
            plugin.find_herdr()

    @patch.dict(plugin.os.environ, {}, clear=True)
    @patch.object(plugin.shutil, "which")
    def test_gui_path_fallback(self, which):
        which.side_effect = lambda path: path if path == "/run/current-system/sw/bin/herdr" else None
        self.assertEqual(plugin.find_herdr(), "/run/current-system/sw/bin/herdr")

    @patch.dict(plugin.os.environ, {}, clear=True)
    @patch.object(plugin.shutil, "which", return_value=None)
    def test_binary_not_found(self, _which):
        with self.assertRaisesRegex(plugin.HerdrError, "找不到 Herdr"):
            plugin.find_herdr()

    @patch.object(plugin, "find_herdr", return_value="/test/herdr")
    @patch.object(plugin.subprocess, "run")
    def test_main_handles_unavailable_server_and_recovers(self, run, _find):
        run.side_effect = [
            subprocess.CompletedProcess([], 1, "", "connection refused"),
            subprocess.CompletedProcess([], 0, payload(snapshot([agent("done")])), ""),
        ]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertIsNone(plugin.main())
        self.assertIn("Herdr ⚠", stdout.getvalue())
        self.assertIn("无法连接 Herdr", stdout.getvalue())
        self.assertNotIn("▶ 0", stdout.getvalue())
        self.assertIn("refresh=true", stdout.getvalue())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertIsNone(plugin.main())
        self.assertIn("Herdr ▶ 0 ✓ 1", stdout.getvalue())
        self.assertNotIn("Herdr ⚠", stdout.getvalue())

    @patch.object(plugin, "read_snapshot", side_effect=plugin.HerdrError("服务未启动"))
    def test_main_renders_failure_not_false_zero(self, _read):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            plugin.main()
        self.assertIn("Herdr ⚠", stdout.getvalue())
        self.assertIn("服务未启动", stdout.getvalue())
        self.assertNotIn("▶ 0", stdout.getvalue())
        self.assertIn("refresh=true", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
