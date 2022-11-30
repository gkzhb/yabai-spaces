#!/usr/bin/env python3
import subprocess
import io
import os
import json

YABAI_LABEL_PATH = os.path.join(os.environ.get('HOME'), '.yabai-labels.json')

default_placeholder = '»'

def rename_space(label: str):
    if not len(label):
        return
    if label == default_placeholder:
        # clear space label
        subprocess.run(['yabai', '-m', 'space', '--label', ''])
    else:
        # avoid double quotes in new label, since they will cause yabai output invalid JSON string
        label = label.replace('"', "'")
        subprocess.run(['yabai', '-m', 'space', '--label', label])
    # persist the space label info
    spaces_json = subprocess.check_output(['yabai', '-m', 'query', '--spaces'])
    spaces = json.loads(spaces_json)
    labeled_spaces = [{ 'index': item.get('index'), 'label': item.get('label')} for item in spaces if item.get('label') and len(item.get('label'))]
    with open(YABAI_LABEL_PATH, 'w') as f:
        json.dump(labeled_spaces, f)

echo = subprocess.Popen(('echo', default_placeholder), stdout=subprocess.PIPE)
new_label = subprocess.check_output(('choose', '-m'), stdin=echo.stdout).decode('utf-8').strip()
echo.wait()

rename_space(new_label)
