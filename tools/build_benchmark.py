#!/usr/bin/env python3
"""
build_benchmark.py — regenerate benchmark.json + benchmark.md for a skill workspace iteration
from the per-run ground-truth files (eval_metadata.json + run-*/grading.json + timing).

Why this exists: the committed benchmark summaries had drifted from reality — placeholder model
names, a hard-coded "3 runs per configuration" when only one run exists, and zeroed token
counts even though every run-*/grading.json records the real `total_tokens`. Hand-maintained
summaries drift; a derived summary can't. This tool reads only the per-run files and emits a
summary that is true by construction.

What it reads, per iteration dir (e.g. skills/outreach-email-workspace/iteration-1):
    eval-<id>/eval_metadata.json                      -> eval ids
    eval-<id>/<config>/run-<n>/grading.json           -> expectations, pass rate, tokens, time
where <config> is with_skill/without_skill (or new_skill/old_skill for a skill-vs-skill diff).

Honesty rules:
  - executor/analyzer model is written as "unrecorded" (the historical runs didn't capture it;
    inventing a model name would be fabrication).
  - tool_calls is null (never captured), not 0 (which reads as "made zero tool calls").
  - tokens come from each run's own timing; the summary ± is the spread ACROSS eval cases,
    stated as such — not mislabeled as repeated runs.

Usage:
    python3 tools/build_benchmark.py skills/outreach-email-workspace/iteration-1
    python3 tools/build_benchmark.py --all          # every skills/*-workspace/iteration-*
    python3 tools/build_benchmark.py --all --check   # don't write; exit 1 if anything differs
"""
import argparse
import glob
import json
import math
import os
import re
import sys

PRIMARY = ("with_skill", "new_skill")
BASELINE = ("without_skill", "old_skill")
LABELS = {"with_skill": "With Skill", "without_skill": "Without Skill",
          "new_skill": "New Skill", "old_skill": "Old Skill"}


def _stats(values):
    """mean / sample-stddev (ddof=1) / min / max, matching the original summaries."""
    n = len(values)
    if n == 0:
        return {"mean": 0.0, "stddev": 0.0, "min": 0, "max": 0}
    mean = sum(values) / n
    stddev = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
    return {"mean": round(mean, 4), "stddev": round(stddev, 4),
            "min": min(values), "max": max(values)}


def _config_dirs(eval_dir):
    out = []
    for name in sorted(os.listdir(eval_dir)):
        d = os.path.join(eval_dir, name)
        if os.path.isdir(d) and glob.glob(os.path.join(d, "run-*", "grading.json")):
            out.append(name)
    # order: primary config(s) first, then baseline
    return (sorted([c for c in out if c in PRIMARY]) +
            sorted([c for c in out if c in BASELINE]) +
            sorted([c for c in out if c not in PRIMARY + BASELINE]))


