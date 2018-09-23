#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import math
import numpy as np
import time

# Time Division `Seconds`

# Pipeline Guide

# | CNC 2 | CNC 4 | CNC 6 | CNC 8 |
# \   >   \   >   \   >   \   >   \
# |  RGV  |       |       |       |
# |  · 1  |  · 2  |  · 3  |  · 4  |
# /   >   /   >   /   >   /   >   /
# | CNC 1 | CNC 3 | CNC 5 | CNC 7 |

# RGV Status Definition
# · 0 | RGV Currently `Free`
# · 1 | RGV Currently `Busy`
# · 2 | RGV Currently `Moving`

# Signal Definition
# · 0 | RGV `No Action`
# · 1 | RGV `Load`
# · 2 | RGV `Move`

# RGV Finite State Machine
#     [ No Action ] -> · 0
# · 0 [ Move ] -> · 2 -> · 0
#     [ Load ] -> · 1 -> · 0

# Remember to check load in the last


class RGV:
    """机械臂基类"""
    Position = 1
    Status = 0
    Count = 0
    MonoMove = 30
    DualMove = 60
    TriMove = 90
    Interval = 100
    Finished = 0
    Face = 0
    Marks = np.zeros(9)

    def __init__(self, position, status, mono, dual, triple, oddinterval, eveninterval, clean):
        self.Position = position
        self.Status = status
        self.MonoMove = mono
        self.DualMove = dual
        self.TriMove = triple
        self.oddInterval = oddinterval
        self.evenInterval = eveninterval
        self.Clean = clean
        self.destination = 0

    def __update__(self, signal, dest):
        if dest is not None:
            self.destination = dest
        if self.Status == 0:
            if signal == 0:
                self.Status = 0
                return
            elif signal == 1:
                self.Status = 1
                if dest % 2 == 1:
                    self.Count = self.oddInterval
                else:
                    self.Count = self.evenInterval
                if self.Marks[2 * self.Position - dest] == 0:
                    self.Marks[2 * self.Position - dest] = 1
                    return
                else:
                    self.Count = self.Count + self.Clean
                    return
            else:
                if abs(dest - self.Position) == 0:
                    self.Status = 0
                    return
                elif abs(dest - self.Position) == 1:
                    self.Status = 2
                    self.Position = dest
                    self.Count = self.MonoMove
                    return
                elif abs(dest - self.Position) == 2:
                    self.Status = 2
                    self.Position = dest
                    self.Count = self.DualMove
                    return
                elif abs(dest - self.Position) == 3:
                    self.Status = 2
                    self.Position = dest
                    self.Count = self.TriMove
                    return
        if self.Status == 1:
            if self.Count == 0:
                self.Status = 0
                self.Finished = self.Finished + 1
                return
            self.Status = 1
            self.Count = self.Count - 1
            return

        if self.Status == 2:
            if self.Count == 0:
                self.Status = 0
                return
            self.Status = 2
            self.Count = self.Count - 1
            return

# CNC Status Definition
# · 0 | CNC Currently `FreeRequest`
# · 1 | CNC Currently `FinishRequest`
# · 2 | CNC Currently `Busy`
# · 3 | CNC Currently `Broken`

# CNC Finite State Machine
# --                          <-                                  <-
# | [ `Broken` · 2 ]           |                                   |
# · 0 [ `RGV Respond` · 1 ] -> · 2 [ `Finish Countdown` · 0/1 ] -> · 1 [ `RGV Respond` · 1 ] --
#                              |                                                              |
#                              --                               <-                           <-

# Signal Definition
# · 0 | RGV `No Action`
# · 1 | RGV `Load`
# · 2 | CNC `Broken`


