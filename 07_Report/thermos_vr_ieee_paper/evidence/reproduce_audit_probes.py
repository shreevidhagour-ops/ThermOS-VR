"""
Reproducible versions of the read-only audit probes whose numbers are
cited in the paper (previously run only in session scratch):

  P1  Independent EDF reference simulator vs the v2 engine
      (4 benchmark workloads + 3,000 seeded random task sets,
       1-3 cores, preemptive and non-preemptive, DVFS off).
  P2  EEVDF-inspired policy on 1 and 2 cores: ineligible dispatches and
      maximum |lag| (in units of one NICE_0 slice), DVFS on.
  P3  TA-EDF thermal idle insertion: how often the hold-back condition
      arose, what happened to each slack-rich task, and whether any core
      was left idle.

Imports the day5 simulator read-only; writes nothing except stdout.
Run:  python -B reproduce_audit_probes.py > audit_probes_output.txt
"""

import collections
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DAY5 = os.path.join(ROOT, "03_Code", "day5_modern_baselines")
sys.path.insert(0, DAY5)
sys.path.insert(0, os.path.join(DAY5, "tests"))

import testutil  # noqa: E402,F401  (adds the v1 folders to sys.path)
from testutil import task  # noqa: E402
from sim_engine import Simulator, create_cores, GOVERNORS  # noqa: E402
from policies import (  # noqa: E402
    GlobalEDFPolicy, EDFNonPreemptivePolicy, ThermalAwareEDFPolicy,
    EEVDFInspiredPolicy, NICE_0_WEIGHT, edf_key,
)
import run_benchmark as RB  # noqa: E402


def cores_for(m):
    cores = (create_cores() + create_cores())[:m]
    for i, c in enumerate(cores):
        c.core_id = i + 1
    return cores


# ---------------------------------------------------------------- P1
def reference_edf(spec, m, preemptive):
    """Independent tick-based EDF at 1 work unit per tick (DVFS off)."""
    remaining = {p: b for p, (a, b, d) in spec.items()}
    done, wait, running, t = {}, collections.Counter(), [], 0
    key = lambda p: (spec[p][2], spec[p][0], p)
    while len(done) < len(spec):
        avail = [p for p, (a, b, d) in spec.items() if a <= t and p not in done]
        if preemptive:
            run = sorted(avail, key=key)[:m]
        else:
            run = [p for p in running if p in avail]
            for p in sorted((p for p in avail if p not in run), key=key):
                if len(run) < m:
                    run.append(p)
        for p in avail:
            if p not in run:
                wait[p] += 1
        for p in run:
            remaining[p] -= 1
        t += 1
        running = [p for p in run if remaining[p] > 0]
        for p in run:
            if remaining[p] == 0:
                done[p] = t
    return done, wait


def probe_edf():
    rng = random.Random(2026)
    sets = [{p.pid: (p.arrival_time, p.burst_time, p.deadline) for p in f()}
            for _, f in RB.WORKLOADS]
    for _ in range(3000):
        n = rng.randint(1, 7)
        sets.append({i + 1: (rng.randint(0, 10), rng.randint(1, 8), rng.randint(1, 40))
                     for i in range(n)})
    cases = mismatches = 0
    for spec in sets:
        for m in (1, 2, 3):
            for preemptive, cls in ((True, GlobalEDFPolicy), (False, EDFNonPreemptivePolicy)):
                procs = [task(p, a, b, d) for p, (a, b, d) in spec.items()]
                sim = Simulator(procs, cores_for(m), cls(), GOVERNORS["off"]())
                sim.run()
                done, wait = reference_edf(spec, m, preemptive)
                got_c = {p.pid: p.completion_time for p in sim.processes}
                got_w = {p.pid: p.waiting_time for p in sim.processes}
                miss_ok = all(p.deadline_missed == (p.completion_time > p.deadline)
                              for p in sim.processes)
                cases += 1
                if got_c != done or got_w != {p: wait[p] for p in spec} or not miss_ok:
                    mismatches += 1
    print(f"P1 EDF reference: {len(sets)} task sets (4 benchmark + 3000 random, seed 2026) "
          f"x 3 core counts x 2 variants = {cases} comparisons; mismatches = {mismatches}")
    return mismatches == 0


