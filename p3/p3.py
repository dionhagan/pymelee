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


def run(cpu, state, sm, mw, pad, stats):
    mm = p3.menu_manager.MenuManager()
    while True:
        last_frame = state.frame
        res = next(mw)
        if res is not None:
            sm.handle(*res)
        if state.frame > last_frame:
            stats.add_frames(state.frame - last_frame)
            start = time.time()
            make_action(state, pad, mm, cpu)
            stats.add_thinking_time(time.time() - start)


def make_action(state, pad, mm, cpu):
    if state.menu == p3.state.Menu.Game:
        # pad.release_button(p3.pad.Pad.START)
        cpu.advance(state)
    elif state.menu == p3.state.Menu.Characters:
        mm.pick_cpu(state, pad)
    elif state.menu == p3.state.Menu.Stages:
        # Handle this once we know where the cursor position is in memory.
        pad.tilt_stick(p3.pad.Stick.C, 0.5, 0.5)
        mm.pick_fd(state, pad)
    elif state.menu == p3.state.Menu.PostGame:
        cpu.pad.reset()
        mm.press_start_lots(state, pad)


def main():
    dolphin_dir = find_dolphin_dir()
    if dolphin_dir is None:
        print('Could not find dolphin config dir.')
        return

    # initialize memory managers
    state = p3.state.State()
    sm = p3.state_manager.StateManager(state)
    write_locations(dolphin_dir, sm.locations())
    stats = p3.stats.Stats()

    try:
        # open Dolphin via CLI - comment out system call and add your own
        # directory
        print('Starting dolphin now. Press ^C to stop p3.')
        # % sys.argv[1])
        os.system("open /Volumes/Seagate\ Backup\ Plus\ Drive/Games/Super\ Smash\ Bros.\ Melee\ \(v1.02\).iso -a ~/Desktop/Dolphin.app/")
        # os.system("open ~/Downloads/Super\ Smash\ Bros.\ Melee\ \(v1.02\).iso
        # -a /Applications/Dolphin.app/")#% sys.argv[1])

        # configure paths
        # p2_pad_path = dolphin_dir + '/Pipes/pipe2'
        p3_pad_path = dolphin_dir + '/Pipes/pipe'
        mw_path = dolphin_dir + '/MemoryWatcher/MemoryWatcher'
        # with p3.pad.Pad(p2_pad_path) as pad2,
        with p3.pad.Pad(p3_pad_path) as pad3, p3.memory_watcher.MemoryWatcher(mw_path) as mw:
            # initialize CPUs
            # falcon2 = p3.falco.Falco(pad2, player=2, enemy=3)
            cpu3 = p3.falco.Falco(pad3, epsilon=0.5, player=3, enemy=1)

            # start both CPUs
            # run(falcon2, state, sm, mw, pad2, stats)
            run(cpu3, state, sm, mw, pad3, stats)

    except KeyboardInterrupt:
        # executed on Ctrl-C
        print ("CTRL-C")
    finally:
        print('Saving Q-tables...')
        # with open("p3/data/qtable2.p", "wb") as f2,
        with open("p3/data/qtable3.p", "wb") as f3:
            # print("P1 Q-Table Size: %i" % len(falcon2.ai.q))
            # pickle.dump(falcon2.ai.q, f2)
            print("P3 Q-Table Size: %i" % len(cpu3.ai.q))
            pickle.dump(cpu3.ai.q, f3)

        # final code to be executed before program exits
        os.system("osascript -e 'quit app \"Dolphin\"'")
        print('Stopped')
        print(stats)
        print('\n')

if __name__ == '__main__':
    main()
