#!/usr/bin/env python3
# <bitbar.title>Yabai Spaces With Labels</bitbar.title>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>gkzhb</bitbar.author>
# <bitbar.author.github>gkzhb</bitbar.author.github>
# <bitbar.desc>Display yabai spaces and labels</bitbar.desc>
# <bitbar.image>https://user-images.githubusercontent.com/36144635/204783828-ccbcf4aa-b423-404e-a5a9-de6c8a3eb245.png</bitbar.image>
# <bitbar.dependencies>python3,choose</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/gkzhb/yabai-spaces</bitbar.abouturl>
import subprocess
import csv
import os
import json
import tempfile

# separator for different display monitor
DISPLAY_SEP = ' '
# customize font displayed in menu bar
CUSTOM_FONT = 'FiraCode Nerd Font'
# path to this git repo, if `skhd-mode.py` is in your shell PATH, you can leave this string empty
YABAI_SPACES_PATH = ''

class Color:
    red = 31
    white = 0

def make_color(color_number: int) -> str:
    '''
    set the color of printed text in terminal
    '''
    return f'\033[{color_number}m'

def get_cmd_output_and_returncode(cmd):
    '''
    run shell command and return its stdout and return code
    '''
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return (result.returncode, result.stdout)

def get_cmd_output(cmd, cmd_desc):
    '''
    run shell command and return its stdout

    additionally check whether shell command runs successfully
    if not, exit program
    '''
    result = get_cmd_output_and_returncode(cmd)
    if result[0] != 0:
        print(f'Error in {cmd_desc}')
        exit(1)
    return result[1]

def filter_visible_spaces(spaces: list[dict]):
    '''filter spaces that should be displayed in the menu bar'''
    ret = []
    for item in spaces:
        if item['is-visible'] == True:
            # space matches one of these conditions:
            # - space is visible
            ret.append(item)
    return ret

def get_space_display_string(item: tuple[int, str, int, bool], display: int) -> str:
    '''
    format spaces displayed in menu bar

    :param item: tuple contains [space index, label, monitor id, whether space is visible]
    :param display: currently focused monitor id
    '''
    ret = ''
    if item[1] and len(item[1]) > 0:
        # label is not empty
        ret = f'{item[1]}({item[0]})'
    else:
        # label is empty
        ret = str(item[0])
    if item[3] == True:
        # the space is displayed
        if display == item[2]:
            # the space is focused
            ret = make_color(colors.red) + ret + make_color(colors.white)
    return ret

def get_all_display_string(spaces: tuple[int, str, int, bool], focused_display: int) -> str:
    '''
    get all spaces' display string
    '''
    process_display = 0
    ret = ''
    for item in spaces:
        if process_display != item[2]:
            ret += DISPLAY_SEP
            process_display = item[2]
        ret += ' ' + get_space_display_string(item, focused_display)
    return ret

colors = Color()

# get all yabai spaces info
cmd_result = get_cmd_output(['yabai', '-m', 'query', '--spaces'], 'querying yabai spaces')
spaces = json.loads(cmd_result)

filtered_spaces = filter_visible_spaces(spaces)
# space related data that are used to persist spaces' label information
visible_spaces_data = [(item['index'], item['label'], item['display'], item['is-visible']) for item in filtered_spaces]

# get current display info
cmd_result = get_cmd_output(['yabai', '-m', 'query', '--displays', '--display'], 'querying current display')
focused_display = json.loads(cmd_result)['index']
str = get_all_display_string(visible_spaces_data, focused_display)
str += f'{DISPLAY_SEP} | font="{CUSTOM_FONT}" ansi=true'

# display skhd mode
skhd_mode = get_cmd_output([os.path.join(YABAI_SPACES_PATH, 'skhd-mode.py')], 'get skhd mode').decode('utf-8').strip()
if skhd_mode != 'default':
    str = skhd_mode + str

strs = [str, '---', 'yabai spaces & skhd mode']

for item in strs:
    print(item)
