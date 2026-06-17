#!/usr/bin/env python3
"""
Offline test for build_benchmark.py — synthesize a tiny workspace iteration with known
per-run numbers and assert the derived summary is honest (real tokens, null tool_calls,
correct run count, ± across eval cases). Run: `python3 test_build_benchmark.py`
"""
import json
import os
import tempfile

import build_benchmark as b


def _run(eval_dir, cfg, pass_rate, passed, total, tokens, secs):
    d = os.path.join(eval_dir, cfg, "run-1")
    os.makedirs(d)
    json.dump({
        "expectations": [{"text": "x", "passed": True, "evidence": "found"}],
        "summary": {"pass_rate": pass_rate, "passed": passed, "failed": total - passed, "total": total},
        "timing": {"total_tokens": tokens, "duration_ms": int(secs * 1000), "total_duration_seconds": secs},
    }, open(os.path.join(d, "grading.json"), "w"))


def _make_ws():
    tmp = tempfile.mkdtemp()
    iterd = os.path.join(tmp, "skills", "demo-skill-workspace", "iteration-1")
    for eid, (wp, wt, op, ot) in enumerate([
        (1.0, 50.0, 0.8, 30.0),   # eval 0: with 100%/50s/1000tok, without 80%/30s/800tok
        (1.0, 60.0, 0.9, 40.0),   # eval 1
    ]):
        ed = os.path.join(iterd, f"eval-{eid}")
        os.makedirs(ed)
        json.dump({"eval_id": eid, "eval_name": f"e{eid}", "prompt": "p", "assertions": []},
                  open(os.path.join(ed, "eval_metadata.json"), "w"))
        _run(ed, "with_skill", wp, int(wp * 5), 5, 1000 + eid * 200, wt)
        _run(ed, "without_skill", op, int(op * 5), 5, 800 + eid * 200, ot)
    # a stale benchmark.json with the exact defects we fix
    json.dump({"metadata": {"timestamp": "2026-06-13T00:00:00Z", "executor_model": "<model-name>",
                            "runs_per_configuration": 3},
               "runs": [{"result": {"tokens": 0, "tool_calls": 0}}]},
              open(os.path.join(iterd, "benchmark.json"), "w"))
    return iterd


def test_derived_summary_is_honest():
    iterd = _make_ws()
    bench, md = b.build(iterd)
    meta = bench["metadata"]

    assert meta["skill_name"] == "demo-skill"
    assert meta["skill_path"] == "skills/demo-skill"
    assert meta["executor_model"] == "unrecorded" and meta["analyzer_model"] == "unrecorded"
    assert meta["timestamp"] == "2026-06-13T00:00:00Z", "real timestamp must be preserved"
    assert meta["runs_per_configuration"] == 1, "one run per config, not 3"
    assert meta["evals_run"] == [0, 1]

    assert len(bench["runs"]) == 4, "2 evals x 2 configs"
    for r in bench["runs"]:
        assert r["result"]["tokens"] > 0, "tokens backfilled from timing"
        assert r["result"]["tool_calls"] is None, "tool_calls null (uncaptured), not 0"

    rs = bench["run_summary"]
    assert rs["with_skill"]["pass_rate"]["mean"] == 1.0
    assert rs["with_skill"]["pass_rate"]["stddev"] == 0.0
    # without: (0.8+0.9)/2 = 0.85
    assert abs(rs["without_skill"]["pass_rate"]["mean"] - 0.85) < 1e-9
    # tokens with_skill: (1000+1200)/2 = 1100
    assert rs["with_skill"]["tokens"]["mean"] == 1100.0
    assert rs["delta"]["pass_rate"] == "+0.15"

    # markdown reflects reality, no placeholder, no "3 runs", real tokens
    assert "<model-name>" not in md
    assert "1 run per configuration each" in md
    assert "± is the spread across the 2 eval cases" in md
    # sample stddev (ddof=1) of {1000,1200} and {800,1000} is sqrt(20000) ≈ 141
    assert "| Tokens | 1100 ± 141 | 900 ± 141 | +200 |" in md
    print("PASS  derived benchmark is honest (model, runs, tokens, tool_calls, delta, md)")


if __name__ == "__main__":
    test_derived_summary_is_honest()
    print("\nbuild_benchmark test passed.")
