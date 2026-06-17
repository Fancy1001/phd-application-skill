# PhD Application Copilot — Build Report

**Status:** Phases 1–5 complete. All nine skills implemented and evaluated.
professor-analyzer iterated to v2; scholarly data-source layer added.
**Date:** 2026-06-13
**Repository:** `phd-application-skill/`

---

## 1. What was built

An AI skill suite that automates the research-intensive and administrative work of applying
for PhD positions — discovery, professor analysis, ranking, outreach, proposals, materials,
tracking, interview prep — coordinated by an orchestrator skill, all sharing a single
Markdown knowledge base. The system is field-agnostic (configured per applicant) and built
on a human-in-the-loop principle: it researches, drafts, and tracks, but the applicant
approves anything sent or submitted.

Nine skills were delivered across five phases:

| Phase | Skills | Role |
|---|---|---|
| 1 | professor-analyzer | Deep-dive a professor/lab; the load-bearing skill all others consume |
| 2 | position-discovery, opportunity-ranker | Find and prioritize opportunities |
| 3 | outreach-email, application-tracker | Cold/follow-up emails; deadline & status management |
| 4 | research-proposal, application-materials | Proposals; CV/SOP/personal-statement tailoring |
| 5 | phd-copilot, interview-prep | End-to-end orchestration; interview readiness |

---

## 2. Architecture

### Design choice: a skill suite over a mega-skill or single agent

The work breaks into distinct competencies that trigger at different times and need
different inputs. Bundling them into one skill would exceed the practical instruction budget
and force every invocation to load instructions it doesn't need. Each competency is therefore
its own skill with a focused trigger description.

### Collaboration: a blackboard, not message-passing

Skills do not call each other directly. They read and write a shared **knowledge base** of
plain Markdown + YAML files. One skill (professor-analyzer) writes a professor profile;
another (outreach-email) reads it to draft a message. The files are the contract between
skills. This makes each skill independently testable, keeps a half-finished pipeline
inspectable as a set of files, and gives the applicant a human-readable, git-versioned record
they can hand-edit.

```
position-discovery → professor-analyzer → opportunity-ranker → outreach-email
       → research-proposal / application-materials → application-tracker → interview-prep
                                  ▲
                          phd-copilot (orchestrator: surveys state, routes to the next step)
```

### Knowledge base layout

```
knowledge-base/
├── profile/         applicant: profile.md, cv-master.md, research-statement.md, recommenders.md
├── professors/      one file per professor (profile + fit assessment)
├── institutions/    program requirements, funding model, deadlines
├── openings/        discovered opportunities + _ranking.md shortlist
├── applications/    one folder per application (status.md, proposal.md, sop.md, cv.md, interview.md)
├── interactions/    dated email log per professor, with follow-up dates
└── templates/       reusable scaffolds
```

Field schemas are defined once in `shared/schemas/README.md` so every skill writes the same
shape. Cross-cutting guidance lives in `shared/references/` (`data-sources.md`, `ethics.md`).

### Authenticity guardrails (built into every drafting skill)

A central design concern: admissions committees and professors detect generic AI text, so
authenticity is enforced, not optional. Every drafting skill is bound to
`shared/references/ethics.md`:

1. **Ground in real material** — emails cite the professor's actual recent papers; proposals
   build on their stated open problems; statements draw only from the applicant's real CV.
2. **Draft, never auto-send** — the applicant reviews and sends everything themselves.
3. **The applicant is the author** — output is a first draft in their voice; `[brackets]`
   mark specifics only they can supply.
4. **No misrepresentation** — tailoring selects and orders true facts; it never inflates.
5. **Respect the reader's time** — favor focused outreach over mass applications.

---

## 3. The skills

**professor-analyzer** — Gathers a professor's recent publications (with takeaways), research
agenda and open problems, and funding signals, then scores fit (0–100) against the applicant
and surfaces concrete outreach hooks. Writes a schema-conformant profile that every
downstream skill consumes. The load-bearing skill of the suite.

