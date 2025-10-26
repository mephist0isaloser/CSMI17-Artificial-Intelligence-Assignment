#!/usr/bin/env python3
import random, math, time, heapq
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Set, Tuple

@dataclass(order=True)
class PrioritizedItem:
    priority: float
    item: Any=field(compare=False)

@dataclass
class Grid:
    width: int
    height: int
    start: Tuple[int,int]
    goal: Tuple[int,int]
    obstacles: Set[Tuple[int,int]]

def neighbors_4(grid: Grid, node: Tuple[int,int]) -> List[Tuple[int,int]]:
    x, y = node
    res = []
    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        nx, ny = x+dx, y+dy
        if 0 <= nx < grid.width and 0 <= ny < grid.height and (nx,ny) not in grid.obstacles:
            res.append((nx,ny))
    return res

def reconstruct_path(came_from: Dict[Tuple[int,int], Tuple[int,int]], current: Tuple[int,int]) -> List[Tuple[int,int]]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def a_star(grid: Grid, heuristic: Callable[[Tuple[int,int], Tuple[int,int]], float]) -> Dict[str, Any]:
    start, goal = grid.start, grid.goal
    open_heap: List[PrioritizedItem] = []
    heapq.heappush(open_heap, PrioritizedItem(0.0, start))
    came_from: Dict[Tuple[int,int], Tuple[int,int]] = {}
    g_score: Dict[Tuple[int,int], float] = {start: 0.0}
    nodes_expanded = 0
    t0 = time.perf_counter()
    while open_heap:
        current = heapq.heappop(open_heap).item
        if current == goal:
            t1 = time.perf_counter()
            path = reconstruct_path(came_from, current)
            return {"found": True, "path": path, "path_cost": g_score[current], "nodes_expanded": nodes_expanded, "time_s": t1-t0, "depth": len(path)-1}
        nodes_expanded += 1
        for nbr in neighbors_4(grid, current):
            tentative_g = g_score[current] + 1.0
            if tentative_g < g_score.get(nbr, float('inf')):
                came_from[nbr] = current
                g_score[nbr] = tentative_g
                f = tentative_g + heuristic(nbr, goal)
                heapq.heappush(open_heap, PrioritizedItem(f, nbr))
    t1 = time.perf_counter()
    return {"found": False, "path": [], "path_cost": float('inf'), "nodes_expanded": nodes_expanded, "time_s": t1-t0, "depth": 0}

# Heuristics
def h_zero(a: Tuple[int,int], b: Tuple[int,int]) -> float:
    return 0.0

def h_manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> float:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def h_euclidean(a: Tuple[int,int], b: Tuple[int,int]) -> float:
    dx, dy = a[0]-b[0], a[1]-b[1]
    return (dx*dx + dy*dy) ** 0.5

def random_grid(width: int, height: int, obstacle_prob: float = 0.25, rng: random.Random = random) -> Grid:
    cells = [(x,y) for x in range(width) for y in range(height)]
    start = rng.choice(cells)
    goal = rng.choice(cells)
    while goal == start:
        goal = rng.choice(cells)
    obstacles = set()
    for x,y in cells:
        if (x,y) not in (start, goal) and rng.random() < obstacle_prob:
            obstacles.add((x,y))
    return Grid(width, height, start, goal, obstacles)

def ensure_solvable(grid: Grid, max_tries: int = 200) -> Grid:
    # Simple carve approach using UCS to test connectivity
    def ucs_h(a,b): return 0.0
    for _ in range(max_tries):
        res = a_star(grid, ucs_h)
        if res["found"]:
            return grid
        # carve some holes
        holes = 0
        for _ in range(50):
            from random import randrange
            x = randrange(grid.width); y = randrange(grid.height)
            if (x,y) in grid.obstacles and (x,y) not in (grid.start, grid.goal):
                grid.obstacles.remove((x,y)); holes += 1
                if holes >= 10: break
    return grid

def run_experiment(trials=30, width=30, height=30, obstacle_prob=0.3, seed=42):
    rng = random.Random(seed)
    heuristics = {"Zero (UCS)": h_zero, "Manhattan": h_manhattan, "Euclidean": h_euclidean}
    rows = []
    for t in range(trials):
        g = random_grid(width, height, obstacle_prob, rng)
        g = ensure_solvable(g)
        for name, h in heuristics.items():
            res = a_star(g, h)
            rows.append({"trial": t, "heuristic": name, **res})
    return rows

if __name__ == "__main__":
    rows = run_experiment()
    import pandas as pd
    df = pd.DataFrame(rows)
    print(df.groupby("heuristic")[["nodes_expanded","time_s","path_cost"]].mean())
