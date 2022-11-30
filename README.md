# Yabai Spaces

A swiftbar plugin displays yabai spaces, inspired by [SxC97/Yabai-Spaces](https://github.com/SxC97/Yabai-Spaces).

## Features

<img width="478" alt="image" src="https://user-images.githubusercontent.com/36144635/204783828-ccbcf4aa-b423-404e-a5a9-de6c8a3eb245.png">

- Display yabai spaces in Mac OS menu bar.
  - Separate spaces belonging to different monitors (two monitors in the above image, and spaces of them are separated by '>')
  - Highlight current space for each monitor and markup focused space (displayed spaces are in red, focused space is wrapped by '<<' '>>')
  - Show up yabai spaces' labels, and you can easily customize them with a
  simple script
    - If you want to customize how the space is displayed, you can edit `get_space_display_string` function in [`yabai.1d.py`](./yabai.1d.py) as you wish.

## Requirements

- Python 3
- Fish Shell, since I'm using fish shell (may be replaced by Python scripts in the future)
- [jq: Command-line JSON processor](https://github.com/stedolan/jq) (may not be required without Fish shell scripts in the future)
- [koekeishiya/yabai](https://github.com/koekeishiya/yabai)
- [SwiftBar](https://github.com/swiftbar/SwiftBar) or [xbar (the BitBar reboot)](https://github.com/matryer/xbar) (not tested for xbar)
- [chipsenkbeil/choose: Fuzzy matcher for OS X that uses both std{in,out} and a native GUI](https://github.com/chipsenkbeil/choose)

## Installation & Usage

### Yabai Spaces in menu bar

Copy [`yabai.1d.py`](./yabai.1d.py) to your SwiftBar/xbar plugin's directory.
If SwiftBar is running, you may see Yabai Spaces in your menu bar.
> If SwiftBar is running and you cannot see it, it might be there is no enough
space to display Yabai Spaces.

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

### Persist Yabai Space Labels

When you restart Yabai, all the labels of spaces will be reset. And here comes
the scripts to persist these data.

Executing [`a`](./rename-space.fish) (bind this script to a hotkey in skhd is
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

In `choose`, you get a default '»' in the selection list. This selection item represents
clearing the space label. Press `Enter` to choose a selection item in `choose`.

Type any new label you want in `choose` and press `Enter`, and you'll get your
space label renamed.

If you want to cancel renaming space in `choose`, use `Esc`.