**position-discovery** — Turns a broad wish ("find PhD positions in X") into specific,
verified, current openings, one schema file each. Handles both advertised/funded boards
(FindAPhD, EURAXESS) and US direct-to-advisor signals (labs whose pages indicate recruiting).
Verifies currency before recording; drops expired listings rather than fabricating.

**opportunity-ranker** — Scores opportunities on transparent weighted dimensions (fit 35%,
admission probability 25%, funding 20%, impact 15%, deadline 5%), honors dealbreakers, and
produces a ranked shortlist with per-item rationale and a portfolio-balance note. Designed
to resist blindly sorting by fit score.

**outreach-email** — Drafts cold emails and follow-ups grounded in the professor profile's
real hooks, in the applicant's voice, ~120–200 words. Detects prior contact (follow-up vs.
cold) and surfaces constraints (e.g. "don't email about admissions"). Logs every contact with
a follow-up date; never sends.

**application-tracker** — Reads all application status files and interaction logs, sorts state
into urgency buckets (overdue / due-soon / missing-docs / waiting-on-others / on-track), and
delivers a prioritized action digest. Computes dates against today; invents nothing.

**research-proposal** — Drafts a proposal at the intersection of the lab's open problems and
the applicant's credible strengths, with a full structure (motivation, related work, proposed
research, methods/feasibility, risks/alternatives, fit). Cites real papers; flags
applicant-only specifics.

**application-materials** — Tailors CV, SOP, and personal statement for a specific target by
selecting, ordering, and emphasizing true material — never inventing. Aligns voice across
documents so an application tells one coherent story.

**interview-prep** — Generates likely questions across the categories a real PhD interview
spans (motivation/fit, the applicant's own work, the proposed research, technical depth,
behavioral, questions to ask back), each with a model answer and a coaching note, grounded in
the specific professor's work. Offers an interactive mock.

**phd-copilot** — The front door. Surveys the knowledge base to see what stage each
opportunity is at, diagnoses the highest-leverage next action, and routes to the matching
skill — for users who know they want help but not which step they need.

---

## 4. Evaluation methodology

Each skill was built and tested with the skill-creator loop: write the skill, run realistic
test prompts **with the skill** against a **baseline** (the same prompt with no skill), grade
both against objective assertions, and review the actual outputs.

- **Test cases**: 14 across the 9 skills — realistic prompts a real applicant would type.
- **Grounding**: discovery and analysis skills ran live web search against real professors
  (Levine, Doudna, Fei-Fei Li) and real boards. Skills that need existing state
  (ranker, tracker, proposal, materials, interview-prep, copilot) ran against purpose-built
  **fixture knowledge bases** with applications at varied stages.
- **Assertions**: objective, programmatically checked where possible (schema conformance,
  presence of required sections, honest fit scores, no fabrication, correct prioritization).
- **Review**: every artifact is persisted under `skills/<skill>-workspace/` — `benchmark.json`
  / `benchmark.md` (the quantitative comparison), per-eval `grading.json` (assertion-level
  pass/fail), the generated `outputs/`, and `timing.json`. The benchmark summaries are
  *derived* from the per-run grading/timing files by `tools/build_benchmark.py` (so they can't
  drift from the raw results) and validated by `tools/test_build_benchmark.py`.

All of these persist in the repository for inspection.

---

## 5. Results

| Skill | Test cases | With skill | Baseline | Δ | Note |
|---|---|---|---|---|---|
| professor-analyzer (v1) | 3 | 100% | 60% | **+40** | Largest lift — schema, fit score, sources, honesty |
| professor-analyzer (v2 vs v1) | 3 | 100% | 81% | +19 | Contact-rule capture, SOP-routing, grounded retrieval |
| position-discovery | 2 | 100% | 83% | +17 | Per-opening schema files vs. prose blob; currency honesty |
| opportunity-ranker | 1 | 100% | 83% | +17 | Resisted fit-only sort; portfolio note |
| outreach-email | 2 | 100% | 82% | +18 | Interaction logging; constraint surfacing; draft-not-send |
| application-tracker | 1 | 100% | 83% | +17 | Urgency bucketing; recurring-digest offer |
| research-proposal | 1 | 100% | 100% | +0 | Tied — strong context yields strong output either way |
| application-materials | 1 | 100% | 100% | +0 | Tied (see §6) |
| interview-prep | 1 | 83% | 67% | +16 | Full category coverage vs. partial |
| phd-copilot | 1 | 100% | 100% | +0 | Tied — both diagnosed the right next action |

