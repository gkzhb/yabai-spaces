#!/usr/bin/env python3
import os
import sys

# temp file path to store skhd mode
skhd_mode_path = '/tmp/skhd_mode'

if len(sys.argv) < 2:
    # if there is no arguments, print current skhd mode
    if os.path.isfile(skhd_mode_path):
        with open(skhd_mode_path, 'r') as f:
            print(f.readline())
    else:
        print('')
    exit(0)

# calculate new skhd mode
new_mode_str = ' '.join(sys.argv[1:])
with open(skhd_mode_path, 'w') as f:
    # write to temp file
    f.write(new_mode_str)
