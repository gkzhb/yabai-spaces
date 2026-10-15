# Yabai Spaces

A swiftbar plugin displays yabai spaces, inspired by [SxC97/Yabai-Spaces](https://github.com/SxC97/Yabai-Spaces).

## Features

<img width="478" alt="image" src="https://user-images.githubusercontent.com/36144635/204783828-ccbcf4aa-b423-404e-a5a9-de6c8a3eb245.png">

- Display yabai spaces in Mac OS menu bar.
  - Separate spaces belonging to different monitors (two monitors in the above image, and spaces of them are separated by '>')
  - Highlight current space for each monitor and markup focused space (displayed spaces are in red, focused space is wrapped by '<<' '>>')
  - Show up yabai spaces' labels, and you can easily customize them in a
  simple script

## Requirements

- Python 3
- [koekeishiya/yabai](https://github.com/koekeishiya/yabai)
- [SwiftBar](https://github.com/swiftbar/SwiftBar) or [xbar (the BitBar reboot)](https://github.com/matryer/xbar) (not tested for xbar)
- [chipsenkbeil/choose: Fuzzy matcher for OS X that uses both std{in,out} and a native GUI](https://github.com/chipsenkbeil/choose)(optional): you can use my [Raycast plugin](https://github.com/gkzhb/raycast-yabai) which provides a better UI
- Fira Code Nerd font(optional): you can use other fonts or characters for the separator.

## Installation & Usage

### Yabai Spaces in menu bar

Copy [`yabai.1d.py`](./yabai.1d.py) to your SwiftBar/xbar plugin's directory. And set the variable value of `YABAI_SPACES_PATH` in the file.

If SwiftBar is running, you may see Yabai Spaces in your menu bar.
> If SwiftBar is running and you cannot see it, it might be there is no enough
space to display Yabai Spaces.


There is another file [`yabai-simp.1d.py`](./yabai-simp.1d.py) that shows visible yabai spaces only, which occupies less space in the menu bar.


You'd better press `Command` key and at the same time drag Yabai Spaces menu bar
item to the most right to try to avoid it being hidden when there are plenty of menu
bar tray icons and no space left to display Yabai Spaces.

Add these to your `.yabairc` to rerender Yabai Spaces after some yabai events to
ensure it presents the latest status of spaces:

```bash
# update yabai-spaces in status bar
yabai -m signal --add event=space_changed action="open -gj 'swiftbar://refreshplugin?name=yabai'"
yabai -m signal --add event=window_focused action="open -gj 'swiftbar://refreshplugin?name=yabai'"
yabai -m signal --add event=display_added action="open -gj 'swiftbar://refreshplugin?name=yabai'"
yabai -m signal --add event=display_removed action="open -gj 'swiftbar://refreshplugin?name=yabai'"
yabai -m signal --add event=display_changed action="open -gj 'swiftbar://refreshplugin?name=yabai'"
yabai -m signal --add event=display_moved action="open -gj 'swiftbar://refreshplugin?name=yabai'"
```

You can customize [`yabai.1d.py`](./yabai.1d.py) script as you need.

For example, change the font by set `CUSTOM_FONT` variable.
If you want to customize how the space is displayed, you can edit
`get_space_display_string` function.

### Persist Yabai Space Labels

When you restart Yabai, all the labels of spaces will be reset. And here comes
the scripts to persist these data.

Executing [`rename-space.fish`](./rename-space.fish) (bind this script to a hotkey in skhd is
recommended) will prompt [`choose`](https://github.com/chipsenkbeil/choose) to rename current
focused space's label and persist latest labels to a local csv file
`$HOME/.yabai-labels.csv` which contains `(space index, label)` pairs.

One more step is to load these space labels on the startup of yabai:
add `restore-space-labels.fish` to your `.yabairc` configuration like this

```bash
# restore space labels
/path/to/yabai-spaces/restore-space-labels.fish
```

#### About rename space label

<img width="829" alt="image" src="https://user-images.githubusercontent.com/36144635/204808747-2e0c84c8-d33b-420b-9ab8-ac88f4fc4242.png">

In `choose`, you get a default '»' in the selection list. This selection item represents
clearing the space label. Press `Enter` to choose a selection item in `choose`.

Type any new label you want in `choose` and press `Enter`, and you'll get your
space label renamed.

If you want to cancel renaming space in `choose`, use `Esc`.

### Display skhd mode

Since skhd command-line does not provide methods to get current skhd mode, we need
to store it to somewhere which I choose a temp file `/tmp/skhd_mode`.

Executing [`skhd-mode.py`](./skhd-mode.py) with no arguments will print currently
saved skhd mode. Execute it with arguments to save the argument string
as new skhd mode. You can put this script in your shell `PATH`.

What's more, in skhd config, [`skhd-mode.py`](./skhd-mode.py) with mode name as
argument should be executed when skhd enters a mode.

For example, when entering `default` mode, execute `skhd-mode.py`(assuming
it's in shell `PATH`) with mode
name and then refresh yabai swiftbar plugin.
```
:: default : skhd-mode.py default; open -gj 'swiftbar://refreshplugin?name=yabai'
```

[`yabai.1d.py`](./yabai.1d.py) uses this script to get current skhd mode and
displays it.

<img width="503" alt="image" src="https://user-images.githubusercontent.com/36144635/204805131-22364c41-0084-4c6e-b32e-7fb80420aa7e.png">

If `skhd-mode.py` is not in your shell `PATH`, you should not only change the
script path in skhd config above, but also set the variable
`YABAI_SPACES_PATH` in `yabai.1d.py`.

## Herdr Agents in menu bar

[`herdr-agents.10s.py`](./herdr-agents.10s.py) is a standalone Python 3 SwiftBar
plugin. It queries `herdr api snapshot` every **10 seconds** and displays
`Herdr ▶ 3 ✓ 4` (running / completed agent counts). Yabai is not required.

Click the menu-bar item to see the **进行中** and **已完成** lists. Each entry
shows the **workspace name**, **tab name** and **pane ID**, for example:

```text
Workspace: my-project · Tab: 开发 · Pane: w1:p2
```

Hover an entry for its agent type and terminal/session title. Tab names come
from Herdr tab labels, not terminal titles. An **立即刷新** menu item refreshes
the data manually.

### Install

The local SwiftBar plugin directory is `~/scripts/swiftbar/`. From this repo:

```bash
chmod +x herdr-agents.10s.py
ln -s "$PWD/herdr-agents.10s.py" "$HOME/scripts/swiftbar/herdr-agents.10s.py"
open -gj 'swiftbar://refreshall'
```

The symlink keeps SwiftBar using the source in this project. The plugin needs
Python 3 and a running local Herdr server with `api snapshot` support (verified
with Herdr 0.9.3). It inherits `HERDR_SOCKET_PATH` when set; otherwise Herdr uses
its default socket. Only the selected/default Herdr session is counted, not
all named sessions or remote machines.

For GUI environments with a minimal `PATH`, the plugin searches common Nix,
Homebrew and `~/.local/bin` locations for Herdr. Set `HERDR_BIN_PATH` in the
SwiftBar environment to override the executable. Python 3 must also be
available on SwiftBar's `PATH` for the `/usr/bin/env python3` shebang.

### State semantics

- **运行中**: `working`.
- **已完成**: only `done`. `idle` is never counted as completed, even if it
  has a positive `completion_seq`.
- **其他状态**: `idle`, `blocked`, `unknown` or future statuses; shown
  separately so they are not silently omitted or counted as completed.

“Completed” means the current turn ended, **not** that the task passed
verification or the process exited. This is a live view of detected agent
panes: closed panes disappear, and past completions are not stored or counted
as cumulative history. Plain shell panes are excluded. An unavailable server,
missing binary, timeout or invalid response shows `Herdr ⚠` rather than
misleading zero counts. The plugin only reads Herdr state and never sends
prompts or changes agents, tabs or workspaces.

### When the Herdr server is not running

The menu-bar item displays **`Herdr ⚠`**. Opening it shows:

```text
无法连接 Herdr；请检查服务或 HERDR_SOCKET_PATH
立即刷新
```

This is a handled connection failure: the plugin exits successfully (code 0),
without a Python traceback, and does not display misleading zero counts.
Queries time out after 3 seconds. SwiftBar retries on the next **10-second**
refresh, or you can choose **立即刷新** after starting Herdr. The plugin does
not start the Herdr server itself.

To check this behavior without stopping your running server, point one
invocation at a nonexistent socket:

```bash
HERDR_SOCKET_PATH="/tmp/herdr-swiftbar-missing-$$.sock" python3 herdr-agents.10s.py
```

Python 3 itself must still be available: a missing interpreter prevents the
plugin from starting and cannot be handled by its error menu.

### Tests

```bash
python3 -B -m unittest discover -s tests -v
```

## Changelog

- v0.1
  - Add skhd mode display and related scripts
  - Replace Fish shell scripts with Python scripts
  - Update requirements and add some screenshots in README