**Headline:** every with-skill configuration met or beat its baseline; none regressed. The
professor-analyzer lift is large (+40) because the skill enforces structured, parseable
output and honest fit assessment that an unguided model skips. The mid-pipeline skills show
steady ~+17 lifts driven by *system behavior* — structured files, interaction logging, and
guardrail surfacing — rather than prose quality.

### Notable qualitative wins

- **Honesty under pressure (professor-analyzer).** Asked to evaluate Fei-Fei Li for a
  multilingual-NLP applicant, the skill returned a fit score of 12/100 and named the
  computer-vision-vs-NLP divergence rather than fabricating overlap — the intended behavior.
- **Currency discipline (position-discovery).** Both runs recognized that genuine 2027-start
  adverts barely exist yet, dropped an expired 2023 listing and a filled 2025 one, and
  excluded self-funded positions against a funding requirement — instead of inventing
  deadlines.
- **Constraint handling (outreach-email).** Targeting a professor whose profile says "don't
  email about admissions," the skill surfaced the constraint first and reframed toward a
  program application rather than producing a naive cold email.
- **Prioritization (application-tracker / phd-copilot).** Given five applications, both
  skills led with the single overdue item, and the copilot correctly treated an overdue
  follow-up to a "do-not-email" professor as *expected silence*, not a failure.

---

## 6. Honest limitations & reading of the results

- **Phase 4–5 deltas are near zero.** research-proposal, application-materials, and
  phd-copilot tied their baselines at 100%. With a rich fixture knowledge base, a capable
  model produces strong proposals, SOPs, and status overviews unprompted. The skills' value
  there is not "can the model do it at all" but *consistency and integration*: writing to the
  right knowledge-base paths, aligning voice across an application's documents, enforcing
  draft-never-send, and using the same schema every time so the next skill can parse it.
  These compound across the pipeline but are hard to capture in a single one-shot binary
  assertion.

- **Grading is file-scoped.** Assertions check the saved artifacts. In one case
  (interview-prep), the skill offered an interactive mock in its chat message rather than the
  file, so the file-based assertion under-counted it. This is a measurement artifact, not a
  behavior gap.

- **One assertion was a wording false-negative** (application-materials "SOP arc"): the
  regex looked for the literal word "why" while the SOP expressed why-this-lab differently.
  It was corrected to check the reasoning rather than the keyword.

- **Single-run benchmarks.** Each configuration was run **once per test case**, so the ± in
  the benchmark summaries is the spread *across the distinct eval cases*, not run-to-run
  variance (which is unmeasured). This is enough to validate behavior and direction; repeated
  runs per case would let us estimate variance. The `runs_per_configuration` field is `1`
  accordingly, and per-run token counts come from each run's own `timing.json`; tool-call
  counts were not captured by the harness and are recorded as `null` rather than `0`.

- **Live-search dependence.** Discovery and analysis quality depends on what the web surfaces
  at run time and on which connectors (arXiv, Scholar, PubMed, position boards) are
  available. Missing connectors degrade coverage; the skills are instructed to surface that
  rather than fail silently.

---

## 6a. Iteration 2 — professor-analyzer + the data-source layer

After the first pass, professor-analyzer (the load-bearing skill) was iterated and a real
retrieval layer was added.

**Connector / data-source layer (`shared/references/connectors.md` +
`skills/professor-analyzer/scripts/scholar_lookup.py`).** The MCP registry currently has no
dedicated academic or position-board connectors, so the layer is built on what's reliably
available, in a defined priority with clean fallback: a dedicated MCP connector *if installed*
→ free scholarly APIs (OpenAlex/arXiv/Crossref/Semantic Scholar/Europe PMC) via `web_fetch`
→ **WebSearch** (always available) → Chrome browser tools for JS-rendered pages. The bundled
`scholar_lookup.py` resolves an author on OpenAlex and pulls their last ~3 years of works with
reconstructed abstracts, falling back to arXiv, and on any network failure prints a NOTICE and
exits non-zero so the skill falls back to WebSearch rather than inventing data.

