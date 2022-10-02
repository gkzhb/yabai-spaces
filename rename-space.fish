#!/usr/bin/env fish
# set label for current space
set YABAI_LABEL_PATH "$HOME/.yabai-labels.csv"
function rename_space
  if test -z "$argv"
    # no action
    return
  end
  if test "$argv" = '»'
    # clear space label
    yabai -m space --label ''
  else
    # avoid double quotes in new label, since they will casuse yabai output invalid JSON
    set new_label (string replace -a \" \' $argv)
    # set new label
    yabai -m space --label "$new_label"
  end
  # persist the space label info
  set csv_content (yabai -m query --spaces | jq -r '.[] | select(.label | length > 0) | [.index, .label] | @csv' | string split0)
  echo $csv_content > $YABAI_LABEL_PATH
  # update swiftbar state
  open -gj 'swiftbar://refreshplugin?name=yabai'
end
rename_space (echo '»' | choose -m)
