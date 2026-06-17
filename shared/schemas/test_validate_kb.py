#!/usr/bin/env python3
"""
Offline tests for validate_kb.py — build tiny knowledge bases in a temp dir and assert the
validator flags exactly what it should. Run: `python3 test_validate_kb.py`
"""
import os
import tempfile

import validate_kb as v


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


GOOD_PROF = """---
slug: jane-smith-mit
name: Jane Smith
field: machine learning
fit_score: 84
funding_signal: strong
accepting_students: yes
admission_model: direct-to-advisor
email_policy: welcomes-inquiry
enrichment: openalex
---
## Sources
- https://example.edu
"""

GOOD_OPENING = """---
slug: smith-lab-rl-2027
professor: jane-smith-mit
institution: mit
title: PhD in RL
discovered: 2026-06-12
verified_on: 2026-06-12
deadline: 2026-12-01
start_year: 2027
funding: fully funded
status: new
---
## Description
x
"""

GOOD_PROFILE = """---
name: Boyuan
field: machine learning
target_start: 2027
funding_required: true
---
## Research interests
x
"""


def _levels(issues):
    return [lv for lv, _, _ in issues]


def test_clean_kb_has_no_errors():
    with tempfile.TemporaryDirectory() as d:
        write(os.path.join(d, "professors", "jane-smith-mit.md"), GOOD_PROF)
        write(os.path.join(d, "openings", "smith-lab-rl-2027.md"), GOOD_OPENING)
        write(os.path.join(d, "profile", "profile.md"), GOOD_PROFILE)
        issues = v.validate_kb(d)
        assert "ERROR" not in _levels(issues), issues
        # a fully-populated KB should also have no warnings
        assert "WARN" not in _levels(issues), issues
    print("PASS  clean KB → no errors, no warnings")


def test_bad_enum_is_error():
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_PROF.replace("email_policy: welcomes-inquiry",
                                "email_policy: sure-go-ahead")
        write(os.path.join(d, "professors", "jane-smith-mit.md"), bad)
        issues = v.validate_kb(d)
        msgs = [m for lv, _, m in issues if lv == "ERROR"]
        assert any("email_policy" in m for m in msgs), issues
    print("PASS  bad enum value → ERROR")


def test_missing_typed_field_is_warn_not_error():
    with tempfile.TemporaryDirectory() as d:
        # a pre-tightening professor file: identity present, typed contact fields absent
        legacy = "---\nslug: old-prof\nname: Old Prof\nfield: biology\n---\n## Notes\nx\n"
        write(os.path.join(d, "professors", "old-prof.md"), legacy)
        issues = v.validate_kb(d)
        assert "ERROR" not in _levels(issues), issues
        warn_msgs = [m for lv, _, m in issues if lv == "WARN"]
        assert any("email_policy" in m for m in warn_msgs), issues
        assert any("admission_model" in m for m in warn_msgs), issues
    print("PASS  missing typed field → WARN, not ERROR")


def test_slug_mismatch_is_error():
    with tempfile.TemporaryDirectory() as d:
        write(os.path.join(d, "professors", "wrong-name.md"), GOOD_PROF)  # slug says jane-smith-mit
        issues = v.validate_kb(d)
        assert any("slug" in m for lv, _, m in issues if lv == "ERROR"), issues
    print("PASS  slug != filename → ERROR")


def test_bad_date_and_fit_score():
    with tempfile.TemporaryDirectory() as d:
        bad = GOOD_PROF.replace("fit_score: 84", "fit_score: 140")
        write(os.path.join(d, "professors", "jane-smith-mit.md"), bad)
        op = GOOD_OPENING.replace("deadline: 2026-12-01", "deadline: Dec 1 2026")
        write(os.path.join(d, "openings", "smith-lab-rl-2027.md"), op)
        issues = v.validate_kb(d)
        msgs = [m for lv, _, m in issues if lv == "ERROR"]
        assert any("fit_score" in m for m in msgs), issues
        assert any("deadline" in m for m in msgs), issues
    print("PASS  out-of-range fit_score and non-ISO date → ERROR")


def test_comment_only_value_parses_as_blank():
    # `key:   # hint` is a blank value in YAML, not the comment text — must not trip enums.
    fm = v.parse_front_matter("---\nemail_policy:   # welcomes-inquiry | unknown\nname: X\n---\n")
    assert fm["email_policy"] == "", fm
    assert fm["name"] == "X", fm
    # and a real value with a trailing comment keeps the value
    fm2 = v.parse_front_matter("---\nfunding: fully funded  # confirmed on page\n---\n")
    assert fm2["funding"] == "fully funded", fm2
    print("PASS  comment-only value parses as blank; trailing comment stripped")


def test_ranking_file_skipped():
    with tempfile.TemporaryDirectory() as d:
        # _ranking.md has no opening front-matter and must not be validated as an opening
        write(os.path.join(d, "openings", "_ranking.md"), "# Opportunity ranking\n| Rank |\n")
        issues = v.validate_kb(d)
        assert issues == [], issues
    print("PASS  openings/_ranking.md is not treated as an opening")


if __name__ == "__main__":
    test_clean_kb_has_no_errors()
    test_bad_enum_is_error()
    test_missing_typed_field_is_warn_not_error()
    test_slug_mismatch_is_error()
    test_bad_date_and_fit_score()
    test_comment_only_value_parses_as_blank()
    test_ranking_file_skipped()
    print("\nAll validate_kb tests passed.")
