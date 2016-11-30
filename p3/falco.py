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

        # convert class methods to serializable strings
        self.action_string = {
            'press_button': self.pad.press_button,
            'release_button': self.pad.release_button,
            'press_trigger': self.pad.press_trigger,
            'tilt_stick': self.pad.tilt_stick,
            'reset': self.pad.reset
        }

        self.last_frame = 0
        self.last_state = None
        self.last_action = None
        self.ai = p3.qlearn.QLearn(actions=[], epsilon=0.75, alpha=0.1)

    def generate_actions(self):
        """
            Creates a basic set of actions to sample from
            called at start of new game or when action_list runs out
        """
        actions = set()

        # native input functions (used to pipe instructions)
        actions.add((0, 'reset', None))
        inputs = ['press_button', 'press_trigger', 'tilt_stick']

        # optimization: use tool like itertools.permutations
        # should be 40 x framewait many options
        for _ in range(10000):
            action = random.choice(inputs)
            frame_wait = random.randint(0, 1)
            frame_wait = np.random.poisson(7, 1)[0]

            if action == 'press_button':
                button = p3.pad.Button(random.randint(0, 10))
                actions.add((frame_wait, action, tuple([button])))
                actions.add((0, 'release_button', tuple([button])))

            if action == 'press_trigger':
                trigger = p3.pad.Trigger(random.randint(0, 1))
                pressures = [0, 0.5, 1]
                pressure = random.choice(pressures)
                actions.add((frame_wait, action, tuple([trigger, pressure])))
                actions.add((0, action, tuple([trigger, 0])))

            if action == 'tilt_stick':
                stick = p3.pad.Stick(random.randint(0, 1))
                directions = [1.0, 0.0, 0.5]
                x = random.choice(directions)
                y = random.choice(directions)
                actions.add((frame_wait, action, tuple([stick, x, y])))

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

            # dam3, stock3 = self.reward_state(self.last_state, player=3)
            # dam1, stock1 = self.reward_state(self.last_state, player=1)
            #
            # p3_damage, p3_stocks = p3_damage - dam3, stock3 - p3_stocks
            # p1_damage, p1_stocks = p1_damage - dam1, stock1 - p1_stocks
        else:
            p3_damage, p3_stocks = 0, 4
            p1_damage, p1_stocks = 0, 4

        # print (p3_damage, p3_death)

        # reward for percentage
        reward -= 0.5 * p3_damage + 2 * p1_stocks
        reward += 0.75 * p1_damage + 4 * p3_stocks

        # penalty for p3_death
        if state.players[2].action_state.value <= 0xA:
            print("Dying!")
            reward += -1

        # reward for a kill
        if state.players[0].action_state.value <= 0xA:
            print("Killing!")
            reward += 1

        print(reward)

        # update Q vals
        if self.last_state:
            self.ai.learn(self.last_state, self.last_action, reward, state)

        # choose next action
        action = self.ai.choose_action(state)
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
