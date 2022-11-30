#!/usr/bin/env python3
import subprocess
import csv
import os
import json
import tempfile

# separator for different display monitor
DISPLAY_SEP = ' '
# customize font displayed in menu bar
CUSTOM_FONT = 'FiraCode Nerd Font'

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
    windows = json.loads(get_cmd_output(['yabai', '-m', 'query', '--windows'], 'get yabai windows'))
    sticky_window_ids = [item['id'] for item in windows if item['is-sticky'] == True]
    for item in spaces:
        if item['is-visible'] == True or len(item['label']) > 0:
            # space matches one of these conditions:
            # - space is visible
            # - space has label
            ret.append(item)
        else:
            non_sticky_window_ids = [window for window in item['windows'] if sticky_window_ids.count(window) == 0]
            if len(non_sticky_window_ids) > 0:
            # there are non sticky windows in space
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
        ret = f'{item[1]}({item[0]})'
    else:
        ret = str(item[0])
    if item[3] == True:
        if display == item[2]:
            ret = f'{ret}'
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

skhd_mode = get_cmd_output([f'{os.environ.get("HOME")}/scripts/yabai/skhd_mode.fish'], 'get skhd mode').decode('utf-8').strip()
if skhd_mode != 'default':
    str = skhd_mode + str

strs = [str, '---', 'yabai spaces & skhd mode']

for item in strs:
    print(item)
