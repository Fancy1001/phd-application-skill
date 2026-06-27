---
name: application-materials
description: >-
  Tailor and optimize academic application documents — CV, resume, statement of purpose
  (SOP), and personal statement — for a specific PhD opportunity. Use this whenever the user
  wants to adapt, customize, write, polish, or optimize application materials — e.g. "tailor
  my CV for this position", "write an SOP for MIT EECS", "customize my personal statement for
  the Smith lab", "make my resume fit this studentship", or "optimize my statement for this
  professor". Selects, reorders, and emphasizes true material from the applicant's master CV
  and profile to fit the target; never invents credentials. Writes tailored documents to
  knowledge-base/applications/[id]/. Trigger whenever the intent is to prepare or adapt
  CV/SOP/personal-statement material for a specific application.
---

# Application materials

Tailoring is the discipline at the heart of this skill: the same person, presented so the
parts most relevant to *this* opportunity come first and loudest. It is selection, ordering,
and emphasis of true facts — never invention. A tailored SOP makes an admissions reader feel
the applicant has thought specifically about this lab; a tailored CV puts the relevant
publication or skill where the eye lands first. The raw material is the applicant's real
record; the craft is fit.

## Step 1 — Load source material and target

Read the applicant's `profile/cv-master.md` (the complete superset of their record),
`profile/profile.md`, and `profile/research-statement.md` if present. Read the target: the
professor's profile at `knowledge-base/professors/<slug>.md` and the opening/application at
`knowledge-base/applications/<id>/` or `knowledge-base/openings/`. Note the program's
explicit requirements (length, prompts, format) and follow them exactly — an SOP that
ignores the stated word limit or prompt reads as careless.

If the master CV is thin or missing, ask the applicant for the missing material rather than
inventing it. You can only tailor what truly exists.

## Step 2 — Decide what to emphasize

Compare the applicant's record against what this target values (from the professor's agenda
and the opening's requirements). Identify the three or four things about the applicant most
relevant *here* — the matching method, the on-topic project, the transferable result — and
make those the spine of the documents. Relevant-but-secondary material stays but moves down;
truly irrelevant material can be cut for length. The same applicant's CV for a theory lab and
a systems lab should look meaningfully different in ordering and emphasis.

## Step 3 — Produce the documents

### CV / resume
Reorder sections and entries so the most relevant come first. Tighten bullet points to lead
with outcomes and the methods this lab cares about. Keep it truthful and verifiable; never
inflate a role, a result, or a skill level. Output `applications/<id>/cv.md`.

### Statement of purpose
The SOP is an argument: *this applicant + this lab = a good bet*. A workable arc:

1. A specific opening that signals genuine, particular interest (not "since childhood I have
   loved science").
2. The applicant's relevant trajectory — what they did, what they learned, the results —
   selected for relevance to this lab.
3. Why *this* lab specifically: the professor's work, named, and how the applicant's
   direction connects to the lab's open problems.
4. Goals and fit: what they want to work on and why this is the place.

Weave the applicant's real experience toward this lab's work. Mark with `[brackets]` any
specific only the applicant can supply (a motivation, a result, a number). Output
`applications/<id>/sop.md`.

### Personal statement
Where a program asks for a separate personal statement (often about background, resilience,
diversity of perspective, or fit with the program's mission rather than research), keep it
distinct from the SOP — personal and reflective, still grounded in the applicant's real
experience. Output `applications/<id>/personal-statement.md`.

## Step 4 — Keep voice consistent and honest

All documents for one application should sound like one person and tell one coherent story —
ideally aligned with any research proposal and outreach email for the same target. Match the
applicant's voice from their existing writing; avoid generic admissions-essay clichés and
overblown phrasing. The hard line from `shared/references/ethics.md`: tailoring selects and
orders true facts; it never fabricates or inflates. An exaggerated CV is both dishonest and a
liability the applicant can't defend in interview.

## Step 5 — Save and hand off

Write the documents to `knowledge-base/applications/<id>/`. Tell the applicant what you
emphasized and why, and list the `[brackets]` they must fill. For submission-grade formatting
(a polished PDF or Word CV/SOP), hand off to the `pdf` or `docx` skill.

## Guardrails

Never invent or inflate credentials, results, or skills — the entire value of tailoring is
that it's true material well-arranged. When something relevant is missing from the master CV,
ask rather than fabricate. Respect program prompts and limits precisely.
