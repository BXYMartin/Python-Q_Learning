# Dynamic Dispatch Strategy for RGV
A Reinforcement Learning Implementation in Python for Mathematical Modelling, implemented by Q-Learning (<img src="https://latex.codecogs.com/gif.latex?\inline&space;\epsilon-Greedy" title="\epsilon-Greedy" />)

# Basics
* `/Bandit` Folder contains trainning algorithms.
* `/Simulator` Folder contains simulator based on the selected strategy file (Q-Table).
* `/Results` Folder contains trained dataset and strategy.

# Factory Setup
```
 | CNC 2 | CNC 4 | CNC 6 | CNC 8 |
 \   >   \   >   \   >   \   >   \
 |  RGV  |       |       |       |
 |  · 1  |  · 2  |  · 3  |  · 4  |
 /   >   /   >   /   >   /   >   /
 | CNC 1 | CNC 3 | CNC 5 | CNC 7 |
```
# RGV Status Definition
```
RGV Status Definition
 · 0 | RGV Currently `Free`
 · 1 | RGV Currently `Busy`
 · 2 | RGV Currently `Moving`
 
Signal Definition
 · 0 | RGV `No Action`
 · 1 | RGV `Load`
 · 2 | RGV `Move`
```

# CNC Status Definition
```
CNC Status Definition
 · 0 | CNC Currently `FreeRequest`
 · 1 | CNC Currently `FinishRequest`
 · 2 | CNC Currently `Busy`
  · 3 | CNC Currently `Broken`
  
CNC Finite State Machine
 --                          <-                                  <-
 | [ `Broken` · 2 ]           |                                   |
 · 0 [ `RGV Respond` · 1 ] -> · 2 [ `Finish Countdown` · 0/1 ] -> · 1 [ `RGV Respond` · 1 ] --
                              |                                                              |
                              --                               <-                           <-
                              
Signal Definition
 · 0 | RGV `No Action`
 · 1 | RGV `Load`
 · 2 | CNC `Broken`
```
