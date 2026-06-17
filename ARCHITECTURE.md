# PhD Application Copilot — System Architecture

An AI skill suite that automates the research-intensive and administrative work of
applying for PhD positions, while keeping every outward-facing artifact (emails,
proposals, statements) personal and academically authentic.

The design philosophy is deliberately **human-in-the-loop**: the system does the
searching, reading, drafting, and tracking, but the applicant approves anything that
gets sent or submitted. Authenticity is a feature, not an afterthought — admissions
committees and professors are good at spotting generic AI text, so every drafting
skill is built to ground its output in *your* real background and *their* real work.

---

## 1. Why a skill suite (not one mega-skill or one agent)

The work breaks cleanly into distinct competencies that trigger at different times and
consume different inputs. A professor deep-dive needs publication search; a tracker
needs your calendar and a status file; an email draft needs both a professor profile
and your CV. Bundling these into one giant skill would blow past the ~500-line budget
and force every invocation to load instructions it doesn't need.

Instead, each competency is its own skill with a focused description, and they
collaborate through a **shared knowledge base** of plain Markdown + YAML files. One
skill writes a professor profile; another reads it to draft an email. The files are the
contract between skills — readable by you, versionable in git, and editable by hand.

```
                         ┌─────────────────────┐
                         │     phd-copilot     │  orchestrator / router
                         │  (intent → skills)  │
                         └──────────┬──────────┘
                                    │ reads & writes
                        ┌───────────▼────────────┐
                        │     knowledge-base/     │  shared state (MD + YAML)
                        │  profile, professors,   │
                        │  openings, applications │
                        └───────────▲────────────┘
                                    │
   ┌──────────────┬─────────────┬───┴─────────┬──────────────┬──────────────┐
   ▼              ▼             ▼             ▼              ▼              ▼
position-     professor-   opportunity-   outreach-    research-     application-
discovery     analyzer     ranker         email        proposal      materials
   │              │             │             │              │              │
   └──────────────┴─────────────┴─────────────┴──────────────┴──────────────┘
                                    ▼
                       application-tracker   interview-prep
```

---

## 2. The skills

Each lives under `skills/<name>/` with its own `SKILL.md`, plus optional
`references/`, `scripts/`, and `assets/`.

| Skill | Triggers when you want to… | Reads | Writes |
|---|---|---|---|
| **phd-copilot** | "help me apply for PhDs", run the whole pipeline, or you're unsure which step you're on | everything | routes to others |
| **position-discovery** | find open PhD positions / funded projects matching your profile | `profile/` | `openings/` |
| **professor-analyzer** | deep-dive a professor or lab: publications, grants, agenda, fit | `profile/`, web | `professors/` |
| **opportunity-ranker** | rank/compare openings by fit, funding, impact, admission odds | `professors/`, `openings/`, `profile/` | `openings/_ranking.md` |
| **outreach-email** | draft a cold email or a follow-up to a professor | `professors/`, `profile/`, `interactions/` | drafts + `interactions/` |
| **research-proposal** | write a proposal aligned to a lab's current & future agenda | `professors/`, `profile/` | `applications/<id>/proposal.md` |
| **application-materials** | tailor CV, SOP, personal statement for a specific opportunity | `profile/`, `professors/`, `applications/` | `applications/<id>/` |
| **application-tracker** | track deadlines, status, documents, follow-up timing | `applications/`, `interactions/` | `applications/`, reminders |
| **interview-prep** | generate likely questions + model answers for a faculty interview | `professors/`, `applications/`, `profile/` | `applications/<id>/interview.md` |

### How they collaborate

The collaboration pattern is **blackboard, not message-passing**: skills don't call each
other directly, they read and write shared files. This keeps each skill independently
testable and means a half-finished pipeline is just a set of files you can inspect.

A typical end-to-end flow:

1. **position-discovery** sweeps sources → writes candidate openings to `openings/`.
2. **professor-analyzer** runs on the professors behind the promising openings →
   writes a structured profile + fit assessment per professor.
3. **opportunity-ranker** reads all profiles + openings → produces a ranked shortlist.
4. For each top opportunity: **outreach-email** drafts a cold email grounded in the
   professor's recent work; **application-materials** tailors the CV/SOP; **research-proposal**
   drafts a proposal if required.
5. **application-tracker** records what was sent, sets follow-up dates, watches deadlines.
6. **interview-prep** activates once an interview is scheduled.

`phd-copilot` is the front door for users who don't know which skill they need — it reads
the knowledge base to see what stage each opportunity is at and suggests the next action.

---

## 3. Knowledge base (shared state)

Plain Markdown with YAML front-matter. Human-readable, git-versioned, hand-editable. One
entity per file so diffs stay meaningful and skills can lock onto a single record.

