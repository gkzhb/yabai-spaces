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
    shell printing color
    '''
    return f'\033[{color_number}m'

def get_cmd_output_and_returncode(cmd):
    '''
    run shell command and return stdout and command's return code
    '''
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return (result.returncode, result.stdout)

def get_cmd_output(cmd, cmd_desc):
    '''
    check shell command runs successfully
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
        if (item['is-visible'] == True or len(item['label']) > 0 or len(item['windows']) > 0):
            ret.append(item)
    return ret

def get_space_display_string(item: tuple[int, str, int, bool], display: int) -> str:
    '''
    format spaces displayed in menu bar
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