# ---------------------------------------------------------------- P2
def probe_eevdf(processes, n_cores, governor):
    policy = EEVDFInspiredPolicy()
    original = policy.schedule
    stats = collections.Counter()
    lags = [0.0]

    def spy(t, ready, cores):
        mapping = original(t, ready, cores)
        runnable = ready + [c.current_process for c in cores if c.current_process]
        chosen = [x for x in mapping.values() if x is not None]
        stats["ineligible_dispatched"] += sum(
            1 for x in chosen if policy.v[x.pid] > policy.V + 1e-12)
        for p in runnable:
            lags.append(abs(policy.weight(p) * (policy.V - policy.v[p.pid]) / NICE_0_WEIGHT))
        return mapping

    policy.schedule = spy
    Simulator(processes, create_cores()[:n_cores], policy, GOVERNORS[governor]()).run()
    return stats["ineligible_dispatched"], max(lags)


def probe_eevdf_all():
    print("P2 EEVDF-inspired (DVFS on): ineligible dispatches / max |lag| in slices")
    for name, f in RB.WORKLOADS:
        one = probe_eevdf(f(), 1, "hysteresis")
        two = probe_eevdf(f(), 2, "hysteresis")
        print(f"   {name:27s} 1 core: {one[0]:3d} / {one[1]:5.2f}    2 cores: {two[0]:3d} / {two[1]:5.2f}")


# ---------------------------------------------------------------- P3
def probe_idle_insertion():
    print("P3 TA-EDF hold-back analysis")
    totals = collections.Counter()
    for gov in ("off", "hysteresis"):
        for name, f in RB.WORKLOADS:
            policy = ThermalAwareEDFPolicy()
            original = policy.schedule
            c = collections.Counter()
            held_events = []

            def spy(t, ready, cores, policy=policy, original=original, c=c, held_events=held_events):
                running = [x.current_process for x in cores if x.current_process]
                cands = sorted(ready + running, key=edf_key)
                hot = [x for x in cores if x.temperature >= policy.guard_temperature]
                rich = [p for p in cands if policy.slack(p, t) >= policy.defer_slack]
                if hot and rich:
                    c["ticks_hot_core_and_slack_rich_task"] += 1
                    free = list(cores)
                    for p in cands:
                        if not free:
                            if p in rich:
                                c["cores_already_filled"] += 1
                            continue
                        core = policy.choose_core(p, free, t)
                        if p in rich:
                            if core.temperature < policy.guard_temperature:
                                c["placed_on_core_below_guard"] += 1
                            else:
                                c["skipped_by_hold_back"] += 1
                                held_events.append((t, p.name, round(policy.slack(p, t), 2),
                                                    core.core_id, round(core.temperature, 2)))
                        if (core.temperature >= policy.guard_temperature
                                and policy.slack(p, t) >= policy.defer_slack):
                            continue
                        free.remove(core)
                mapping = original(t, ready, cores)
                chosen = {id(x) for x in mapping.values() if x}
                idle = sum(1 for x in mapping.values() if x is None)
                unassigned = [p for p in cands if id(p) not in chosen]
                c["idle_core_ticks_with_waiting_task"] += min(idle, len(unassigned))
                return mapping

            policy.schedule = spy
            Simulator(f(), create_cores(), policy, GOVERNORS[gov]()).run()
            totals.update(c)
            if c:
                print(f"   {gov:10s} {name:27s} {dict(c)}  skipped: {held_events}")
    print(f"   TOTAL over 64-run benchmark: {dict(totals)}")
    return totals["idle_core_ticks_with_waiting_task"] == 0


if __name__ == "__main__":
    ok1 = probe_edf()
    probe_eevdf_all()
    ok3 = probe_idle_insertion()
    print(f"\nP1 zero mismatches: {ok1}; P3 no core ever idled by hold-back: {ok3}")
