# Knowledge-base schemas

Every skill reads and writes the knowledge base, so the files need a shared shape.
Each schema below is the YAML front-matter + section layout for one entity type. Skills
should treat these as the contract: write all the fields, leave a field blank (not absent)
when unknown, and keep the Markdown section headings stable so other skills can find them.

Slugs are lowercase-kebab (`jane-smith-mit`). Dates are ISO (`2026-06-12`).

## Conventions (read once, apply everywhere)

- **Enumerated fields** (marked with a `# a | b | c` comment) must hold exactly one of the
  listed values, or be left blank when unknown. Don't invent new values — downstream skills
  branch on these, so a typo silently breaks routing. `unknown` is always a valid value for
  an enum and is the honest default; never guess to fill it.
- **Blank, not absent.** When a value isn't known, keep the key with an empty value rather
  than deleting it, so every file has the same keys and a reader can tell "unknown" from
  "forgot to write it".
- **Provenance & currency.** Evidence-gathering skills record *where* a claim came from and
  *when* it was checked (the `enrichment`, `verified_on`, and `## Sources` fields below).
  A downstream skill can then judge how much to trust a record and whether it's gone stale.
- **Typed field wins, prose is the fallback.** Several rules that used to live only in prose
  (a professor's email policy, the admission model, whether funding is required) now have a
  dedicated front-matter field so other skills can parse them reliably. A reader should use
  the typed field when it's set and fall back to the relevant prose section only when it's blank.
- Validate any knowledge base against these schemas with
  `python3 shared/schemas/validate_kb.py <kb-dir>` (see that script for the exact checks).

---

## professor (`knowledge-base/professors/<slug>.md`)

```yaml
---
slug: jane-smith-mit
name: Jane Smith
title: Associate Professor
institution: MIT
department: EECS
lab: Smith Lab
homepage:
scholar:
email:
field: machine learning
last_analyzed: 2026-06-12
fit_score:          # 0–100, set by professor-analyzer; reserve 80+ for strong, evidenced fit
funding_signal:     # strong | mixed | weak | unknown — likelihood a funded position exists
accepting_students: # yes | no | unknown — recruiting status for the applicant's target year
admission_model:    # direct-to-advisor | program-committee | rotation | unknown
email_policy:       # welcomes-inquiry | do-not-email-admissions | unknown
enrichment:         # openalex | arxiv | websearch | none — where the publication evidence came from
---
```

The three lower fields make the **contact / application rules** machine-readable so
`outreach-email` and `opportunity-ranker` don't have to guess from prose:

- `admission_model` — how students are admitted. `direct-to-advisor`: the professor picks; a
  cold email can matter. `program-committee` / `rotation`: a central committee decides, so
  effort belongs in the application, not the inbox.
- `email_policy` — `do-not-email-admissions` when the page/profile says not to email about
  admissions (common at top labs); `welcomes-inquiry` when brief intros are invited;
  `unknown` otherwise. `outreach-email` must check this before drafting a cold email.
- `enrichment` — the source of the publication list, so a reader knows the provenance:
  `openalex`/`arxiv` (structured index), `websearch` (grounded fallback), `none` (no evidence
  retrieved — treat the profile as provisional).

Body sections (stable headings):
`## Research focus` · `## Recent publications` (last ~3 yrs, with takeaways) ·
`## Research agenda & open problems` · `## Funding & grants` · `## Fit with my profile`
(specific overlaps + gaps) · `## Outreach hooks` (concrete things to reference in an email) ·
`## Notes` (contact protocol, subject conventions, anything not captured above) ·
`## Sources` (links — one per claim-bearing source).

---

## opening (`knowledge-base/openings/<slug>.md`)

```yaml
---
slug: smith-lab-rl-2026
professor: jane-smith-mit
institution: MIT
title: PhD in reinforcement learning for robotics
source_url:
discovered: 2026-06-12
verified_on:        # ISO date the listing was last confirmed current at source_url
deadline:
start_year:         # target intake year, e.g. 2027 — lets the ranker drop stale cycles
funding: # fully funded | partial | self-funded | unknown
status: # new | shortlisted | applied | rejected | offer | declined
---
```

`verified_on` is the currency stamp: position-discovery sets it to the date it confirmed the
opening is live at `source_url`. A reader (or the ranker) treats an opening whose
`verified_on` is far in the past — or whose `deadline` has passed — as stale and to re-check,
rather than acting on it blindly. `self-funded` is a distinct funding value (not "partial")
so a funding-required applicant's filter can drop it cleanly.

Body: `## Description` · `## Requirements` · `## Why it fits` · `## Notes`.

---

## institution (`knowledge-base/institutions/<slug>.md`)

```yaml
---
slug: mit
name: Massachusetts Institute of Technology
country: USA
admission_model: # direct-to-advisor | program-committee | rotation | unknown
gre_required:
english_test:
application_deadline:
funding_model:
---
```

Body: `## Program requirements` · `## Funding` · `## Notes`.

---

## application (`knowledge-base/applications/<id>/status.md`)

`<id>` is `<professor-slug>` or `<institution>-<program>`.

```yaml
---
id: jane-smith-mit
opening: smith-lab-rl-2026
professor: jane-smith-mit
institution: mit
stage: # researching | contacted | replied | applying | submitted | interview | decision
deadline:
priority: # high | medium | low
---
```

Body: `## Checklist` (documents needed + done/pending) · `## Timeline` · `## Notes`.
Companion files in the same folder: `proposal.md`, `sop.md`, `cv.md`, `interview.md`.

---

## interaction log (`knowledge-base/interactions/<professor-slug>.md`)

A reverse-chronological log. Each entry:

```markdown
### 2026-06-12 — sent: cold email
Subject: ...
Summary: ...
Follow-up due: 2026-06-26
Status: awaiting reply
```

---

## profile (`knowledge-base/profile/profile.md`)

```yaml
---
name: Alex Kim          # example applicant
field:
subfields: []
degree_seeking: PhD
target_regions: []
target_start: 2027
funding_required:  # true | false — true means an unfunded/self-funded position is a dealbreaker
sources: []        # which boards/databases to search
constraints: []    # location, visa, two-body, etc. (free text; funding has its own typed field)
---
```

`funding_required` lifts the single most common dealbreaker out of free-text `constraints`
into a typed field, so position-discovery and opportunity-ranker can apply it as a hard filter
rather than parsing prose. Keep any nuance ("would consider self-funded if topic is perfect")
in `## Dealbreakers`; the boolean is the machine-checkable default.

Body: `## Research interests` · `## Background` · `## Goals` · `## Dealbreakers`.
