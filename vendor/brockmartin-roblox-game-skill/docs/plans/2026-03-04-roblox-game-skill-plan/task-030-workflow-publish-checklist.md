# Task 030: Write publish-checklist.md Workflow

**depends-on:** 001
**phase:** 5 - Workflows
**files:** `workflows/publish-checklist.md`

## Description

Write the pre-publish verification checklist.

## What To Do

Create a comprehensive checklist organized by category:

1. **Data & Persistence** — DataStore tested (save/load/edge cases), session locking verified, BindToClose implemented, data migration plan if updating
2. **Security** — All remotes validated server-side, no sensitive data exposed, rate limiting on all remotes, no client-trusted game logic
3. **Performance** — Mobile tested, part count within limits, no memory leaks, MicroProfiler reviewed, StreamingEnabled if large map
4. **Monetization** — GamePasses work correctly, DevProducts grant properly and handle ProcessReceipt, Premium benefits functional, prices reviewed
5. **Mobile Compatibility** — Touch controls work, UI scales properly (Scale not Offset), ContextActionService for input, tested on small screen
6. **Gameplay** — Core loop tested end-to-end, edge cases handled (disconnect during trade, death during cutscene), tutorial/FTUE works
7. **Metadata** — Game icon set (512x512), thumbnails uploaded, description written, genre selected, max players configured
8. **Social** — Private servers configured and priced, social features tested, report/block doesn't break game
9. **Analytics** — Key events instrumented (joins, purchases, level completions), basic funnel tracking

Each item should be a checkable item with brief explanation of what to verify.

## Verification

- File exists at `workflows/publish-checklist.md`
- At least 9 categories covered
- Each item is specific and verifiable
- Mobile compatibility section included
- Monetization verification included