**Three targeted fixes to professor-analyzer:** (1) grounded retrieval — pull recent papers
from a real index via the helper instead of from memory; (2) **Step 2a** — actively capture
the professor's contact / application rules (do-not-email, program-vs-direct admission,
subject conventions) in the profile, because outreach-email and opportunity-ranker depend on
it; (3) smarter empty-profile handling — use the in-request background when the profile file
is blank instead of stopping to ask.

**Result: v2 100% vs v1 81% (+19) across the same three evals.** The v1 misses were exactly
the targeted dimensions — contact-rule capture (Levine, Fei-Fei Li) and SOP-routing of hooks
when cold email is discouraged. Empty-profile handling worked: no run stalled to ask for
background it already had.

**A real-world note on the data layer.** In the test sandbox the scholarly APIs were not on
the network allowlist, so the helper failed and every run fell back to WebSearch — which is
the designed behavior and produced grounded, non-fabricated profiles. In an environment where
those API hosts are reachable, the helper adds DOI-level, abstract-rich publication data on
top.

**Validation outcome.** Attempting live validation in this environment confirmed the APIs are
unreachable through *every* available channel here — the bash sandbox allowlist returns 403,
`web_fetch` returns empty for JSON endpoints, and no browser is connected — so a live call
could not be made from here. The validation was therefore done two ways that don't depend on
network: (1) the lookup's `--dry-run` confirms it builds correct OpenAlex/arXiv URLs, and (2)
a new offline test (`scripts/test_scholar_lookup.py`) mocks the network and validates the
parser against **realistic OpenAlex and arXiv payloads** — author resolution, institution
disambiguation, abstract reconstruction, null-field handling, arXiv Atom parsing, and the
empty-result fallback all pass. Validation also surfaced and fixed a real bug: OpenAlex
deprecated the singular `last_known_institution` (object) in favor of
`last_known_institutions` (list); the lookup now supports both. A one-line **live check** for a
network-enabled environment is documented in `connectors.md`.

## 7. Recommended next steps

1. **Iterate where it counts.** *(Done for professor-analyzer — see §6a.)* Apply the same
   pattern to the next-highest-leverage skills (outreach-email, opportunity-ranker).
2. **Wire up real connectors.** *(Foundation laid — see §6a.)* The data-source layer and
   `scholar_lookup.py` are in place with WebSearch fallback. Next: validate the scholarly-API
   path in the deployment environment, and add a dedicated MCP connector at priority 1 if one
   becomes available (arXiv / Semantic Scholar / OpenAlex / PubMed / position boards).
3. **Schedule recurring sweeps.** position-discovery and application-tracker are natural
   recurring tasks (weekly discovery; Monday status digest) via scheduled tasks.
4. **Optimize trigger descriptions.** Run the description-optimization loop so each skill
   fires reliably on real phrasings without over-triggering on adjacent requests.
5. **Expand the test set.** More test cases per skill and repeated runs to measure variance,
   plus end-to-end tests that chain skills through the knowledge base.
6. **Package and install.** Bundle the suite (optionally as a Cowork plugin) so the applicant
   can install and run it directly.

---

## 8. Repository map

```
phd-application-skill/
├── ARCHITECTURE.md            full design rationale
├── README.md                  quickstart + build status
├── REPORT.md                  this report
├── skills/
│   ├── <skill>/SKILL.md       the nine skills
│   └── <skill>-workspace/     saved eval artifacts (benchmarks, grading, outputs, timing)
├── knowledge-base/            applicant data (profile templates + entity folders)
├── tools/                     build_benchmark.py (+ test) — derives honest benchmark summaries
└── shared/
    ├── schemas/               README.md (field definitions) + validate_kb.py (+ test)
    └── references/            data-sources.md, connectors.md, ethics.md
```

Per-skill benchmarks and generated outputs are persisted under each
`skills/<skill>-workspace/` directory.
