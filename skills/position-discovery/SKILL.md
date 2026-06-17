---
name: position-discovery
description: >-
  Find open PhD positions, funded studentships, fellowships, or labs actively recruiting
  students that match the applicant's profile. Use this whenever the user wants to discover,
  search for, find, or surface PhD opportunities — e.g. "find me PhD positions in NLP in
  Europe", "any funded studentships in computational biology?", "what programs should I be
  looking at?", "search for open PhD spots with professors working on diffusion models", or
  "are there openings in these three departments?". Sweeps position boards, department and
  lab pages, and funding databases, filters by the applicant's field/region/constraints,
  de-duplicates, and writes structured opening records to knowledge-base/openings/. Trigger
  even when the user names a board, a region, or a topic instead of saying "position" — any
  intent to locate PhD opportunities to apply to should use this skill.
---

# Position discovery

The job of this skill is to turn a broad wish ("find me PhD positions in X") into a small
set of **specific, real, current openings** the applicant can act on — each captured as a
file the rest of the copilot can consume. Quality beats quantity: ten well-verified,
genuinely-matching openings are worth more than a hundred scraped links, because every
opening you surface becomes downstream work (analyzing the professor, drafting outreach).

## What you produce

One file per opening at `knowledge-base/openings/<slug>.md`, following the **opening
schema** in `shared/schemas/README.md` (read it for the exact front-matter fields). Slugs
are lowercase-kebab and should encode lab + topic + year, e.g. `smith-lab-rl-2026`.

## Step 1 — Load the search profile

Read `knowledge-base/profile/profile.md`. The `field`, `subfields`, `target_regions`,
`target_start`, `sources`, and `constraints` fields define the search. If the profile is
empty or thin, ask the user for at least field + region + whether funding is required —
searching without these produces noise. If the user's request already narrows things
(a specific topic, professor, or department), treat that as an overriding filter.

## Step 2 — Choose sources and sweep

Use `shared/references/data-sources.md` for the catalogue. Pick sources that fit the
applicant's field and region rather than searching everything — the `sources:` list in the
profile is the guide. As a rule of thumb:

- **Advertised, funded projects** (common in UK/EU): FindAPhD, EURAXESS, jobs.ac.uk, and
  national portals. These have explicit deadlines and funding — capture them precisely.
- **US / direct-to-advisor style**: there's rarely a "position" posting; the signal is a
  professor whose lab page says they're recruiting, or whose recent hiring/grant activity
  implies openings. Treat "this lab is plausibly recruiting in your area" as a valid
  opening, with `funding: unknown` and a note on the admission model.
- **Topic-driven**: when the user gives a research topic, search recent publications and
  lab pages to find *who* works on it, then check those labs for openings.

For static pages use web fetch; for JS-rendered listings (some boards, Scholar) use the
browser tools. If a source needs a connector that isn't available, tell the user rather
than silently skipping it.

**Verify before recording.** Follow each promising hit to its primary source (the lab or
program page), confirm it's current (not a closed call from two years ago), and read enough
to fill the schema honestly. A plausible-looking listing that turns out to be expired is
worse than no listing. Determine today's date with the shell, and when you confirm an opening
is live, record that date in `verified_on` — it's the currency stamp the ranker and tracker
use to tell a fresh opening from a stale one. Check the `deadline` and intended `start_year`
against today: a passed deadline or a prior cycle means *don't record it as new* (or record it
with a clear note that it's expired), rather than presenting it as actionable.

## Step 3 — Filter and de-duplicate

Apply the applicant's hard constraints as filters, not suggestions. Read the typed
**`funding_required`** flag and `target_start` from the profile: if `funding_required: true`,
drop `self-funded` openings (and flag `unknown`-funding ones for the applicant to verify) —
an unfunded position for someone who needs funding is not a match. Drop anything that fails a
dealbreaker, region, or start-year filter.

Before writing, check existing files in `knowledge-base/openings/` so you don't create a
duplicate. If an opening already exists, update it (e.g. a newly found deadline) rather
than making a second file.

## Step 4 — Write opening records

For each surviving opening, write `knowledge-base/openings/<slug>.md` with all schema
fields. Set `status: new`, `verified_on` to today's date, `start_year` to the intake year,
and `funding` to one of `fully funded | partial | self-funded | unknown` (use `self-funded`
explicitly — never blur it into `partial`). In the body:

- `## Description` — what the project/position actually is, in your words.
- `## Requirements` — degree, skills, tests, eligibility (note visa/nationality limits).
- `## Why it fits` — the concrete link to the applicant's profile (topic, method, goal).
  This is what makes the record useful later; be specific, not "matches your interests".
- `## Notes` — admission model, funding clarity, anything the applicant should verify.

Leave a field blank when genuinely unknown rather than guessing a deadline or funding
status — downstream ranking depends on these being honest.

## Step 5 — Report and hand off

Give the user a short ranked-by-promise summary: how many openings you found, the
strongest two or three with one line each on why, and any source you couldn't reach. Then
suggest the natural next steps: deep-dive the most promising professors with
**professor-analyzer**, or rank everything with **opportunity-ranker** once a few openings
exist.

## Recurring sweeps

Discovery is naturally periodic — new positions appear throughout a cycle. If the user
wants ongoing coverage, offer to set up a scheduled task that re-runs this sweep (e.g.
weekly) and reports only genuinely new openings since last time.

## Guardrails

Respect source etiquette in `shared/references/data-sources.md` (APIs over scraping, rate
limits). Never invent an opening, a deadline, or a funding guarantee — an applicant who
plans around a fabricated deadline is actively harmed. When unsure whether a position is
real or current, mark it for the user to verify rather than asserting it.
