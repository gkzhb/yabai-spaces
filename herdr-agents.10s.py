#!/usr/bin/env python3
# <bitbar.title>Herdr Agents</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.desc>Herdr agent counts and workspace/tab/pane details</bitbar.desc>
# <bitbar.dependencies>python3,herdr</bitbar.dependencies>
"""Read-only SwiftBar plugin. Refresh every ten seconds; no third-party deps."""

import json
import os
import re
import shutil
import subprocess


TIMEOUT_SECONDS = 3
MENU_FONT = "FiraCode Nerd Font"
OTHER_ICON = ""  # nf-fa-ellipsis_h
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class HerdrError(Exception):
    """An actionable error safe to display in the menu."""


def menu_text(value):
    """Do not let external labels inject SwiftBar rows, attributes or ANSI."""
    text = ANSI_ESCAPE.sub("", str(value))
    text = " ".join(text.split())
    return "".join(c for c in text if c.isprintable()).replace("|", "｜")


def find_herdr():
    override = os.environ.get("HERDR_BIN_PATH")
    if override:
        binary = shutil.which(os.path.expanduser(override))
        if not binary:
            raise HerdrError("HERDR_BIN_PATH 指定的 Herdr 不可执行")
        return binary
    binary = shutil.which("herdr")
    if binary:
        return binary
    for candidate in (
        "/run/current-system/sw/bin/herdr",
        "~/.nix-profile/bin/herdr",
        "~/.local/bin/herdr",
        "/opt/homebrew/bin/herdr",
        "/usr/local/bin/herdr",
    ):
        binary = shutil.which(os.path.expanduser(candidate))
        if binary:
            return binary
    raise HerdrError("找不到 Herdr；请配置 HERDR_BIN_PATH")


def parse_snapshot(payload):
    try:
        response = json.loads(payload)
        snapshot = response["result"]["snapshot"]
        for key in ("agents", "workspaces", "tabs"):
            rows = snapshot[key]
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError("invalid collection")
        for key, id_key in (("agents", "pane_id"), ("workspaces", "workspace_id"), ("tabs", "tab_id")):
            for row in snapshot[key]:
                if not isinstance(row.get(id_key), str) or not row[id_key]:
                    raise ValueError("missing identifier")
        return snapshot
    except (ValueError, KeyError, TypeError) as exc:
        raise HerdrError("Herdr 快照格式无效；请检查 herdr api snapshot") from exc


def read_snapshot():
    try:
        result = subprocess.run(
            [find_herdr(), "api", "snapshot"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise HerdrError("Herdr 查询超时；请检查服务状态") from exc
    except (OSError, UnicodeError) as exc:
        raise HerdrError("无法执行 Herdr；请检查安装和访问权限") from exc
    if result.returncode:
        raise HerdrError("无法连接 Herdr；请检查服务或 HERDR_SOCKET_PATH")
    return parse_snapshot(result.stdout)


def agent_group(agent):
    status = agent.get("agent_status")
    if status == "working":
        return "running"
    if status == "done":
        return "completed"
    return "other"


def render_menu(snapshot):
    workspaces = {row["workspace_id"]: row for row in snapshot["workspaces"]}
    tabs = {row["tab_id"]: row for row in snapshot["tabs"]}
    groups = {"running": [], "completed": [], "other": []}
    for agent in snapshot["agents"]:
        groups[agent_group(agent)].append(agent)

    title = f"Herdr ▶ {len(groups['running'])} ✓ {len(groups['completed'])}"
    if groups["other"]:
        title += f" {OTHER_ICON} {len(groups['other'])}"
    lines = [title + f' | dropdown=false font="{MENU_FONT}"', "---"]
    status_labels = {"idle": "空闲", "blocked": "阻塞", "unknown": "未知"}
    for group, heading in (("running", "进行中"), ("completed", "已完成"), ("other", "其他状态")):
        agents = groups[group]
        if group == "other" and not agents:
            continue
        lines.append(f"{heading}（{len(agents)}） | disabled=true")
        for agent in sorted(agents, key=lambda a: (
            str(a.get("workspace_id", "")), str(a.get("tab_id", "")), a["pane_id"]
        )):
            workspace_id = agent.get("workspace_id")
            tab_id = agent.get("tab_id")
            workspace = workspaces.get(workspace_id, {}).get("label") or workspace_id or "未知工作区"
            tab = tabs.get(tab_id, {}).get("label") or tab_id or "未知 Tab"
            label = f"Workspace: {workspace} · Tab: {tab} · Pane: {agent['pane_id']}"
            if group == "other":
                status = agent.get("agent_status") or "unknown"
                label += f" · {status_labels.get(status, status)}"
            lines.append(menu_text(label) + " | ansi=false emojize=false")
            agent_name = menu_text(agent.get("agent") or "unknown")
            lines.append(f"--Agent: {agent_name} | disabled=true")
            terminal_title = agent.get("terminal_title_stripped") or agent.get("terminal_title")
            if terminal_title:
                lines.append("--标题: " + menu_text(terminal_title) + " | ansi=false emojize=false")
        if not agents:
            lines.append("暂无 | disabled=true")
        lines.append("---")
    lines.extend([
        "已完成 = done（idle 不计入） | disabled=true",
        "仅统计当前 Herdr 会话中仍存在的 agent pane | disabled=true",
        "立即刷新 | refresh=true",
    ])
    return "\n".join(lines)


def render_error(message):
    return "\n".join([
        "Herdr ⚠ | dropdown=false",
        "---",
        menu_text(message) + " | disabled=true ansi=false emojize=false",
        "立即刷新 | refresh=true",
    ])


def main():
    try:
        output = render_menu(read_snapshot())
    except HerdrError as exc:
        output = render_error(str(exc))
    print(output)


if __name__ == "__main__":
    main()
