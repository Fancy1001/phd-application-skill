---
name: professor-analyzer
description: >-
  Deep-dive a professor or research lab to assess PhD fit. Use this whenever the user
  wants to research, analyze, profile, or "look into" a potential PhD supervisor, advisor,
  faculty member, or lab — including questions like "is Prof X a good fit for me?", "what
  is this lab working on?", "analyze Professor Smith's recent work", "should I email this
  professor?", or when they paste a faculty page, Google Scholar link, or lab URL and want
  it understood. Gathers recent publications, grants, lab agenda, and open problems, then
  scores fit against the applicant's profile and surfaces concrete outreach hooks. Writes a
  structured profile to knowledge-base/professors/. Trigger even if the user doesn't say
  the word "analyze" — any intent to evaluate a specific researcher for PhD applications
  should use this skill.
---

# Professor / lab analyzer

This is the load-bearing skill of the PhD copilot: outreach emails, proposals, and ranking
all consume the profile it produces. The goal is a profile so specific that a cold email
built from it could only have been written to *this* professor — the opposite of generic.

## What you produce

A single file at `knowledge-base/professors/<slug>.md` following the **professor schema**
in `shared/schemas/README.md` (read it for the exact front-matter fields and section
headings). Match that shape exactly so downstream skills can parse it.

## Step 1 — Load context

Read `knowledge-base/profile/profile.md` (and `profile/cv-master.md` if fit detail is
needed). You cannot assess "fit" without knowing the applicant's interests, background, and
dealbreakers. Handle the applicant context in this order, so you never block unnecessarily:

1. If `profile.md` has real content, use it.
2. Otherwise, if the user's request itself describes their background and interests
   (e.g. "I work on sim-to-real RL, analyze Prof X"), use that as the working profile —
   don't stop to ask for what you've already been told.
3. Only if you have neither, ask the user for their research interests and background, since
   fit scoring is meaningless without them.

Identify the professor from the user's request: a name + institution, a homepage, a Scholar
profile, or a lab URL.

## Step 2 — Gather evidence

Follow the retrieval priority in `shared/references/connectors.md` — it defines which tool to
reach for and how to fall back cleanly. Prioritize *recency*: a PhD starts in 1–2 years, so
what matters is where the lab is heading, not its decade-old greatest hits. Ground every
later claim in a real source.

**Get the recent publications from a real index, not memory.** Run the bundled helper to
pull the professor's last ~3 years of work with abstracts:

```
python scripts/scholar_lookup.py "<Full Name>" --institution "<Institution>" --since <year>
```

It queries OpenAlex (falling back to arXiv) and returns titles, venues, years, DOIs, and
abstracts as JSON. If it prints a `NOTICE` that the API was unavailable or returns no works,
fall back to **WebSearch** (always available) and the browser tools for Google Scholar —
and note in the profile that structured-index enrichment was unavailable. Never fill the gap
by guessing publications from memory; an invented paper in an outreach email is fatal.

**Record where the evidence came from** in the `enrichment` front-matter field: `openalex` or
`arxiv` if the helper returned works, `websearch` if you fell back to search, `none` if you
could retrieve no real publication evidence at all (in which case say so plainly and treat the
whole profile as provisional — a profile with `enrichment: none` should not seed a confident
outreach email).

Then gather, roughly in priority order:

- **Recent publications (last ~3 years)** — from the helper / search above. For each, capture
  the *takeaway*: what problem, what approach, what's new. This is what makes hooks specific.
- **Lab website / "join us" / "prospective students" page.** Current projects, stated open
  problems, whether they're recruiting, funding mentions — and any **application process /
  contact rules** (see Step 2a).
- **Grants / funding signals.** Active grants suggest funded positions. Mark `unknown` when
  unclear — don't guess.
- **Research trajectory.** Read across the recent papers for the *direction*: what thread is
  the lab pulling on, what will the next few papers likely be about?

If a source can't be fetched, note the gap rather than fabricating around it.

### Step 2a — Capture the contact / application rules (downstream skills depend on this)

Actively look for how this professor wants to be approached. This is not optional polish:
**outreach-email** and **opportunity-ranker** branch on it, and getting it wrong wastes the
applicant's one shot. Record each rule in the **typed front-matter field** so downstream
skills can parse it without reading prose, and add any nuance to `## Notes`:

- **`email_policy`** — set `do-not-email-admissions` when the page/profile says not to email
  about admissions (many top labs do) and routes applicants to the program; `welcomes-inquiry`
  when brief intros are invited; `unknown` if the page is silent. In `## Notes`, capture the
  routing it implies ("apply to <program> and name me") and any **subject-line convention**.
- **`admission_model`** — `direct-to-advisor`, `program-committee`, `rotation`, or `unknown`.
- **`accepting_students`** — `yes` / `no` / `unknown` for the applicant's target year; note the
  year in `## Notes` if stated.

Set these to `unknown` rather than guessing when the source is silent — a wrong `welcomes-inquiry`
is worse than an honest `unknown`. When you find a hard rule (e.g. do-not-email), surface it in
your summary too: it changes whether outreach is even the right move.

## Step 3 — Assess fit

This is the part that makes the profile useful. Compare the professor's trajectory against
the applicant's profile and be honest and specific:

- **Overlaps** — concrete intersections between their open problems and the applicant's
  interests/skills. Name the paper and the matching part of the applicant's background.
- **Gaps** — where the applicant lacks relevant background, or the lab's direction diverges
  from their goals. Real assessment includes the misses.
- **fit_score (0–100)** — your overall judgment, justified by the overlaps/gaps above, not
  a vibe. Reserve 80+ for strong, well-evidenced matches.
- **Funding & "accepting students"** signals, set honestly to `unknown` when unclear.

## Step 4 — Outreach hooks

The payoff section. List 2–4 *specific* things the applicant could reference in a first
email: a particular recent paper and a genuine, substantive reaction or question; a
connection between one of their projects and the applicant's work; an open problem the
applicant is positioned to contribute to. These must be real and specific — they are what
separates an authentic email from spam. No flattery, no invented enthusiasm.

If Step 2a found that the professor doesn't take cold admissions emails, these hooks still
matter — note that they're best used in the **statement of purpose / program application**
(or a narrow, substantive research question) rather than a "please take me" cold email, so
the downstream skills route them correctly.

## Step 5 — Write the file

Write `knowledge-base/professors/<slug>.md` with **all** schema front-matter fields filled
(blank, not absent, when unknown) — including the typed `funding_signal`, `accepting_students`,
`admission_model`, `email_policy`, and `enrichment` fields the downstream skills read — and a
`## Sources` section with one link per claim-bearing source. Then give the user a short
summary: the fit verdict, the single strongest hook, and any gap they should be aware of. If
you found a clear opening, suggest the natural next step (e.g. drafting outreach).

## Guardrails

Follow `shared/references/ethics.md`. The cardinal rule: never invent a publication,
finding, grant, or shared interest. If you're unsure whether something is real, mark it
uncertain and cite what you actually found. A profile that honestly says "weak fit" is more
valuable than a flattering one that wastes the applicant's outreach on a bad match.
