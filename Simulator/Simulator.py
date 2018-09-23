#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import time
import numpy as np
# Time Division `Seconds`
# Global Variables
Marks = np.zeros(9)
# Classes Needs to be Inherited for the simulator to work
class errors:
    """记录程序"""
    result = 0
    record = []
    temp_record = []
    def recordMovement(self, time, rqv, cnc_array):
        self.temp_record.append([time, rqv.Finished, rqv.HalfFinished, 2*rqv.Position - rqv.destination])
    def confirmMovement(self, count):
        if count > self.result:
            self.record.clear()
            self.result = count
            self.record = self.temp_record.copy()
        self.temp_record.clear()
    def saveMovement(self):
        now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
        fqname = now + r" Score " + str(self.result) + r" Errors.tsv"
        fq = open(fqname, "w")
        for e in self.record:
            fq.write("\t".join([str(t) for t in e]) + "\n")
        fq.close()
class recorder:
    """记录程序"""
    result = 0
    record = []
    temp_record = []
    def recordMovement(self, time, rqv, cnc_array):
        self.temp_record.append([time, rqv.Finished, rqv.HalfFinished, 2*rqv.Position - rqv.destination])
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
def near_fcfs(rgv, cnc_array):      # Return destination address
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
def fcfs(rgv, cnc_array):      # Return destination address
    for c in cnc_array:
        if c is None:
            continue
        if c.Status == 0 or c.Status == 1:
            return int((c.Number + 1)/2)
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
    return int((int(arm) + 2) / 2)
memo = recorder()
error = errors()
def clock(algorithm):
    f = open('2018-09-16 04-11-48 QTable_Results.tsv', 'r')
    action = np.zeros(30000, dtype=np.int)
    for line in f.readlines():
        action[int(line.split('\t')[0])] = int(line.split('\t')[1])
    time = 0
    flag = 0
    operate0 = 400
    operate1 = 378
    rgv = RGV(1, 0, 20, 33, 46, 56)
    cnc1 = CNC(1, 0, operate0, operate1, 800)
    cnc2 = CNC(2, 0, operate0, operate1, 800)
    cnc3 = CNC(3, 0, operate0, operate1, 800)
    cnc4 = CNC(4, 0, operate0, operate1, 800)
    cnc5 = CNC(5, 0, operate0, operate1, 800)
    cnc6 = CNC(6, 0, operate0, operate1, 800)
    cnc7 = CNC(7, 0, operate0, operate1, 800)
    cnc8 = CNC(8, 0, operate0, operate1, 800)
    cnc_array = [None, cnc1, cnc2, cnc3, cnc4, cnc5, cnc6, cnc7, cnc8]
    memo.recordMovement(time, rgv, cnc_array)
    while time < 28800:
        # status_graph(time, rgv, cnc_array)
        time = time + 1
        rgv.__update__(0, 0)
        # Something Might Went Wrong
        if random.random() <= 0.001:
            cnc_array[random.randint(1, 8)].__update__(2)
            error.recordMovement(time, rgv, cnc_array)
        flag = 0
        for cnc in cnc_array:
            if cnc is None:
                continue
            cnc.__update__(0)
            if cnc.Status == 0 or cnc.Status == 1:
                flag = flag + 1
            else:
                flag = flag + 0
            # greedy(rgv, cnc_array)
        if flag != 0 and rgv.Status == 0:
            rgv.__update__(2, action2status(action[status2encoding(rgv, cnc_array)]))
            memo.recordMovement(time, rgv, cnc_array)
        # Check whether this address needs operation
        if rgv.Status == 0 and (cnc_array[2*rgv.Position-1].Status == 0 or cnc_array[2*rgv.Position-1].Status == 1):
            cnc_array[2*rgv.Position - 1].__update__(1)
            rgv.__update__(1, 1)
        elif rgv.Status == 0 and (cnc_array[2*rgv.Position].Status == 0 or cnc_array[2*rgv.Position].Status == 1):
            cnc_array[2 * rgv.Position].__update__(1)
            rgv.__update__(1, 0)
        memo.recordMovement(time, rgv, cnc_array)
    memo.confirmMovement(rgv.Finished)
    error.confirmMovement(rgv.Finished)
    print("\n Finished %d Object!" % rgv.Finished)
    return rgv.Finished
# Main Program
n = 20
result = 0
for i in range(1, n):
    result = result + clock(fcfs)
memo.saveMovement()
error.saveMovement()
result = result / n
print(" Final Result is %d Object On Average!" % result)


