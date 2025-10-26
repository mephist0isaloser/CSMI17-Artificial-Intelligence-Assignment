#!/usr/bin/env python3
import random, time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

@dataclass
class Course:
    name: str
    professor: str
    size: int

@dataclass
class TimetableInstance:
    courses: List[Course]
    rooms: List[Tuple[str, int]]
    timeslots: List[str]
    unavailable: Dict[str, Set[str]]  # professor -> blocked timeslots

Assignment = Dict[str, Tuple[str, str]]  # course -> (timeslot, room)

def random_timetable_instance(n_courses=12, n_rooms=5, n_timeslots=10, seed=123) -> TimetableInstance:
    rng = random.Random(seed + n_courses + n_rooms + n_timeslots)
    profs = [f"P{i}" for i in range(max(4, n_courses//3))]
    courses = [Course(name=f"C{i}", professor=rng.choice(profs), size=rng.randint(20, 120)) for i in range(n_courses)]
    rooms = [(f"R{j}", rng.choice([30, 50, 80, 120])) for j in range(n_rooms)]
    days = ["Mon","Tue","Wed","Thu","Fri"]; hours = ["9","10","11","12","14","15"]
    pool = [f"{d}-{h}" for d in days for h in hours]; rng.shuffle(pool)
    timeslots = pool[:n_timeslots]
    unavailable = {p: set() for p in profs}
    for p in profs:
        if rng.random() < 0.6:
            k = max(0, rng.randint(0, max(1,n_timeslots//4)))
            unavailable[p] = set(rng.sample(timeslots, k=k))
    return TimetableInstance(courses, rooms, timeslots, unavailable)

def csp_constraints_ok(course_name: str, value: Tuple[str,str], assign: Assignment, inst: TimetableInstance) -> bool:
    t, r = value
    course = next(c for c in inst.courses if c.name == course_name)
    r_cap = next(cap for (rn, cap) in inst.rooms if rn == r)
    if course.size > r_cap:
        return False
    if t in inst.unavailable.get(course.professor, set()):
        return False
    for c2, (t2, r2) in assign.items():
        if t == t2 and r == r2:
            return False
        prof2 = next(c for c in inst.courses if c.name == c2).professor
        if t == t2 and prof2 == course.professor:
            return False
    return True

def domains_for_course(course: Course, inst: TimetableInstance) -> List[Tuple[str,str]]:
    dom = []
    for t in inst.timeslots:
        if t in inst.unavailable.get(course.professor, set()):
            continue
        for r, cap in inst.rooms:
            if course.size <= cap:
                dom.append((t,r))
    return dom

def select_unassigned_variable_MRV_degree(assign: Assignment, inst: TimetableInstance, domains: Dict[str, List[Tuple[str,str]]]) -> str:
    unassigned = [c.name for c in inst.courses if c.name not in assign]
    mrv = min(unassigned, key=lambda cn: len(domains[cn]))
    min_len = len(domains[mrv])
    ties = [cn for cn in unassigned if len(domains[cn]) == min_len]
    if len(ties) == 1:
        return mrv
    def degree(cn: str) -> int:
        my_ts = set(t for (t,r) in domains[cn])
        count = 0
        for other in unassigned:
            if other == cn: continue
            oth_ts = set(t for (t,r) in domains[other])
            count += len(my_ts & oth_ts)
        return -count
    return max(ties, key=degree)

def order_domain_values_LCV(cn: str, assign: Assignment, inst: TimetableInstance, domains: Dict[str, List[Tuple[str,str]]]) -> List[Tuple[str,str]]:
    values = domains[cn][:]
    def score(val: Tuple[str,str]) -> int:
        t, r = val
        pruning = 0
        for other in [c.name for c in inst.courses if c.name not in assign and c.name != cn]:
            for v in domains[other]:
                if v[0] == t and v[1] == r:
                    pruning += 1
        return pruning
    values.sort(key=score)
    return values

def forward_checking(domains: Dict[str, List[Tuple[str,str]]], var: str, val: Tuple[str,str], inst: TimetableInstance, assignment: Assignment) -> Optional[Dict[str, List[Tuple[str,str]]]]:
    new_domains = {k: v[:] for k, v in domains.items()}
    t, r = val
    new_domains[var] = [val]
    for other in new_domains:
        if other == var or other in assignment:
            continue
        pruned = []
        for v in new_domains[other]:
            if v[0] == t and v[1] == r:
                pruned.append(v); continue
            prof_var = next(c for c in inst.courses if c.name == var).professor
            prof_oth = next(c for c in inst.courses if c.name == other).professor
            if prof_var == prof_oth and v[0] == t:
                pruned.append(v); continue
        if pruned:
            new_domains[other] = [v for v in new_domains[other] if v not in pruned]
            if not new_domains[other]:
                return None
    return new_domains

def backtracking_search_ordering(inst: TimetableInstance, time_limit_s: float = 10.0):
    start = time.perf_counter()
    domains = {c.name: domains_for_course(c, inst) for c in inst.courses}
    nodes = 0
    assignment: Assignment = {}
    def backtrack():
        nonlocal nodes
        if time.perf_counter() - start > time_limit_s: return None
        if len(assignment) == len(inst.courses): return assignment
        var = select_unassigned_variable_MRV_degree(assignment, inst, domains)
        for val in order_domain_values_LCV(var, assignment, inst, domains):
            if csp_constraints_ok(var, val, assignment, inst):
                assignment[var] = val; nodes += 1
                result = backtrack()
                if result is not None: return result
                assignment.pop(var, None)
        return None
    t0 = time.perf_counter(); sol = backtrack(); t1 = time.perf_counter()
    return {"solution": sol, "nodes": nodes, "time_s": t1-t0, "success": sol is not None}

def backtracking_search_forward_checking(inst: TimetableInstance, time_limit_s: float = 10.0):
    start = time.perf_counter()
    domains = {c.name: domains_for_course(c, inst) for c in inst.courses}
    nodes = 0
    assignment: Assignment = {}
    def backtrack(local_domains):
        nonlocal nodes
        if time.perf_counter() - start > time_limit_s: return None
        if len(assignment) == len(inst.courses): return assignment
        var = select_unassigned_variable_MRV_degree(assignment, inst, local_domains)
        values = order_domain_values_LCV(var, assignment, inst, local_domains)
        for val in values:
            if csp_constraints_ok(var, val, assignment, inst):
                pruned = forward_checking(local_domains, var, val, inst, assignment)
                if pruned is not None:
                    assignment[var] = val; nodes += 1
                    result = backtrack(pruned)
                    if result is not None: return result
                    assignment.pop(var, None)
        return None
    t0 = time.perf_counter(); sol = backtrack(domains); t1 = time.perf_counter()
    return {"solution": sol, "nodes": nodes, "time_s": t1-t0, "success": sol is not None}

if __name__ == "__main__":
    inst = random_timetable_instance()
    a = backtracking_search_ordering(inst)
    b = backtracking_search_forward_checking(inst)
    print("Ordering:", a["success"], a["nodes"], a["time_s"])
    print("Forward Checking:", b["success"], b["nodes"], b["time_s"])