```
knowledge-base/
├── profile/
│   ├── profile.md              # who you are: research interests, goals, constraints
│   ├── cv-master.md            # master CV — superset of everything, tailored down per app
│   ├── research-statement.md   # your core research narrative (reused across SOPs)
│   └── recommenders.md         # referees, their relationship to you, what they can speak to
├── professors/
│   └── <slug>.md               # one per professor: profile, publications, agenda, fit score
├── institutions/
│   └── <slug>.md               # program requirements, funding model, deadlines, notes
├── openings/
│   ├── <slug>.md               # a specific advertised/inferred opening
│   └── _ranking.md             # ranker output: the live shortlist
├── applications/
│   └── <id>/                   # one folder per application you're pursuing
│       ├── status.md           # stage, checklist, deadlines, documents
│       ├── proposal.md
│       ├── sop.md
│       ├── cv.md
│       └── interview.md
├── interactions/
│   └── <professor-slug>.md     # dated log of every email sent/received + follow-up status
└── templates/                  # your reusable scaffolds (email tone, SOP skeleton)
```

The exact field schemas live in `shared/schemas/` so every skill writes the same shape.
See `shared/schemas/README.md`. Contact/application rules that downstream skills branch on —
a professor's `email_policy` and `admission_model`, an opening's `funding` and `verified_on`
currency stamp, the applicant's `funding_required` flag — are **typed front-matter fields**, not
prose, so a reader parses them reliably (with prose as a fallback). Any knowledge base can be
checked against the schemas with `python3 shared/schemas/validate_kb.py <kb-dir>`.

---

## 4. Data sources & tools

Field-agnostic by design — the specific sources are configured in `profile/profile.md`
so the same skills work for CS, bioscience, or the humanities. Categories the skills know
how to use:

- **Publication search**: web search + (where available) connectors for arXiv, Google
  Scholar, OpenReview, PubMed, Semantic Scholar, OpenAlex, CrossRef. Used heavily by
  *professor-analyzer*.
- **Position boards**: FindAPhD, EURAXESS, jobs.ac.uk, university department pages,
  lab "join us" pages, field-specific mailing lists. Used by *position-discovery*.
- **Funding databases**: program pages, national funding schemes (configured per region).
- **Web fetch / browser**: lab websites, faculty pages, Google Scholar profiles — for
  pages that need rendering, the browser tools; otherwise web fetch.
- **Your accounts** (optional connectors): email (send/track outreach + follow-ups),
  calendar (deadlines, interviews), a document store for transcripts and writing samples.
- **Output skills**: `docx` / `pdf` for submission-ready CVs and statements, `xlsx` for an
  optional deadline tracker export.

When a source needs an MCP connector that isn't installed, the relevant skill should
surface that to you rather than silently failing.

---

## 5. Authenticity & ethics guardrails

These are baked into the drafting skills, not bolted on:

- **Ground everything in real material.** Emails cite the professor's actual recent papers;
  proposals build on their stated open problems; statements draw only from your real CV.
  No invented achievements, no fabricated shared interests.
- **Draft, never auto-send.** Every email and submission is produced as a draft for your
  review. The tracker can *schedule* a follow-up but you approve the send.
- **You are the author.** Output is a strong first draft in your voice, meant to be edited.
  The skills flag where you must add specifics only you know.
- **Respect the other side's time.** The ranker discourages spray-and-pray mass outreach;
  it pushes toward fewer, better-targeted contacts.
- **No misrepresentation.** Tailoring a CV means selecting and ordering true facts for
  relevance — never inflating them.

---

## 6. Implementation roadmap

**Phase 1 — Foundation (now).** Repo scaffold, knowledge-base schemas, user profile, and
the first and most load-bearing skill: **professor-analyzer** (every downstream skill
consumes its output). Build, write test cases, evaluate, iterate via skill-creator.

**Phase 2 — Discovery & ranking.** *position-discovery* and *opportunity-ranker* so the
pipeline can find and prioritize opportunities, feeding the analyzer.

**Phase 3 — Outreach.** *outreach-email* (cold + follow-up) and *application-tracker* —
the highest day-to-day time savings.

**Phase 4 — Heavy writing.** *research-proposal* and *application-materials* (CV/SOP/PS
tailoring), leaning on the docx/pdf skills for submission-grade output.

**Phase 5 — Orchestration & interview.** *phd-copilot* router and *interview-prep*, plus
scheduled tasks for recurring discovery sweeps and follow-up reminders.

Each phase: draft the skill → 2–3 realistic test prompts → run with/without skill →
review outputs → iterate → optimize the trigger description → package.

---

## 7. Repository layout

```
phd-application-skill/
├── ARCHITECTURE.md            # this file
├── README.md                  # quickstart + how the pieces fit
├── skills/                    # the skill suite (one dir per skill)
├── knowledge-base/            # shared state (your data lives here)
└── shared/
    ├── schemas/               # YAML field definitions every skill writes to
    └── references/            # cross-cutting guidance (data sources, ethics)
```
