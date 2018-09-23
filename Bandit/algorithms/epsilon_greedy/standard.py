import random
import numpy as np

def ind_max(x):
  m = max(x)
  return x.index(m)


def np_max(x):
  m = max(x)
  return x.tolist().index(m)

class EpsilonGreedy():
  def __init__(self, epsilon, counts, values):
    self.epsilon = epsilon
    self.counts = counts
    self.values = values
    return

  def initialize(self, n_arms):
    self.counts = [0 for col in range(n_arms)]
    self.values = np.zeros((26247, 8), dtype=np.float)
    return

  def select_arm(self, status):
    if random.random() > self.epsilon and self.values[status][0] != 0:
        temp = 0
        m = self.values[status][0]
        for i in range(8):
            if self.values[status][i] > m:
                m = self.values[status][i]
                temp = i
        return temp
    else:
      return random.randrange(len(self.values[status]))

  def update(self, reward_index, status):
      n = ind_max([reward_index[i] for i in range(len(reward_index))])
      for i in range(len(self.values[status])):
        self.values[status][i] = self.epsilon / 8

      self.values[status][n] = 1 - self.epsilon
      return