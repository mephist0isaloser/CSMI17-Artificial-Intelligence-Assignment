# CSMI17 – Artificial Intelligence Assignment

This repository contains two problems:
1. **Robot Path-finding (A\*)** with three heuristics (Zero/UCS, Manhattan, Euclidean) and a benchmarking harness.
2. **Timetable Generation (CSP)** solved via
   - Backtracking + MRV/degree + LCV
   - Backtracking + Forward Checking (+ same ordering heuristics)

## How to run

```bash
python3 pathfinding_astar.py
python3 timetable_csp.py
```

To reproduce the full experiments and charts, run the notebook/script used to generate results (or call the functions in your own runner).

## Heuristics & Metrics

- **A\*** heuristics: Zero (UCS baseline), Manhattan, Euclidean.  
- Metrics: nodes expanded, runtime, path cost, and effective branching factor.

- **CSP** methods: backtracking with ordering heuristics vs. forward checking.  
- Metrics: success rate, nodes expanded, runtime.

## Files

- `pathfinding_astar.py` – A\* grid world, heuristics, and mini-benchmark.
- `timetable_csp.py` – CSP formulation and solvers.
- `report_template.md` – Fill-in structure for your submission.
- `figures/` – Placeholder for plots you generate.
