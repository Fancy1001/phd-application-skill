---
name: opportunity-ranker
description: >-
  Rank, prioritize, or compare PhD opportunities by fit, funding, research impact, and
  admission probability so the applicant knows where to spend effort. Use this whenever the
  user wants to decide between or order multiple professors, labs, programs, or openings —
  e.g. "which of these should I apply to first?", "rank my options", "is it worth applying
  to this one?", "compare these three labs", "where are my best chances?", or "help me build
  a shortlist". Reads the professor profiles and openings already in the knowledge base,
  scores each on transparent weighted dimensions, and writes a ranked shortlist with
  per-item rationale to knowledge-base/openings/_ranking.md. Trigger whenever the intent is
  to prioritize among several PhD targets, even if the user doesn't use the word "rank".
---

# Opportunity ranker

The applicant has limited time and limited credible outreach. The value of this skill is
**focus**: turning a pile of openings and professor profiles into an honest, ordered
shortlist so the strongest, most-winnable opportunities get the best effort. The ranking is
only as trustworthy as it is transparent — a number with no reasoning behind it is useless,
so every score is explained.

## What you produce

`knowledge-base/openings/_ranking.md`: a ranked table plus a short rationale per item, so
the applicant sees *why* each opportunity sits where it does, not just an opaque ordering.

## Step 1 — Gather what you're ranking

Read `knowledge-base/profile/profile.md` (the applicant's interests, goals, constraints,
and crucially their dealbreakers — including the typed **`funding_required`** flag and
`target_start` year), then the candidates: `knowledge-base/professors/*.md` and
`knowledge-base/openings/*.md`. Reuse the typed signals professor-analyzer and
position-discovery already wrote rather than re-deriving them: the professor's `fit_score`,
`funding_signal`, `accepting_students`, `admission_model`, and `email_policy`; the opening's
`funding`, `deadline`, `start_year`, and `verified_on`.

If a candidate the user wants ranked has no profile yet, note it as "needs analysis" and
either rank it provisionally with low confidence or suggest running professor-analyzer
first. Don't silently invent the missing data — a confident ranking built on guesses is
worse than an honest "I can't rank this well yet".

## Step 2 — Score each opportunity

**First apply hard filters, then score what survives.** A dealbreaker removes a candidate
before scoring — it isn't a low score, it's out. In particular: if `funding_required: true`,
drop openings with `funding: self-funded` (and treat `unknown` funding as a flagged risk, not
a pass). Also flag — don't silently rank — any opening whose `deadline` has passed or whose
`verified_on`/`start_year` shows it's from a stale cycle; recommend re-verifying rather than
applying. Note each dropped candidate and why, so the applicant can override.

Score the survivors on these dimensions. They're weighted because they matter unequally, but
the weights are defaults you should adapt to what the applicant's profile says they care about.

| Dimension | Default weight | What it measures |
|---|---|---|
| **Fit** | 35% | Overlap between the lab's current/future agenda and the applicant's interests + skills. Use the professor profile's `fit_score`. |
| **Admission probability** | 25% | Realistic odds given the applicant's background vs. the opening's requirements and the lab/program selectivity. Be sober, not optimistic. |
| **Funding** | 20% | Funded vs. partial vs. unknown vs. self-funded. Honor dealbreakers. |
| **Research impact / environment** | 15% | Standing and trajectory of the lab/group and the quality of the research environment for the applicant's goals. |
| **Deadline urgency** | 5% | Soonest actionable deadlines get a nudge up so nothing winnable is missed. |

Compute a 0–100 composite. The weights are a tool for consistency, not a black box —
if a dimension is unknown, say so and reflect the uncertainty rather than scoring it as if
it were average.

### Admission probability — be honest

This is the dimension applicants most want sugar-coated and most need straight. A
world-class lab that's a perfect fit but takes one student a year from hundreds of
applicants is a long shot, and saying so lets the applicant balance reaches with realistic
targets. Weigh the applicant's concrete record (publications, relevant experience, fit of
background to requirements) against the opening's selectivity. Frame it as odds and reasons,
never as a verdict on the applicant's worth.

## Step 3 — Write the ranking

Write `knowledge-base/openings/_ranking.md`:

```markdown
# Opportunity ranking — <date>

| Rank | Opportunity | Composite | Fit | Admission | Funding | Impact | Why |
|------|-------------|-----------|-----|-----------|---------|--------|-----|
| 1 | Smith Lab (MIT) — RL robotics | 84 | 88 | 70 | strong | high | ... |
...

## Rationale
### 1. Smith Lab (MIT)
2–3 sentences: why it ranks here, the key strength, the main risk, and the recommended
move (e.g. "reach — apply but pair with safer targets").

## Portfolio note
A short read on the shortlist as a whole: is it all reaches? all safe? Suggest balance.
```

The **portfolio note** is important — applicants often over-index on a few dream labs. Point
out when the shortlist needs a realistic anchor or could use more ambition.

## Step 4 — Report and hand off

Summarize the top few and the portfolio shape for the user. Then suggest next actions on
the leaders: draft outreach with **outreach-email**, tailor materials with
**application-materials**, or analyze any "needs analysis" candidates first.

## Guardrails

Per `shared/references/ethics.md`: the ranking exists to direct effort wisely, not to
encourage mass applications. Favor a focused shortlist over a long one. Be transparent about
missing data and honest about admission odds — false optimism wastes the applicant's scarce
time and outreach credibility. Never present a guessed score as if it were grounded.
