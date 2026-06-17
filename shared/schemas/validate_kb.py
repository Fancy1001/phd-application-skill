#!/usr/bin/env python3
"""
validate_kb.py — check a knowledge-base directory against the schemas in README.md.

The knowledge base is the contract between skills (the blackboard). When a skill writes a
field with a value outside the agreed enum, or drops a key another skill reads, the break is
silent — the next skill just mis-routes. This validator makes those breaks loud.

It is dependency-free (stdlib only) so it runs anywhere the copilot does, and it only parses
the *scalar* front-matter keys it needs to check — it is not a full YAML parser.

Severity:
  ERROR  — actively wrong: an enum value not in the schema, a malformed date, a slug that
           disagrees with the filename, a core identity field missing. Exit code 1.
  WARN   — a recommended typed field is absent (often a record written before the schema was
           tightened). Exit code stays 0; the suite still works via prose fallback.

Usage:
    python3 validate_kb.py <kb-dir> [<kb-dir> ...]
    python3 validate_kb.py knowledge-base
    python3 validate_kb.py --strict knowledge-base   # treat WARN as failure too
"""
import argparse
import datetime
import glob
import os
import re
import sys

# --- enum / presence rules per entity, derived from shared/schemas/README.md ---------------
ENUMS = {
    "professor": {
        "funding_signal": {"strong", "mixed", "weak", "unknown"},
        "accepting_students": {"yes", "no", "unknown"},
        "admission_model": {"direct-to-advisor", "program-committee", "rotation", "unknown"},
        "email_policy": {"welcomes-inquiry", "do-not-email-admissions", "unknown"},
        "enrichment": {"openalex", "arxiv", "websearch", "none"},
    },
    "opening": {
        "funding": {"fully funded", "partial", "self-funded", "unknown"},
        "status": {"new", "shortlisted", "applied", "rejected", "offer", "declined"},
    },
    "institution": {
        "admission_model": {"direct-to-advisor", "program-committee", "rotation", "unknown"},
    },
    "application": {
        "stage": {"researching", "contacted", "replied", "applying", "submitted",
                  "interview", "decision"},
        "priority": {"high", "medium", "low"},
    },
    "profile": {
        "funding_required": {"true", "false"},
    },
}
# Core identity fields: missing => ERROR.
REQUIRED = {
    "professor": ["slug", "name", "field"],
    "opening": ["slug", "professor", "institution", "title", "status"],
    "institution": ["slug", "name"],
    "application": ["id", "stage"],
    "profile": ["name"],
}
# Typed fields skills parse: absent => WARN (prose fallback still works).
RECOMMENDED = {
    "professor": ["fit_score", "funding_signal", "accepting_students",
                  "admission_model", "email_policy", "enrichment"],
    "opening": ["funding", "deadline", "verified_on", "start_year"],
    "application": ["deadline", "priority"],
    "profile": ["field", "funding_required", "target_start"],
}
DATE_FIELDS = {"last_analyzed", "discovered", "verified_on", "deadline", "application_deadline"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_front_matter(text):
    """Return {key: raw_string_value} for top-level scalar keys in the leading --- block.

    Deliberately minimal: list values (``[a, b]``) and block scalars are returned as their raw
    string; we only need scalar enum/date/slug keys. Returns None if there is no front matter.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    body = text[3:end]
    fm = {}
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        # an unquoted value that is only a comment (`key:  # hint`) is a blank value in YAML
        if val.startswith("#"):
            val = ""
        else:
            # strip a trailing inline comment, then surrounding quotes/whitespace
            val = re.sub(r"\s+#.*$", "", val).strip().strip('"').strip("'")
        fm[key] = val
    return fm


def check_entity(path, entity, fm, slug_from_name=None):
    issues = []

    def add(level, msg):
        issues.append((level, path, msg))

    if fm is None:
        add("ERROR", "no YAML front-matter found")
        return issues

    for key in REQUIRED.get(entity, []):
        if key not in fm:
            add("ERROR", f"missing required key '{key}'")
    for key in RECOMMENDED.get(entity, []):
        if key not in fm:
            add("WARN", f"missing recommended typed field '{key}' (downstream skills parse it)")

    for key, allowed in ENUMS.get(entity, {}).items():
        if key in fm and fm[key] != "" and fm[key] not in allowed:
            add("ERROR", f"'{key}: {fm[key]}' not in {sorted(allowed)}")

    if entity == "professor" and "fit_score" in fm and fm["fit_score"] != "":
        try:
            n = int(fm["fit_score"])
            if not 0 <= n <= 100:
                add("ERROR", f"fit_score {n} out of range 0–100")
        except ValueError:
            add("ERROR", f"fit_score '{fm['fit_score']}' is not an integer")

    for key in DATE_FIELDS:
        if fm.get(key):
            if not DATE_RE.match(fm[key]):
                add("ERROR", f"'{key}: {fm[key]}' is not an ISO date (YYYY-MM-DD)")

    if slug_from_name and fm.get("slug") and fm["slug"] != slug_from_name:
        add("ERROR", f"slug '{fm['slug']}' != filename '{slug_from_name}'")

    return issues


def validate_kb(kb):
    issues = []

    def load(p):
        with open(p, encoding="utf-8") as f:
            return parse_front_matter(f.read())

    prof = os.path.join(kb, "profile", "profile.md")
    if os.path.exists(prof):
        issues += check_entity(prof, "profile", load(prof))

    for p in sorted(glob.glob(os.path.join(kb, "professors", "*.md"))):
        if os.path.basename(p).startswith("."):
            continue
        slug = os.path.splitext(os.path.basename(p))[0]
        issues += check_entity(p, "professor", load(p), slug_from_name=slug)

    for p in sorted(glob.glob(os.path.join(kb, "openings", "*.md"))):
        base = os.path.basename(p)
        if base.startswith(".") or base.startswith("_"):  # _ranking.md is not an opening
            continue
        slug = os.path.splitext(base)[0]
        issues += check_entity(p, "opening", load(p), slug_from_name=slug)

    for p in sorted(glob.glob(os.path.join(kb, "institutions", "*.md"))):
        if os.path.basename(p).startswith("."):
            continue
        issues += check_entity(p, "institution", load(p))

    for p in sorted(glob.glob(os.path.join(kb, "applications", "*", "status.md"))):
        issues += check_entity(p, "application", load(p))

    return issues


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("kb_dirs", nargs="+")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failure")
    args = ap.parse_args(argv)

    all_issues = []
    for kb in args.kb_dirs:
        all_issues += validate_kb(kb)

    errors = [i for i in all_issues if i[0] == "ERROR"]
    warns = [i for i in all_issues if i[0] == "WARN"]
    for level, path, msg in all_issues:
        print(f"{level}  {path}: {msg}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s).")
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
