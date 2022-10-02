#!/usr/bin/env fish
set YABAI_LABEL_PATH "$HOME/.yabai-labels.csv"
if test -e "$YABAI_LABEL_PATH"
  set LABELS (cat $YABAI_LABEL_PATH)
  set label_list (string split \n $LABELS)
  for label_item in $label_list
    if test -n $label_item
      set label_kv (string split , $label_item)
      set index $label_kv[1]
      set label (string sub -s 2 -e -1 $label_kv[2]) # remove double quotes around label
      yabai -m space $index --label $label
    end
  end
end
