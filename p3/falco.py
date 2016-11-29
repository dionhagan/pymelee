import pdb

import random
import p3.qlearn

import p3.pad
from p3.state import ActionState

class Falco:
    def __init__(self):
        self.action_list = []
        self.last_frame = 0
        self.last_state = None
        self.last_action = None
        self.ai = p3.qlearn.QLearn(actions=[], epsilon=0.75, alpha=0.1)

    def generate_actions(self, pad):
        """
            Creates a basic set of actions to sample from
            called at start of new game or when action_list runs out
        """
        actions = set()

        # native input functions (used to pipe instructions)
        actions.add((0, pad.reset, None))
        inputs = [pad.press_button, pad.press_trigger, pad.tilt_stick]

        # optimization: use tool like itertools.permutations
        # while len(actions) < 500:
        # should be 40 x framewait many options
        for _ in range(500):
            action = random.choice(inputs)
            frame_wait = random.randint(0, 5)

            if action == pad.press_button:
                button = p3.pad.Button(random.randint(0, 10))
                actions.add((frame_wait, action, tuple([button])))
                actions.add((0, pad.release_button, tuple([button])))

            if action == pad.press_trigger:
                trigger = p3.pad.Trigger(random.randint(0, 1))
                pressures = [0, 0.5, 1]
                pressure = random.choice(pressures)
                actions.add((frame_wait, action, tuple([trigger, pressure])))
                actions.add((0, action, tuple([trigger, 0])))

            if action == pad.tilt_stick:
                stick = p3.pad.Stick(random.randint(0, 1))
                directions = [1.0, 0.0, 0.5]
                x = random.choice(directions)
                y = random.choice(directions)
                actions.add((frame_wait, action, tuple([stick, x, y])))

            print(len(actions))
        print(actions)
        return list(actions)

    def update(self, state):
        """
            Calculate reward for current state and action,
            and update Q-table
        """

        # extract damage/stock state for p1 and p3
        damage_taken, death = self.reward_state(state, player=3)
        damage_dealt, kill = self.reward_state(state, player=1)
        reward = -1

        # penalty for death
        if state.players[2].action_state.value <= 0xA:
            print("Dying!")
            reward += -1
            if self.last_state:
                self.ai.learn(self.last_state, self.last_action, reward, state)
            if death:
                self.last_state = None

        # reward for a kill
        if state.players[0].action_state.value <= 0xA:
            print("Killing!")
            reward += 1
            if self.last_state:
                self.ai.learn(self.last_state, self.last_action, reward, state)

        # reward for percentage
        reward -= 0.1 * damage_taken
        reward += 0.1 * damage_dealt

        # print(reward)

        # update Q vals
        if self.last_state:
            self.ai.learn(self.last_state, self.last_action, reward, state)

        # choose next action
        action = self.ai.choose_action(state)
        self.action_list.append(action)

        # record last state-action pair
        self.last_state = state
        self.last_action = action


    def advance(self, state, pad):
        while self.action_list:

            # print(state.frame)

            # generate possible actions if none
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

            if func and args:
                func(*args)
            elif func:
                func()
            self.last_frame = state.frame

            # update Q vals and add next action
            self.update(state)
        else:
            if not self.ai.actions:
                self.ai.actions = self.generate_actions(pad)
            self.update(state)

    # extracts
    def reward_state(self, state, player=3):
        return (state.players[player - 1].percent, state.players[player - 1].stocks)