class CNC:
    """加工机器基类"""
    Number = 1
    Status = 0
    Count = 0
    Interval = 30
    Repair = 600

    def __init__(self, number, status, time, repair):
        self.Number = number
        self.Status = status
        self.Interval = time
        self.Repair = repair

    def __update__(self, signal):
        if self.Status == 0:
            if signal == 1:     # RGV Operates
                self.Status = 2
                self.Count = self.Interval
                return
            elif signal == 0:   # RGV Ignores
                self.Status = 0
                return

        if self.Status == 1:
            if signal == 1:     # RGV Operates
                self.Status = 2
                self.Count = self.Interval
                return
            elif signal == 0:   # RGV Ignores
                self.Status = 1
                return

        if self.Status == 2:
            if self.Count == 0:
                self.Status = 1
                return
            if signal != 2:     # RGV Operates
                self.Status = 2
                self.Count = self.Count - 1
                return
            else:               # Broken
                self.Status = 3
                self.Count = self.Repair
                return

        if self.Status == 3:
            if self.Count == 0:
                self.Status = 0
                return

            self.Status = 3
            self.Count = self.Count - 1
            return


class recorder:
    """记录程序"""
    result = 0
    record = []
    temp_record = []

    def visual(self, time, rgv, cnc_array):
        string = []
        string.clear()
        string.append('\n Time %d Pipeline Status :' % time)
        string.append(' | CNC 2 | CNC 4 | CNC 6 | CNC 8 |')
        string.append(' | %5d | %5d | %5d | %5d |'
                      % (cnc_array[2].Count, cnc_array[4].Count, cnc_array[6].Count, cnc_array[8].Count))

        if rgv.Status == 1 and rgv.destination == 0:
            if rgv.Position == 1:
                string.append(' \   ^   \   >   \   >   \   >   \\ ')
            elif rgv.Position == 2:
                string.append(' \   >   \   ^   \   >   \   >   \\ ')
            elif rgv.Position == 3:
                string.append(' \   >   \   >   \   ^   \   >   \\ ')
            else:
                string.append(' \   >   \   >   \   >   \   ^   \\ ')
        else:
            string.append(' \   >   \   >   \   >   \   >   \\ ')

        if rgv.Position == 1:
            string.append(' |  RGV  |       |       |       |')
        elif rgv.Position == 2:
            string.append(' |       |  RGV  |       |       |')
        elif rgv.Position == 3:
            string.append(' |       |       |  RGV  |       |')
        else:
            string.append(' |       |       |       |  RGV  |')
        if rgv.Status == 0:
            string.append(' |             Free              |')
            string.append(' \   >   \   >   \   >   \   >   \\ ')
        elif rgv.Status == 1:
            string.append(' |             Busy              |')
            if rgv.destination == 1:
                if rgv.Position == 1:
                    string.append(' \   ^   \   >   \   >   \   >   \\ ')
                elif rgv.Position == 2:
                    string.append(' \   >   \   ^   \   >   \   >   \\ ')
                elif rgv.Position == 3:
                    string.append(' \   >   \   >   \   ^   \   >   \\ ')
                else:
                    string.append(' \   >   \   >   \   >   \   ^   \\ ')
        else:
            string.append(' |             Move              |')
            string.append(' \   >   \   >   \   >   \   >   \\ ')
        string.append(' | %5d | %5d | %5d | %5d |'
                      % (cnc_array[1].Count, cnc_array[3].Count, cnc_array[5].Count, cnc_array[7].Count))
        string.append(' | CNC 1 | CNC 3 | CNC 5 | CNC 7 |\n')
        return string

    def recordMovement(self, time, rqv, cnc_array):
        self.temp_record.append([time, rqv.Count, 2*rqv.Position - rqv.destination])

    def confirmMovement(self, count):
        if count > self.result:
            self.record.clear()
            self.result = count
            self.record = self.temp_record.copy()
        self.temp_record.clear()

    def saveMovement(self):
        now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
        fqname = now + r" Score " + str(self.result) + r" Movement.tsv"
        fq = open(fqname, "w")
        for e in self.record:
            fq.write("\t".join([str(t) for t in e]) + "\n")
        fq.close()


def near_greedy(rgv, cnc_array):      # Return destination address
    mini = 4
    num = -1
    for c in cnc_array:
        if c is None:
            continue
        if c.Status == 0 or c.Status == 1:
            if abs(math.ceil(c.Number / 2) - rgv.Position) < mini:
                mini = abs(math.ceil(c.Number / 2) - rgv.Position)
                num = c.Number
    return int((num + 1)/2)


