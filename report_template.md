# CSMI17 – Artificial Intelligence: Report

## 1. Problem Definition
### 1.1 Robot Path-finding (A*)
- State: robot cell (x, y) on a grid; obstacles block occupancy.
- Actions: up, down, left, right (unit cost).
- Goal test: current cell == goal cell.
- Path cost: number of steps.

### 1.2 Timetable Generation (CSP)
- Variables: courses to be scheduled.
- Domains: (timeslot, room) pairs meeting capacity.
- Constraints: no professor conflicts, no room conflicts, respect unavailability.

## 2. Assumptions / Customizations
- Grid is fully observable and deterministic; unit step cost.
- Random grids with obstacle probability p.
- Timetabling instance generator with random professors, room capacities, timeslots, and unavailability.

## 3. Algorithms / Heuristics
### 3.1 A*
- `f(n) = g(n) + h(n)`; heuristics:
  - h=0 (UCS baseline)
  - Manhattan
  - Euclidean

### 3.2 CSP
- Backtracking + MRV + Degree + LCV
- Backtracking + Forward Checking

## 4. Experimental Setup
- A*: width=35, height=35, obstacle_prob=0.28, 35 trials.
- CSP: 16 trials across varying courses/rooms/timeslots.
- Machine: (fill in).
- Random seeds noted in code.

## 5. Performance Comparison
### 5.1 A*
- Nodes expanded: (paste table/plot)
- Runtime: (paste table/plot)
- Effective branching factor: (paste table/plot)
- Path cost (all heuristics remain optimal under unit costs).

### 5.2 CSP
- Success rate, nodes expanded, runtime comparison.
- Discussion: forward checking typically reduces nodes/time by early pruning.

## 6. GitHub Link
- (Add your repository URL after upload.)
