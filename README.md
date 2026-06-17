# PhD Application Copilot

An AI skill suite that automates the slow, repetitive parts of applying for a PhD —
finding openings, analyzing professors, drafting outreach, tailoring materials, and
tracking deadlines — while keeping everything you send personal and authentic.

It is **field-agnostic**: your research area, target regions, and preferred sources are
configured once in `knowledge-base/profile/profile.md`, and the same skills work whether
you're applying in machine learning, molecular biology, or medieval history.

## How it works

The system is a set of focused **skills** that share a **knowledge base** of Markdown
files. Skills don't call each other; they read and write the same files (a "blackboard").
That makes every step inspectable and hand-editable, and the whole thing version-controlled.

```
skills/            the suite — each dir is one skill with a SKILL.md
knowledge-base/    your data: profile, professors, openings, applications, interactions
shared/schemas/    the agreed-upon shape of each knowledge-base file (+ validate_kb.py)
shared/references/ cross-cutting guidance: data sources, connectors, ethics
ARCHITECTURE.md    full design: skills, collaboration, data sources, roadmap
REPORT.md          what was built + how it was evaluated
```

## Quickstart

1. Fill in `knowledge-base/profile/profile.md` (who you are, what you want, where to look)
   and `profile/cv-master.md` (your full CV).
2. Ask Claude to analyze a professor — e.g. *"Do a deep dive on Prof. Jane Smith at MIT
   for fit with my background."* The **professor-analyzer** skill writes a profile to
   `knowledge-base/professors/`.
3. From there, draft outreach, rank opportunities, or tailor materials — each skill picks
   up the files the previous one wrote.

## The skills

All nine skills are implemented (each is a `SKILL.md` under `skills/`) and evaluated against
realistic prompts — see `REPORT.md` for the build and evaluation write-up.

| Skill | What it does |
|---|---|
| **phd-copilot** | front door: surveys the knowledge base and routes to the next best step |
| **position-discovery** | finds current, matching PhD openings → `openings/` |
| **professor-analyzer** | deep-dives a professor/lab and scores fit → `professors/` |
| **opportunity-ranker** | ranks openings on weighted, transparent dimensions → `openings/_ranking.md` |
| **outreach-email** | drafts grounded cold/follow-up emails (never sends) → `interactions/` |
| **research-proposal** | drafts a proposal at the lab's open problems → `applications/<id>/proposal.md` |
| **application-materials** | tailors CV / SOP / personal statement → `applications/<id>/` |
| **application-tracker** | surfaces what's overdue, due-soon, or missing across applications |
| **interview-prep** | generates likely questions + model answers → `applications/<id>/interview.md` |

Validate a knowledge base against the shared schemas at any time:

```
python3 shared/schemas/validate_kb.py knowledge-base
```

See `ARCHITECTURE.md` for the full design and rationale.
