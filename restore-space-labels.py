#!/usr/bin/env python3
import os
import json
import subprocess

YABAI_LABEL_PATH = f'{os.environ.get("HOME")}/.yabai-labels.json'

if os.path.isfile(YABAI_LABEL_PATH):
    with open(YABAI_LABEL_PATH, 'r') as f:
        label_list = json.load(f)
        for label in label_list:
            subprocess.Popen(['yabai', '-m', 'space', str(label.get('index')), '--label', label.get('label')])