def build(iter_dir):
    skill = os.path.basename(os.path.dirname(iter_dir)).replace("-workspace", "")
    eval_dirs = sorted(glob.glob(os.path.join(iter_dir, "eval-*")),
                       key=lambda p: int(p.rsplit("-", 1)[-1]))
    runs, evals_run, per_config = [], [], {}
    runs_per_cfg = set()

    configs_seen = []
    for ed in eval_dirs:
        meta_path = os.path.join(ed, "eval_metadata.json")
        cfgs = _config_dirs(ed)
        if not os.path.exists(meta_path) or not cfgs:
            # an incomplete/empty eval dir (no metadata or no graded runs) — skip it
            sys.stderr.write(f"skip  {ed} (no eval_metadata.json or no graded runs)\n")
            continue
        meta = json.load(open(meta_path))
        eid = meta["eval_id"]
        evals_run.append(eid)
        for cfg in cfgs:
            if cfg not in configs_seen:
                configs_seen.append(cfg)
            run_files = sorted(glob.glob(os.path.join(ed, cfg, "run-*", "grading.json")))
            runs_per_cfg.add(len(run_files))
            for rf in run_files:
                rn = int(re.search(r"run-(\d+)", rf).group(1))
                g = json.load(open(rf))
                s, t = g.get("summary", {}), g.get("timing", {})
                tokens = t.get("total_tokens", 0)
                secs = t.get("total_duration_seconds")
                if secs is None and t.get("duration_ms") is not None:
                    secs = round(t["duration_ms"] / 1000, 1)
                runs.append({
                    "eval_id": eid,
                    "configuration": cfg,
                    "run_number": rn,
                    "result": {
                        "pass_rate": s.get("pass_rate", 0),
                        "passed": s.get("passed", 0),
                        "failed": s.get("failed", 0),
                        "total": s.get("total", 0),
                        "time_seconds": secs if secs is not None else 0,
                        "tokens": tokens,
                        "tool_calls": None,  # never captured by the harness
                        "errors": 0,
                    },
                    "expectations": g.get("expectations", []),
                    "notes": [],
                })
                per_config.setdefault(cfg, {"pass": [], "time": [], "tok": []})
                per_config[cfg]["pass"].append(s.get("pass_rate", 0))
                per_config[cfg]["time"].append(secs if secs is not None else 0)
                per_config[cfg]["tok"].append(tokens)

    run_summary = {}
    for cfg, vals in per_config.items():
        run_summary[cfg] = {
            "pass_rate": _stats(vals["pass"]),
            "time_seconds": _stats(vals["time"]),
            "tokens": _stats(vals["tok"]),
        }

    primary = next((c for c in configs_seen if c in PRIMARY), None)
    baseline = next((c for c in configs_seen if c in BASELINE), None)
    if primary and baseline:
        run_summary["delta"] = {
            "pass_rate": f"{run_summary[primary]['pass_rate']['mean'] - run_summary[baseline]['pass_rate']['mean']:+.2f}",
            "time_seconds": f"{run_summary[primary]['time_seconds']['mean'] - run_summary[baseline]['time_seconds']['mean']:+.1f}",
            "tokens": f"{run_summary[primary]['tokens']['mean'] - run_summary[baseline]['tokens']['mean']:+.0f}",
        }

    # preserve the real timestamp from the existing benchmark.json if present
    timestamp = ""
    existing = os.path.join(iter_dir, "benchmark.json")
    if os.path.exists(existing):
        timestamp = json.load(open(existing)).get("metadata", {}).get("timestamp", "")

    rpc = runs_per_cfg.pop() if len(runs_per_cfg) == 1 else (max(runs_per_cfg) if runs_per_cfg else 0)
    bench = {
        "metadata": {
            "skill_name": skill,
            "skill_path": f"skills/{skill}",
            "executor_model": "unrecorded",
            "analyzer_model": "unrecorded",
            "timestamp": timestamp,
            "evals_run": evals_run,
            "runs_per_configuration": rpc,
            "note": (f"Summary mean/stddev is the spread across the {len(evals_run)} distinct "
                     f"eval case{'s' if len(evals_run) != 1 else ''}, {rpc} run each. tokens are "
                     "backfilled from each run's timing; tool_calls were not captured by the harness."),
        },
        "runs": runs,
        "run_summary": run_summary,
        "notes": [],
    }
    return bench, _render_md(bench)


def _render_md(bench):
    m = bench["metadata"]
    rs = bench["run_summary"]
    configs = [c for c in (list(PRIMARY) + list(BASELINE)) if c in rs]
    n_evals = len(m["evals_run"])
    rpc = m["runs_per_configuration"]
    lines = [
        f"# Skill Benchmark: {m['skill_name']}",
        "",
        f"**Model**: {m['executor_model']}",
        f"**Date**: {m['timestamp']}",
        f"**Evals**: {', '.join(str(e) for e in m['evals_run'])} "
        f"({rpc} run per configuration each; ± is the spread across the {n_evals} "
        f"eval case{'s' if n_evals != 1 else ''})",
        "",
        "## Summary",
        "",
    ]
    if len(configs) == 2:
        a, b = configs
        la, lb = LABELS.get(a, a), LABELS.get(b, b)

        def pct(x):
            return f"{round(x['mean']*100)}% ± {round(x['stddev']*100)}%"

        def secs(x):
            return f"{x['mean']:.1f}s ± {x['stddev']:.1f}s"

        def tok(x):
            return f"{round(x['mean'])} ± {round(x['stddev'])}"

        d = rs.get("delta", {})
        lines += [
            f"| Metric | {la} | {lb} | Delta |",
            "|--------|------------|---------------|-------|",
            f"| Pass Rate | {pct(rs[a]['pass_rate'])} | {pct(rs[b]['pass_rate'])} | {d.get('pass_rate','')} |",
            f"| Time | {secs(rs[a]['time_seconds'])} | {secs(rs[b]['time_seconds'])} | {d.get('time_seconds','')}s |",
            f"| Tokens | {tok(rs[a]['tokens'])} | {tok(rs[b]['tokens'])} | {d.get('tokens','')} |",
        ]
    return "\n".join(lines) + "\n"


def iter_dirs():
    return sorted(glob.glob("skills/*-workspace/iteration-*"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("iter_dir", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true", help="don't write; exit 1 if output differs")
    args = ap.parse_args(argv)

    targets = iter_dirs() if args.all else [args.iter_dir]
    if not targets or targets == [None]:
        ap.error("give an iteration dir or --all")

    differed = False
    for d in targets:
        bench, md = build(d)
        bj = json.dumps(bench, indent=2) + "\n"
        for path, content in ((os.path.join(d, "benchmark.json"), bj),
                              (os.path.join(d, "benchmark.md"), md)):
            old = open(path).read() if os.path.exists(path) else None
            if old != content:
                differed = True
                if args.check:
                    print(f"DIFF  {path}")
                else:
                    open(path, "w").write(content)
                    print(f"WROTE {path}")
            else:
                print(f"ok    {path}")
    return 1 if (args.check and differed) else 0


if __name__ == "__main__":
    sys.exit(main())
