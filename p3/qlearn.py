import random
import pickle
import pandas as pd

import p3.pad
from p3.state import ActionState


class QLearn(object):
    def __init__(self, actions, epsilon=0.2, alpha=0.2, gamma=0.75, player=3):
        self.q = {}

        print("Loading P%i Q table..." % player)
        with open("p3/data/qtable%i.p" % player, "rb") as f:
            try:
                self.q = pickle.load(f)
            except:
                self.q = {}

        self.actions = actions
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def choose_action(self, state):
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            q = [self.getQ(state, a) for a in self.actions]
            if not q:
                print(self.actions)
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)
            action = self.actions[i]
        return action

    def getQ(self, state, action):
        return self.q.get((state, action), 0.0)

    def learnQ(self, state, action, reward, value):
        oldv = self.q.get((state, action), None)
        if oldv:
            # print ("Update")
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)
        else:
            # print ("New")
            self.q[(state, action)] = reward


    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.getQ(state2, a) for a in self.actions])
        self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)
