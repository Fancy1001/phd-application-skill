---
name: outreach-email
description: >-
  Draft a personalized cold email or a follow-up message to a potential PhD supervisor. Use
  this whenever the user wants to write, draft, compose, or send an email to a professor —
  e.g. "write a cold email to Prof X", "help me reach out to this professor", "draft an
  intro email about her robotics work", "the professor hasn't replied, write a follow-up",
  or "can you email this PI about a PhD?". Grounds the draft in the professor's real recent
  work (from their knowledge-base profile) and the applicant's real background, produces a
  ready-to-edit draft the applicant sends themselves (never auto-sends), and logs the
  contact with a follow-up date to knowledge-base/interactions/. Trigger whenever the intent
  is to contact a professor about a PhD, including follow-ups and reply-drafting, even if the
  word "email" isn't used.
---

# Outreach email

A cold email to a professor is the applicant's first impression, competing for attention in
an overflowing inbox. The emails that get replies are short, specific, and unmistakably
written *to this person* — they prove the applicant read the work and have a real reason to
want this lab. The emails that get ignored are long, generic, and could have been sent to
anyone. This skill exists to produce the former, grounded in fact, in the applicant's voice.

The cardinal rule, from `shared/references/ethics.md`: **draft, never send.** You produce a
draft for the applicant to review, edit, and send themselves. You may record the contact and
schedule a follow-up reminder, but the applicant owns the send.

## Step 1 — Load the people

Read the professor's profile at `knowledge-base/professors/<slug>.md`. Check the typed
front-matter fields first — they're the contract: **`email_policy`** (is a cold admissions
email even welcome?), **`admission_model`** (does the professor or a committee decide?), and
**`accepting_students`**. Then read the **Outreach hooks**, **Research agenda**, and **Notes**
(subject conventions, application routing) for the substance. Read the applicant's
`knowledge-base/profile/profile.md` and skim `profile/cv-master.md` for the one or two
credentials most relevant to *this* professor.

If no professor profile exists, run **professor-analyzer** first — an email written without
it will be generic, which defeats the purpose. **Before drafting, honor the contact rules:**

- `email_policy: do-not-email-admissions` (or Notes saying so) → don't produce a cold
  "please take me" email. Surface it: the right move is a program application that names them,
  or a narrow, substantive research question. Hand the hooks to **application-materials** for
  the SOP instead.
- `admission_model: program-committee` / `rotation` → outreach is low-leverage; say so and
  steer effort to the application unless the applicant has a specific research reason to write.
- If `email_policy` is blank, fall back to the `## Notes` prose, then default to a careful
  cold email only when nothing says otherwise.

## Step 2 — Cold email vs. follow-up

Check `knowledge-base/interactions/<professor-slug>.md`. If there's prior contact, this is a
**follow-up**, not a cold email — read what was already said and when, and write something
that adds value rather than just "bumping". If there's no prior contact, it's a cold email.

## Step 3 — Draft a cold email

Keep it tight — roughly 120–200 words, readable on a phone in 20 seconds. Structure:

- **Subject line**: specific and honest, e.g. "Prospective PhD — sim-to-real RL & your
  HiL-SERL work". Use any subject convention the profile Notes specify.
- **Who you are** (one line): name, current position, the single most relevant credential.
- **Why this lab** (the core): reference one genuine, specific hook from the profile — a
  particular recent paper and a real reaction or question, or a concrete link between their
  open problem and the applicant's work. This is the sentence that proves it isn't spam.
- **What you're asking**: a clear, low-friction ask (whether they're taking students for
  <year>, whether they'd be open to a short chat). One ask, not five.
- **Sign-off**: a line pointing to attached CV / a link, and thanks.

Use at most one or two hooks — piling on every paper reads as a literature review, not a
message. Match the applicant's voice from their profile; don't make them sound like a
press release. Flag with `[brackets]` any specific only the applicant can supply (a result,
a number, a personal motivation) rather than inventing it.

## Step 4 — Draft a follow-up

A follow-up should be shorter than the original and give a *reason* to re-engage, not just
guilt. Good reasons: a new relevant result or paper of the applicant's, a brief
clarification of fit, or a genuinely new specific question about their work. Keep it polite,
brief, and easy to ignore-or-reply. Reference the prior email lightly ("following up on my
note from <date>"). Never be pushy or imply obligation — respect that silence is an answer.

## Step 5 — Produce the draft and log it

Present the draft to the applicant clearly (subject + body), with any `[brackets]` they must
fill and a one-line note on why you chose the hook you did. Do **not** send it.

Then append an entry to `knowledge-base/interactions/<professor-slug>.md` following the
interaction-log format in `shared/schemas/README.md`:

```markdown
### <date> — drafted: cold email
Subject: ...
Summary: one line on the angle/hook used
Follow-up due: <date ~10–14 days out>
Status: draft — awaiting user send
```

Set a sensible follow-up date (typically ~2 weeks for a cold email). If the applicant
confirms they've sent it, update Status to "sent". Offer to have **application-tracker**
watch the follow-up date.

## Guardrails

Follow `shared/references/ethics.md` without exception. Never fabricate a shared interest,
a paper, a result, or enthusiasm the applicant doesn't have — a professor who catches one
invented detail discards the whole message and remembers the name. If genuine fit is thin,
say so to the applicant rather than papering over it with flattery; a weaker but honest
email beats a strong dishonest one. And never send — the applicant always reviews first.