def greedy(rgv, cnc_array):      # Return destination address
    for c in cnc_array:
        if c is None:
            continue
        if c.Status == 0 or c.Status == 1:
            return int((c.Number + 1)/2)


def status_graph(time, rgv, cnc_array):
    print("\n Time %d Pipeline Status :" % time)
    print(" | CNC 2 | CNC 4 | CNC 6 | CNC 8 |")
    print(" | %5d | %5d | %5d | %5d |"
        % (cnc_array[2].Count, cnc_array[4].Count, cnc_array[6].Count, cnc_array[8].Count))
    print(" \   >   \   >   \   >   \   >   \\")
    if rgv.Position == 1:
        print(" |  RGV  |       |       |       |")
    elif rgv.Position == 2:
        print(" |       |  RGV  |       |       |")
    elif rgv.Position == 3:
        print(" |       |       |  RGV  |       |")
    else:
        print(" |       |       |       |  RGV  |")
    if rgv.Status == 0:
        print(" |             Free              |")
    elif rgv.Status == 1:
        print(" |             Busy              |")
    else:
        print(" |             Move              |")
    print(" \   >   \   >   \   >   \   >   \\")
    print(" | %5d | %5d | %5d | %5d |"
          % (cnc_array[1].Count, cnc_array[3].Count, cnc_array[5].Count, cnc_array[7].Count))
    print(" | CNC 1 | CNC 3 | CNC 5 | CNC 7 |")


def clock(algorithm):
    time = 0
    flag = 0
    rgv = RGV(1, 0, 30, 60, 90, 100)
    cnc1 = CNC(1, 0, 300, 600)
    cnc2 = CNC(2, 0, 300, 600)
    cnc3 = CNC(3, 0, 300, 600)
    cnc4 = CNC(4, 0, 300, 600)
    cnc5 = CNC(5, 0, 300, 600)
    cnc6 = CNC(6, 0, 300, 600)
    cnc7 = CNC(7, 0, 300, 600)
    cnc8 = CNC(8, 0, 300, 600)
    cnc_array = [None, cnc1, cnc2, cnc3, cnc4, cnc5, cnc6, cnc7, cnc8]
    while time < 28800:
        # status_graph(time, rgv, cnc_array)
        time = time + 1
        rgv.__update__(0, None)

        # Something Might Went Wrong
        #if random.random() <= 0.01:
        #    cnc_array[random.randint(1, 8)].__update__(2)

        for cnc in cnc_array:
            if cnc is None:
                continue
            cnc.__update__(0)
            if cnc.Status == 0 or cnc.Status == 1:
                flag = flag + 1
            else:
                flag = flag + 0
        if flag != 0 and rgv.Status == 0:
            rgv.__update__(2, algorithm(rgv, cnc_array))    # greedy(rgv, cnc_array)

        # Check whether this address needs operation

        if rgv.Status == 0 and (cnc_array[2*rgv.Position-1].Status == 0 or cnc_array[2*rgv.Position-1].Status == 1):
            cnc_array[2*rgv.Position - 1].__update__(1)
            rgv.__update__(1, None)
        elif rgv.Status == 0 and (cnc_array[2*rgv.Position].Status == 0 or cnc_array[2*rgv.Position].Status == 1):
            cnc_array[2 * rgv.Position].__update__(1)
            rgv.__update__(1, None)
    print("\n Finished %d Object!" % rgv.Finished)
    return rgv.Finished


def pivot2urgency(t):
    pivotUrgent = 60
    pivotRelax = 200
    if t < pivotUrgent:
        return 0
    elif t < pivotRelax:
        return 1
    else:
        return 2


