import pdb
import pickle
import random
import numpy as np
import pandas as pd

import p3.qlearn
import p3.pad
from p3.state import ActionState

class Falco:
    def __init__(self, pad):
        self.pad = pad
        self.action_list = []

        # dict to convert class methods to serializable strings
        self.action_string = {
            'press_button': self.pad.press_button,
            'release_button': self.pad.release_button,
            'press_trigger': self.pad.press_trigger,
            'tilt_stick': self.pad.tilt_stick,
            'reset': self.pad.reset
        }
        self.move_string = {
            'stop': self.stop,
            'dash_left': self.dash_left,
            'dash_right': self.dash_right,
            'shorthop': self.shorthop,
            'shine': self.shine,
            'laser': self.laser,
            'nair': self.nair,
            'fair_left': self.fair_left,
            'fair_right': self.fair_left,
            'bair': self.bair,
            'dair': self.dair,
            'upB': self.upB,
            'shield': self.shield,
            'wavedash': self.wavedash,
            'shorthop_laser': self.shorthop_laser,
            'shinespam': self.shinespam
        }

        self.last_frame = 0
        self.last_state = None
        self.last_action = None
        self.ai = p3.qlearn.QLearn(actions=[], epsilon=0.95, alpha=0.33)

    def generate_actions(self):
        """
            Creates a basic set of actions to sample from
            called at start of new game or when action_list runs out
        """
        actions = set()

        # native input functions (used to pipe instructions)
        actions.add((0, 'reset', None))
        inputs = ['tilt_stick']
        inputs.extend(list(self.move_string.keys()))

        # optimization: use tool like itertools.permutations
        # should be 40 x framewait many options
        for _ in range(10000):
            action = random.choice(inputs)
            frame_wait = np.random.poisson(12, 1)[0]

            if action == 'press_button':
                button = p3.pad.Button(random.randint(0, 10))
                actions.add((frame_wait, action, tuple([button])))
                actions.add((frame_wait, 'release_button', tuple([button])))

            elif action == 'press_trigger':
                trigger = p3.pad.Trigger(random.randint(0, 1))
                pressures = [0, 0.5, 1]
                pressure = random.choice(pressures)
                actions.add((frame_wait, action, tuple([trigger, pressure])))

            elif action == 'tilt_stick':
                stick = p3.pad.Stick(random.randint(0, 1))
                directions = [1.0, 0.0, 0.5]
                x = random.choice(directions)
                y = random.choice(directions)
                actions.add((frame_wait, action, tuple([stick, x, y])))

            else:
                actions.add(action)


        print(len(actions))
        return list(actions)

    def update(self, state):
        """
            Calculate reward for current state and action,
            and update Q-table
        """
        reward = -1

        # extract damage/stock state for p1 and p3
        if self.last_state:
            # print (self.last_frame)
            # print(self.last_state == state)
            p3_damage, p3_stocks = self.reward_state(state, player=3)
            p1_damage, p1_stocks = self.reward_state(state, player=1)
        else:
            p3_damage, p3_stocks = 0, 4
            p1_damage, p1_stocks = 0, 4

        # print (p3_damage, p3_death)

        # reward for percentage
        reward -= 1 * p3_damage + 1 * p1_stocks
        reward += 5 * p1_damage + 1 * p3_stocks

        # penalty for p3_death
        if state.players[2].action_state.value <= 0xA:
            # print("Dying!")
            reward += -1

        # reward for a kill
        if state.players[0].action_state.value <= 0xA:
            # print("Killing!")
            reward += 1

        print(reward)

        # update Q vals
        if self.last_state:
            self.ai.learn(self.last_state, self.last_action, reward, state)

        # choose next action
        action = self.ai.choose_action(state)
        if action in self.move_string:
            func = self.move_string[action]
            func()
        else:
            self.action_list.append(action)

        # record last state-action pair
        self.last_state = state
        self.last_action = action


    def advance(self, state):
        while self.action_list and self.ai.actions:
            if not self.ai.actions:
                self.ai.actions = self.generate_actions(pad)

            # e.g. wait = 1; func = tilt_stick; args = {x: 0.5, y: 0.5}
            # peek at first action in stack
            wait, func, args = self.action_list[0]

            # stop actions until frame wait is over
            if state.frame - self.last_frame < wait:
                return

            # pop off first action if wait is over
            self.action_list.pop(0)

            if func:
                print(wait, func, args)
                # convert action string back to function
                f = self.action_string[func]
                if args:
                    f(*args)
                else:
                    f()
            self.last_frame = state.frame

            # update Q vals and add next action
            self.update(state)
        else:
            # generate possible actions if none
            self.ai.actions = self.generate_actions()
            self.update(state)

    # extracts
    def reward_state(self, state, player=3):
        # print(self.last_state.players[player - 1].percent - state.players[player - 1].percent)
        # damage = state.players[player - 1].percent - self.last_state.players[player - 1].percent
        # stocks = self.last_state.players[player - 1].stocks - state.players[player - 1].stocks
        damage = state.players[player - 1].percent
        stocks = state.players[player - 1].stocks
        return (damage, stocks)


    """
        Falco Moveset
    """

    # FUNDAMENTALS
    def stop(self, wait=10):
        # self.action_list.append((0, pad.reset, []))
        self.action_list.append((wait, 'reset', None))

    def pressA(self, x=0.5, y=0.5):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, x, y]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
        self.action_list.append((2, 'release_button', [p3.pad.Button.A]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def pressB(self, x=0.5, y=0.5):
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, y]))
        self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
        self.action_list.append((2, pad.release_button, [p3.pad.Button.B]))
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def pressX(self, pad):
        self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
        self.action_list.append((2, pad.release_button, [p3.pad.Button.X]))

    def shield(self, wait=30):
        self.action_list.append((wait, 'press_trigger', [p3.pad.Trigger.L, 1]))
        self.action_list.append((0, 'press_trigger', [p3.pad.Trigger.L, 0]))


    # MOVEMENT
    def jump(self, pad):
        self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
        self.action_list.append((3, pad.release_button, [p3.pad.Button.X]))

    def shorthop(self):
        self.action_list.append((2, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.X]))

    def double_jump(self, pad):
        self.jump()
        self.jump()

    def dash(self, x, wait=60):
        self.action_list.append((wait, 'tilt_stick', [p3.pad.Stick.MAIN, x, 0.5]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def dash_left(self):
        self.dash(x=0)

    def dash_right(self):
        self.dash(x=1)

    # SPECIALS
    def laser(self):
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.B]))
        self.stop(30)

    def upB(self, x=0.5, y=1.0):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, x, y]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((3, 'release_button', [p3.pad.Button.B]))

    def sideB(self, pad):
        pass

    def shine(self):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.0]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.B]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    # SMASH ATTACKS
    def fsmash(self, x):
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.C, x, 0.5]))
        self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.C, 0.5, 0.5]))

    def up_smash(self, pad):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.C, 0.5, 1]))
        self.action_list.append((1, 'tilt_stick', [p3.pad.Stick.C, 0.5, 0.5]))

    def down_smash(self, pad):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.C, 0, 0.5]))
        self.action_list.append((1, 'tilt_stick', [p3.pad.Stick.C, 0.5, 0.5]))

    # AERIALS
    def nair(self):
        self.shorthop()
        self.pressA()
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def fair_right(self):
        self.shorthop()
        self.pressA(x=1)
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def fair_left(self):
        self.shorthop()
        self.pressA(x=0)
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def dair(self):
        self.shorthop()
        self.pressA(y=0)
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def bair(self):
        self.shorthop()
        self.pressA(x=0)
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))


    # TECH
    def shinespam(self):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.0]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.B]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.X]))
        self.stop(5)

    def shorthop_laser(self):
        self.action_list.append((0, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((2, 'release_button', [p3.pad.Button.X]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
        self.laser()
        self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.stop()

    def wavedash(self):
        self.action_list.append((0, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.X]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0, 0]))
        self.action_list.append((2, 'press_trigger', [p3.pad.Trigger.L, 1]))
        self.action_list.append((2, 'reset', None))
