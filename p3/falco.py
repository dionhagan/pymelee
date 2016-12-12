import pdb
import pickle
import random
import numpy as np
import pandas as pd

import p3.qlearn
import p3.pad
from p3.state import ActionState

class Falco:
    def __init__(self, pad, epsilon=0.75, player=3, enemy=1):
        self.player = player - 1
        self.enemy = enemy - 1

        self.pad = pad
        self.last_frame = 0
        self.action_list = []
        self.last_state = None
        self.last_action = None
        self.ai = p3.qlearn.QLearn(actions=[], epsilon=epsilon, alpha=0.5,
                                               gamma=0.9, player=player)

        # convert native commands to serializable strings
        self.action_string = {
            'press_button': self.pad.press_button,
            'release_button': self.pad.release_button,
            'press_trigger': self.pad.press_trigger,
            'tilt_stick': self.pad.tilt_stick,
            'reset': self.pad.reset
        }

        # convert native commands to serializable strings
        self.move_string = {
            # WORKING
            'stop': self.stop,
            'shield': self.shield,
            'light_shield': self.light_shield,

            'pressZ': self.pressZ,

            'neutralB': self.neutralB,'downB': self.downB,'upB': self.upB,
            'sideB_left': self.sideB_left, 'sideB_right': self.sideB_right,

            'nair': self.nair, 'dair': self.dair, 'fair': self.fair, 'bair': self.bair,

            # NOT WORKING
            # 'pressA': self.pressA, 'pressB': self.pressB, 'pressX': self.pressX,
            'fsmash_left': self.fsmash_left, 'fsmash_right': self.fsmash_right,
            'up_smash': self.up_smash, 'down_smash': self.down_smash,
            # 'wavedash': self.wavedash,
        }

    def generate_actions(self):
        """
            Creates a basic set of actions to sample from
            called at start of new game or when action_list runs out
        """
        actions = set()
        actions.add((0, 'reset', None))

        # native input functions (used to pipe instructions)
        # inputs = list()
        inputs = ['tilt_stick', 'press_button']#, 'press_trigger']
        inputs.extend(list(self.move_string.keys()))

        for _ in range(300):
            action = random.choice(inputs)
            frame_wait = np.random.poisson(8, 1)[0]

            if action == 'tilt_stick':
                # stick = p3.pad.Stick(random.randint(0, 1))
                stick = p3.pad.Stick.MAIN
                directions = [0.0, 0.5, 1.0]
                x = random.choice(directions)
                y = random.choice(directions)
                actions.add((frame_wait, action, tuple([stick, x, y])))

            # Currently inactive
            elif action == 'press_button':
                button = p3.pad.Button(random.randint(0, 10))
                actions.add((frame_wait, action, tuple([button])))
                actions.add((frame_wait, 'release_button', tuple([button])))

            elif action == 'press_trigger':
                trigger = p3.pad.Trigger(random.randint(0, 1))
                pressures = [0, 0.5, 1]
                pressure = random.choice(pressures)
                actions.add((frame_wait, action, tuple([trigger, pressure])))

            else:
                actions.add(action)


        # print(len(actions))
        return list(actions)

    def update(self, state):
        """
            Calculate reward for current state and action,
            and update Q-table
        """
        # set current
        state.players[0].type = 0

        reward = -1

        # extract damage/stock state for p1 and p3
        if self.last_state:
            p3_damage, p3_stocks = self.reward_state(state, player=self.player)
            p1_damage, p1_stocks = self.reward_state(state, player=self.enemy)
        else:
            p3_damage, p3_stocks = 0, 4
            p1_damage, p1_stocks = 0, 4

        # print (p3_damage, p3_death)

        # reward for percentage
        reward -= 5 * p3_damage # + 1 * p1_stocks
        reward += 500 * p1_damage # + 1 * p3_stocks

        # get players action states
        p3_action_state = state.players[self.player].action_state.value
        p1_action_state = state.players[self.enemy].action_state.value

        # penalty for p3_death
        if state.players[self.player].action_state.value <= 0xA:
            print("NOoO0o0oO0O!")
            reward += -10000

        # reward for a kill
        if state.players[self.enemy].action_state.value <= 0xA:
            print("REKT")
            reward += 100

        # reward for attacking
        if p3_action_state >= 0x2C and p3_action_state <= 0x45:
            print('Attacking!')
            reward += 500

        # punish for falling/dying
        if p3_action_state >= 0x1D and p3_action_state <= 0x26:
            print('Falling!')
            reward -= 5000

        # punish for being below stage
        if state.players[self.player].pos_y < 0:
            print('BELOW')
            reward -= 100 * abs(state.players[self.player].pos_y)

        # reward for being on the grounded
        if state.players[self.player].on_ground:
            print ("GROUNDED")
            reward += 1000

        # reward for being center stage
        # print ('X-Coord: %i' % state.players[self.player-2].pos_x)
        reward -= abs(state.players[self.player].pos_x)
        print(reward)

        # update Q vals
        if self.last_state:
            self.ai.learn(self.last_state, self.last_action, reward, state)

        # choose next action
        action = self.ai.choose_action(state)
        print(action)
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

            # print (state.frame, self.last_frame)

            # stop actions until frame wait is over
            if state.frame - self.last_frame < wait:
                return

            # pop off first action if wait is over
            self.action_list.pop(0)

            if func:
                # print(wait, func, args)
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
    def reward_state(self, state, player):
        damage = state.players[self.player].percent
        stocks = state.players[self.player].stocks
        return (damage, stocks)


    """
        P3 MOVESET
    """

    # FUNDAMENTALS
    def stop(self, wait=7):
        # self.action_list.append((0, pad.reset, []))
        self.action_list.append((wait, 'reset', None))

    def shield(self, wait=240):
        self.action_list.append((wait, 'press_trigger', [p3.pad.Trigger.L, 1]))
        self.action_list.append((5, 'press_trigger', [p3.pad.Trigger.L, 0]))

    def light_shield(self, wait=30):
        self.action_list.append((wait, 'press_trigger', [p3.pad.Trigger.L, 0.5]))
        self.action_list.append((0, 'press_trigger', [p3.pad.Trigger.L, 0]))

    def pressZ(self):
        self.action_list.append((0, 'press_button', [p3.pad.Button.Z]))
        self.action_list.append((0, 'release_button', [p3.pad.Button.Z]))

    def pressA(self, x=0.5, y=0.5):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, x, y]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
        self.action_list.append((random.uniform(1, 60), 'release_button', [p3.pad.Button.A]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def pressB(self, x=0.5, y=0.5):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, x, y]))
        # self.action_list.append((random.uniform(1, 12), 'press_button', [p3.pad.Button.B]))
        self.action_list.append((6, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((0, 'release_button', [p3.pad.Button.B]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def pressX(self):
        self.action_list.append((2, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((0, 'release_button', [p3.pad.Button.X]))

    # MOVEMENT
    def shorthop(self):
        self.action_list.append((2, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((0, 'release_button', [p3.pad.Button.X]))

    def fullhop(self):
        self.action_list.append((3, 'press_button', [p3.pad.Button.X]))
        self.action_list.append((0, 'release_button', [p3.pad.Button.X]))

    def double_jump(self):
        self.fullhop(); self.fullhop()

    def dash(self, x, wait=240):
        self.action_list.append((wait, 'tilt_stick', [p3.pad.Stick.MAIN, x, 0.5]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def dash_left(self):
        self.dash(x=0)

    def dash_right(self):
        self.dash(x=1)

    # SPECIALS
    def neutralB(self):
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.B]))
        self.stop(30)

    def upB(self):
        self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((10, 'release_button', [p3.pad.Button.B]))

    def sideB_left(self):
        self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.0, 0.5]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((10, 'release_button', [p3.pad.Button.B]))

    def sideB_right(self):
        self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 1.0, 0.5]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((10, 'release_button', [p3.pad.Button.B]))

    def downB(self):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.0]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.B]))
        self.action_list.append((1, 'release_button', [p3.pad.Button.B]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    # SMASH ATTACKS
    def fsmash(self, x):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.C, x, 0.5]))
        self.action_list.append((7, 'tilt_stick', [p3.pad.Stick.C, 0.5, 0.5]))

    def fsmash_left(self):
        self.fsmash(x=0)

    def fsmash_right(self):
        self.fsmash(x=1)

    def up_smash(self):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.C, 0.5, 1]))
        self.action_list.append((1, 'tilt_stick', [p3.pad.Stick.C, 0.5, 0.5]))

    def down_smash(self):
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.C, 0, 0.5]))
        self.action_list.append((1, 'tilt_stick', [p3.pad.Stick.C, 0.5, 0.5]))

    # AERIALS
    def nair(self):
        self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
        self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.A]))

    def fair(self):
        if self.last_state:
            if self.last_state.players[2].facing == 1.0:
                self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
                self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
                self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
                self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 1.0, 0]))
                self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
            else:
                self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
                self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
                self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
                self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.0, 0]))
                self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def dair(self):
        self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
        self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
        self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
        self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def bair(self):
        if self.last_state:
            if self.last_state.players[2].facing == 1.0:
                self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
                self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
                self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
                self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 0.0, 0]))
                self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
            else:
                self.action_list.append((6, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 1.0]))
                self.action_list.append((5, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))
                self.action_list.append((0, 'press_button', [p3.pad.Button.A]))
                self.action_list.append((0, 'tilt_stick', [p3.pad.Stick.MAIN, 1.0, 0]))
                self.action_list.append((2, 'tilt_stick', [p3.pad.Stick.MAIN, 0.5, 0.5]))


    # TECH
    def lcancel(self):
        self.shield(wait=3)

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
