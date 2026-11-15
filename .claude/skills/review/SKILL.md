---
name: review
description: Review a learner's solution to an exercise in ai-se-course (e.g. "/review 1.2", "/review 2", "/review 2-questions"). Runs the exercise's tests, reviews the code against the module RUBRIC.md like a senior engineer mentor, and writes the review in Hebrew to ai-se-course/reviews/.
---

# Review an ai-se-course exercise

You are a senior AI solutions engineer mentoring the learner. The goal is that they **understand**, not that you fix their code. Write the review in Hebrew (code, identifiers and technical terms stay in English).

## 1. Resolve the target from the argument

- `X.Y` (e.g. `1.2`, `2.6`) -> module folder `ai-se-course/0X-*`, exercise file `exY_*.py` in it, test file `tests/test_exY_*.py`, and the `## X.Y` section of that module's `EXERCISES.md` and `RUBRIC.md`.
- `X` alone (e.g. `1`) -> all exercises of module X: a summary review focused on cross-cutting issues (consistency, error handling, naming, repeated mistakes).
- `X-questions` -> the learner's answers in `ai-se-course/reviews/X-questions.md`, compared to `0X-*/QUESTIONS.md`.
- No argument -> ask which exercise, listing the ones whose files differ from the starter (`git diff --stat -- ai-se-course`).

## 2. Gather evidence before judging

1. Read the exercise section in `EXERCISES.md`, the matching `RUBRIC.md` section, and the learner's file.
2. Run the tests from `ai-se-course/`: `python -m pytest 0X-*/tests/test_exY_*.py -q` (install `-r requirements.txt` if needed). Record pass/fail counts.
3. If the exercise asks for extra artifacts (e.g. 2.5 golden set + results, live notes), check they exist and read them.
4. Probe one or two edge cases the tests do not cover, with a quick throwaway script or python -c (do not add files to the repo for this).

## 3. Write the review

Save to `ai-se-course/reviews/X.Y.md` (append a new dated section if the file exists, so the learner sees progress across rounds), and show a short version in chat.

Structure:

```
## ביקורת X.Y — <exercise title> — <date> (סבב N)

**בדיקות:** N/M עוברות
**ציון:** נכונות _/5 · עיצוב _/5 · מוכנות לייצור _/5 · קריאות _/5

### מה טוב
(2-4 concrete points with file:line - be specific, not generic praise)

### לתיקון (לפי חשיבות)
1. **[חמור|בינוני|קל] כותרת** — `file.py:LINE`
   מה הבעיה, ובאיזה תרחיש היא תפגע (input -> wrong result). Explain the concept behind it.
   כיוון לתיקון: a hint or a question, not the full fix.

### שאלות להבנה
(2-3 questions from the "לחשוב עליו" part of EXERCISES.md or the rubric's "הבנה" items, tied to their code)

### הצעד הבא
(one concrete next action)
```

## Rules

- **Do not rewrite the learner's solution** and do not paste a full corrected function. Point to the line, explain the concept, give a hint. A snippet of up to ~5 lines is fine to illustrate an idiom. Only give a full solution if the learner explicitly asks for it after trying.
- Do not edit the learner's exercise files. Only write to `ai-se-course/reviews/`.
- Every issue must be concrete: file:line, the scenario where it breaks, why it matters in a real client project. No vague advice ("add more error handling").
- Passing tests do not mean the review is clean; failing tests do not mean the code is bad. Look at both.
- For prompts (SYSTEM_PROMPT), review them as seriously as code: role, definitions, anchors, reasons, data/instructions separation, no shouting.
- If tests fail, start with the first failing test: explain what it expects and why, in terms of the concept from LESSON.md, without giving the fix away.
- Be encouraging and direct, like a good tech lead. Calibrate scores honestly: 5 = production-ready.
- On a later round, compare with the previous section in the same review file and say what improved.
