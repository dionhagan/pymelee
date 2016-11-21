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
        actions.add(pad.reset)
        inputs = [pad.press_button, pad.release_button, pad.press_trigger,
                  pad.tilt_stick, pad.reset]

        # populate set of 50,000 possible actions
        while len(actions) < 50000:
            for _ in range(50000):
                action = random.choice(inputs)
                print(action)
                frame_wait = random.randint(0, 5)

                if action == pad.press_button or action == pad.release_button:
                    button = p3.pad.Button(random.randint(0, 10))
                    actions.add((frame_wait, action, tuple([button])))

                if action == pad.press_trigger:
                    trigger = p3.pad.Trigger(random.randint(0, 1))
                    pressure = random.uniform(0, 1)
                    actions.add((frame_wait, action, tuple([trigger, pressure])))
                    actions.add((0, action, tuple([trigger, 0])))

                if action == pad.tilt_stick:
                    stick = p3.pad.Stick(random.randint(0, 1))
                    directions = [1.0, 0.0, 0.5]
                    # x = random.choice(directions)
                    # y = random.choice(directions)
                    x = directions[random.randint(0, 2)]
                    y = directions[random.randint(0, 2)]
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
        damage_taken, death = self.getAttrs(state, player=3)
        damage_dealt, kill = self.getAttrs(state, player=1)
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
            wait, func, args = self.action_list.pop(0)

            if state.frame - self.last_frame < wait:
                return

            if func is not None:
                func(*args)
            self.last_frame = state.frame

            # update Q vals and add next action
            self.update(state)
        else:
            if not self.ai.actions:
                self.ai.actions = self.generate_actions(pad)
            self.update(state)

    # extracts
    def getAttrs(self, state, player=3):
        return (state.players[player - 1].percent, state.players[player - 1].stocks)
