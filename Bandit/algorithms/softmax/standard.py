import math
import random
import numpy

# Convenience functions
def ind_max(x):
  m = max(x)
  return x.index(m)


def categorical_draw(probs):
  z = random.random()
  cum_prob = 0.0
  for i in range(len(probs)):
    prob = probs[i]
    cum_prob += prob
    if cum_prob > z:
      return i
  
  return len(probs) - 1

class Softmax:
  def __init__(self, temperature, counts, values):
    self.temperature = temperature
    self.counts = counts
    self.values = values
    return
  
  def initialize(self, n_arms):
    self.counts = [0 for col in range(n_arms)]
    self.values = [0.0 for col in range(n_arms)]
    return

  def select_arm(self, epsilon):
    if random.random() > 1 - epsilon:
      return ind_max(self.values)
    else:
      return random.randrange(len(self.values))

  def update(self, epsilon, reward_index):
    n = ind_max(reward_index)

    self.values[:] = epsilon / n

    self.values[n] = 1 - epsilon
    return
