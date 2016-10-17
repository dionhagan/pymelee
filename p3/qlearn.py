import random
import pickle

import p3.pad
from p3.state import ActionState

class QLearn(object):
    def __init__(self, actions, epsilon=0.2, alpha=0.2, gamma=0.9):
        self.q = {}
       
        # try:
        #     with open('fox.p', 'rb') as handle:
        #         self.q = pickle.load(handle)

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
        if oldv is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)

    def learn(self, state1, action1, reward, state2):
        maxqnew = max([self.getQ(state2, a) for a in self.actions])
        self.learnQ(state1, action1, reward, reward + self.gamma*maxqnew)
        # with open('fox.p', 'wb') as handle:
        #     self.q = pickle.dump(self.q, handle)
