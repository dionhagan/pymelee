import os
import time
import pickle
import json
import numpy as np
import pandas as pd

import p3.falco
import p3.memory_watcher
import p3.menu_manager
import p3.pad
from p3.pad import Pad
import p3.state
import p3.state_manager
import p3.stats


def find_dolphin_dir():
    """Attempts to find the dolphin user directory. None on failure."""
    candidates = ['~/Library/Application Support/Dolphin']
    for candidate in candidates:
        path = os.path.expanduser(candidate)
        if os.path.isdir(path):
            return path
    return None

def write_locations(dolphin_dir, locations):
    """Writes out the locations list to the appropriate place under dolphin_dir."""
    path = dolphin_dir + '/MemoryWatcher/Locations.txt'
    with open(path, 'w') as f:
        f.write('\n'.join(locations))

        dolphin_dir = find_dolphin_dir()
        if dolphin_dir is None:
            print('Could not detect dolphin directory.')
            return

def run(falco, state, sm, mw, pad, stats):
    mm = p3.menu_manager.MenuManager()
    while True:
        last_frame = state.frame
        res = next(mw)
        if res is not None:
            sm.handle(*res)
        if state.frame > last_frame:
            stats.add_frames(state.frame - last_frame)
            start = time.time()
            make_action(state, pad, mm, falco)
            stats.add_thinking_time(time.time() - start)

def make_action(state, pad, mm, falco):
    if state.menu == p3.state.Menu.Game:
        # pad.release_button(p3.pad.Pad.START)
        falco.advance(state)
    elif state.menu == p3.state.Menu.Characters:
        mm.pick_falco(state, pad)
    elif state.menu == p3.state.Menu.Stages:
        # Handle this once we know where the cursor position is in memory.
        pad.tilt_stick(p3.pad.Stick.C, 0.5, 0.5)
        mm.pick_fd(state, pad)
    elif state.menu == p3.state.Menu.PostGame:
        mm.press_start_lots(state, pad)
        # pad.press_button(p3.pad.Pad.START)

def main():
    dolphin_dir = find_dolphin_dir()
    if dolphin_dir is None:
        print('Could not find dolphin config dir.')
        return

    # initialize memory managersdol
    state = p3.state.State()
    sm = p3.state_manager.StateManager(state)
    write_locations(dolphin_dir, sm.locations())
    stats = p3.stats.Stats()

    try:
        # open Dolphin via CLI - comment out system call and add your own directory
        print('Starting dolphin now. Press ^C to stop p3.')
        os.system("open /Volumes/Seagate\ Backup\ Plus\ Drive/Games/Super\ Smash\ Bros.\ Melee\ \(v1.02\).iso -a ~/Desktop/Dolphin.app/")#% sys.argv[1])

        # configure paths
        pad_path = dolphin_dir + '/Pipes/pipe'
        mw_path = dolphin_dir + '/MemoryWatcher/MemoryWatcher'
        with p3.pad.Pad(pad_path) as pad, p3.memory_watcher.MemoryWatcher(mw_path) as mw:
            falco = p3.falco.Falco(pad)
            run(falco, state, sm, mw, pad, stats)
    except KeyboardInterrupt:
        # executed on Ctrl-C
        print ('\n')
    finally:
        print('Saving Q-table...')
        with open("qtable.p", "wb") as f:
            print("Q Table Size: %i" % len(falco.ai.q))
            pickle.dump(falco.ai.q, f)

        # final code to be executed before program exits
        os.system("osascript -e 'quit app \"Dolphin\"'")
        print('Stopped')
        print(stats)
        print('\n')

if __name__ == '__main__':
    main()
