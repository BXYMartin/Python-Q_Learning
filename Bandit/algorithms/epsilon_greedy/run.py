import os,sys
import time

# Convenience functions
def ind_max(x):
  m = max(x)
  return x.index(m)

# Need access to random numbers
import random

# Definitions of bandit arms
from arms.adversarial import *
from arms.bernoulli import *
from arms.normal import *

# Definitions of bandit algorithms
from algorithms.epsilon_greedy.standard import *
from algorithms.epsilon_greedy.annealing import *
from algorithms.softmax.standard import *
from algorithms.softmax.annealing import *
from algorithms.ucb.ucb1 import *
from algorithms.ucb.ucb2 import *
from algorithms.exp3.exp3 import *
from algorithms.hedge.hedge import *

# # Testing framework
from testing_framework.tests import *


random.seed(1)
means = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]
n_arms = len(means)
random.shuffle(means)
arms = list(map(lambda mu: NormalArm(mu, 0.1), means))      # miu and sigma set
print("Best arm is " + str(ind_max(means)))

now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))

for epsilon in [0.3]:   # This is epsilon, 0.2, 0.3, 0.4, 0.5]:
    algo = EpsilonGreedy(epsilon, [], [])
    algo.initialize(n_arms)
    QTable = test_algorithm(algo, arms, 2000, 26247, 1, 0.9, epsilon)

fqname = now+r" QTable_Results.tsv"
fq = open(fqname, "w")
for i in range(26247):
    index = ind_max([QTable[i][j] for j in range(8)])
    fq.write(str(i) + "\t" + str(index) + "\t" + str(QTable[i][index]) + "\n")
fq.close()