import pdb

import random
import p3.qlearn

import p3.pad
from p3.state import ActionState

class Fox:
    def __init__(self):
        self.action_list = []

        self.last_frame = 0
        self.last_state = None
        self.last_action = None
        self.ai = p3.qlearn.QLearn(actions=[], epsilon=0.75, alpha=0.2)

    def generate_actions(self, pad):
        actions = set()
        actions.add(pad.reset)
        inputs = [pad.press_button, pad.release_button, pad.press_trigger,
                  pad.tilt_stick, pad.reset]

        # populate set of possible actions
        while len(actions) < 50000:
            for i in range(50000):
                action = random.choice(inputs)
                frame_wait = random.randint(0, 5)
                
                if action == pad.press_button or action == pad.release_button:
                    button = p3.pad.Button(random.randint(0, 10))
                    actions.add((frame_wait, action, tuple([button])))

                if action == pad.press_trigger:
                    trigger = p3.pad.Trigger(random.randint(0, 1))
                    pressure = random.uniform(0, 1)
                    actions.add((frame_wait, action, tuple([trigger, pressure])))

                if action == pad.tilt_stick:
                    stick = p3.pad.Stick(random.randint(0, 1))
                    x = random.uniform(0, 1)
                    y = random.uniform(0, 1)
                    actions.add((frame_wait, action, tuple([stick, x, y])))

            print(len(actions))
        print(actions)
        return list(actions)

    def update(self, state):
        damage_taken, death = self.getAttrs(state)
        damage_dealt, kill = self.getAttrs(state, 1)
        reward = -1

        def isDying(state):
            return state.players[2].action_state <= 0xA

        # penalty for death
        if isDying:
            reward += -100
            if self.last_state:
                self.ai.learn(self.last_state, self.last_action, reward, state)
            if death:
                self.last_state = None

        # reward for a kill
        if kill == 1:
            reward += 100

        # reward for percentage
        reward -= damage_taken
        reward += damage_dealt

        # update Q vals
        if self.last_state:
            self.ai.learn(self.last_state, self.last_action, reward, state)

        action = self.ai.choose_action(state)
        self.action_list.append(action)

        self.last_state = state
        self.last_action = action


    def advance(self, state, pad):
        while self.action_list:
            if not self.ai.actions:
                self.ai.actions = self.generate_actions(pad)
            
            wait, func, args = self.action_list[0]
            if state.frame - self.last_frame < wait:
                return
            self.action_list.pop(0)
            if func is not None:
                func(*args)
            self.last_frame = state.frame

            # update Q vals and add next action
            self.update(state)
        else:
            if not self.ai.actions:
                self.ai.actions = self.generate_actions(pad)
            self.update(state)

    def getAttrs(self, state, player=3):
        return (state.players[player - 1].percent, state.players[player - 1].stocks)