def status2encoding(rgv, cnc_array):
    cnc_status = []
    cnc_status.append(pivot2urgency(cnc_array[1].Count))
    cnc_status.append(pivot2urgency(cnc_array[2].Count))
    cnc_status.append(pivot2urgency(cnc_array[3].Count))
    cnc_status.append(pivot2urgency(cnc_array[4].Count))
    cnc_status.append(pivot2urgency(cnc_array[5].Count))
    cnc_status.append(pivot2urgency(cnc_array[6].Count))
    cnc_status.append(pivot2urgency(cnc_array[7].Count))
    cnc_status.append(pivot2urgency(cnc_array[8].Count))
    encoding = 0
    for status in cnc_status:
        encoding = encoding + pow(3, cnc_status.index(status)) * status
    return encoding * 4 + rgv.Position - 1


def action2status(arm):
    return int((arm + 2) / 2)


def test_algorithm(algo, arms, num_sims, horizon, alpha, gamma, epsilon):
  rewards = np.zeros((horizon, len(arms)), dtype=np.float)
  memo = recorder()
  for sim in range(num_sims):
    sim = sim + 1
    if sim % 10 == 1:
        print("Progress %.0f%%" % (100 * sim / num_sims))
    #  algo.initialize(len(arms))
    operate = 580
    time = 0
    rgv = RGV(1, 0, 23, 41, 59, 30, 35, 30)
    cnc1 = CNC(1, 0, operate, 600)
    cnc2 = CNC(2, 0, operate, 600)
    cnc3 = CNC(3, 0, operate, 600)
    cnc4 = CNC(4, 0, operate, 600)
    cnc5 = CNC(5, 0, operate, 600)
    cnc6 = CNC(6, 0, operate, 600)
    cnc7 = CNC(7, 0, operate, 600)
    cnc8 = CNC(8, 0, operate, 600)
    cnc_array = [None, cnc1, cnc2, cnc3, cnc4, cnc5, cnc6, cnc7, cnc8]
    destination = 1
    last_record = 0
    last_arm = 0
    t = status2encoding(rgv, cnc_array)
    memo.recordMovement(time, rgv, cnc_array)
    while time < 28800:
        # status_graph(time, rgv, cnc_array)
        time = time + 1

        rgv.__update__(0, None)

        # Something Might Went Wrong
        #if random.random() <= 0.01:
        #    cnc_array[random.randint(1, 8)].__update__(2)
        flag = 0
        for cnc in cnc_array:
            if cnc is None:
                continue
            cnc.__update__(0)
            if cnc.Status == 0 or cnc.Status == 1:
                flag = flag + 1
            else:
                flag = flag + 0
        # print("flag",time,flag, rgv.Position, cnc.Number, cnc.Status,"\n")

        if flag != 0 and rgv.Status == 0:

            tep = status2encoding(rgv, cnc_array)

            if algo.select_arm(tep) != last_arm:
                index = t
                t = status2encoding(rgv, cnc_array)
                chosen_arm = algo.select_arm(t)

                rewards[index][last_arm] = rewards[index][last_arm] + alpha * (rgv.Finished - last_record + gamma * np.max([rewards[t][i] for i in range(8)])- rewards[index][last_arm]) #
                # print("update:",time, index,last_arm,rewards[index][last_arm],rgv.Finished,"\n")

                algo.update(rewards[index], index)
                last_arm = chosen_arm
                destination = action2status(chosen_arm)
                rgv.__update__(2, destination)    # greedy(rgv, cnc_array)
                memo.recordMovement(time, rgv, cnc_array)
                last_record = rgv.Finished


        # Check whether this address needs operation

        if rgv.Status == 0 and (cnc_array[2*rgv.Position-1].Status == 0 or cnc_array[2*rgv.Position-1].Status == 1):
            cnc_array[2*rgv.Position - 1].__update__(1)
            rgv.__update__(1, 1)
        elif rgv.Status == 0 and (cnc_array[2*rgv.Position].Status == 0 or cnc_array[2*rgv.Position].Status == 1):
            cnc_array[2 * rgv.Position].__update__(1)
            rgv.__update__(1, 0)
            memo.recordMovement(time, rgv, cnc_array)
    print(rgv.Finished)
    memo.confirmMovement(rgv.Finished)
  memo.saveMovement()
  return rewards

