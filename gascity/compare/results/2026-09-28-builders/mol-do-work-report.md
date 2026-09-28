Method: dual-agent (A: impeccable.design-reviewer step xpr-maw · B: impeccable.evidence-collector step xpr-9yh)

# Critique: Harbor Ledger landing page (`mol-do-work/index.html`)

Mode: **Persuade**. No PRODUCT.md or DESIGN.md exists, so the page is the only source of context. There was no live URL, and browser evidence could not be collected (see the Visual overlays section below).

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Static page, so there is little status to report. Skip link and focus rings are visible. The nav has no current-section state, and the hero CTA gives no cue that it leaves for `app.harborledger.example`. |
| 2 | Match System / Real World | 3 | The language is plain, but "files the month" (lead, Monthly close) is ambiguous: file taxes, archive, or produce statements? "Close" is bookkeeping jargon that a spreadsheet keeper may not use. |
| 3 | User Control and Freedom | 3 | Nothing traps the reader, and the trial needs no card. Once the reader scrolls past the hero, the only way to act is to scroll back up. |
| 4 | Consistency and Standards | 3 | Visually cohesive. The voice changes from "you" (hero, FAQ) to "the customer" (Privacy, Terms). The nav lists Pricing and FAQ but leaves out `#features`, the page's main argument. |
| 5 | Error Prevention | 3 | The fear of being charged is headed off three times (plan card, FAQ, Terms). The $18 plan card never says what it covers (how many businesses, how many bank accounts, the free accountant seat), which invites wrong expectations. |
| 6 | Recognition Rather Than Recall | 3 | Everything is labelled and visible. The one value add (a free accountant seat) appears only in the FAQ, away from the price. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: a single-scroll landing page has no expert workflow to accelerate. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and restrained. Two one-sentence legal sections carry the same h2 and section weight as Pricing, and the palette is the detector-flagged cream default. |
| 9 | Error Recovery | n/a | No inputs, forms, or stateful actions on the page. Signup errors happen on the external app. |
| 10 | Help and Documentation | 2 | A three-question FAQ plus a contact email. It skips what a bookkeeping buyer actually asks: how the bank connection works and whether it is secure, which spreadsheet tools work, and what "files the month" produces. |
| **Total** | | **23/32** | **Good** (72%; heuristics 7 and 9 scored n/a) |

The score is high because the page is usable. Its weaknesses are persuasion and trust, and these heuristics only partly measure those. Read 23/32 as "nothing is broken", not "this converts".

## Design Specificity Verdict

**The copy is specific to the product. The visual design is category-interchangeable.**

**LLM assessment.** "Books that close themselves", "reads the spreadsheet you already keep", and "a report your accountant can read without asking you to explain your spreadsheet" name one audience (small-business owners who keep their books in a spreadsheet) and one pain (the month-end close and the handoff to an accountant). That copy is where all the character is. The visuals are a cream background (`#faf6ec`), one green accent (`#1f7a4d`), the system-ui font stack, one 44rem column, 1px rules between sections, and one rounded green button. You could swap in a meditation app or a newsletter and change nothing but the words. The missed opportunities:
- **No evidence of the product.** Nothing on the page shows a matched transaction, a closed month, or the accountant report.
- **Accounting's visual vocabulary goes unused.** Ledger rules, tabular figures, debit and credit columns, and a "closed" mark are all absent. The cream hints at paper and stops there.
- **"Harbor" does no work.** Neither the brand nor the plan name (also "Harbor") ties to any visual or verbal idea, such as safe keeping.

The restraint is disciplined and accessible, not decoration. The result reads as unfinished rather than authored.

**Deterministic scan.** `impeccable detect --json mol-do-work/index.html` exited 2 with **1 finding, 1 rule, 1 file**:
- `cream-palette` (warning, category "slop"). The page background is rgb(250, 246, 236). The detector reports line 0 because it checks computed page style. In the source, the token `--cream: #faf6ec` is defined on line 10 and applied to `body` on line 21. The related tokens `--cream-deep: #f1ebd9` (line 11, the plan card) and `--rule: #d8d0b8` (line 15) belong to the same family.

**Where they agree.** The design review never saw the detector output, yet it independently named the cream and green system as generic. The detector's `cream-palette` hit is the mechanical form of that same judgement, so the two sources agree on the page's main design weakness. **This is not a false positive.** The value matches the rule exactly, and no DESIGN.md records a deliberate palette decision that could override it. The only sign of intent is that the colour is a named token inside a small, consistent palette. That shows discipline, not a decision.

**What the detector could not see.** Every other priority issue below comes only from the design review: the missing CTA at the end, the absence of trust signals, the legal sections with h2 weight, the ambiguous "files", and the flat section hierarchy. The detector's rule set does not cover persuasion structure or trust, so it has no false negatives to fault here, only a narrow scope.

**Visual overlays.** None. No browser automation tool was available in this session, and no Chromium or Playwright was on PATH. The live-server and script-injection steps never ran, so **no reliable user-visible overlay exists**. The fallback signal is the CLI detector result above. No server was started, so none needs stopping.

## Overall Impression

This is an honest, accessible, well-written page that sells on words alone. The copy lands in the first 25 words. Everything after that under-delivers: nothing shows the product working, nothing earns the trust that a bank-data product needs, and the page ends on two one-sentence legal stubs with no second chance to act. **The biggest opportunity is to show one month closing**, a ledger-styled excerpt of a matched transaction or the accountant report. That single element would fix both the proof gap and the generic look.

## What's Working

1. **Precise, honest copy.** The headline and lead name a real audience and a real pain without hype. The trial terms ("14 days", "no card", "nothing is billed") are plain and consistent everywhere they appear.
2. **Solid accessibility basics.** The page has a skip link, a 3px `:focus-visible` ring, `aria-labelledby` on every section, a labelled nav, a correct h1 → h2 → h3 order, a 44px minimum button height, and smooth scroll turned off under `prefers-reduced-motion`. Contrast passes AA everywhere: ink on cream is 16.2:1, muted on cream 8.3:1, green links on cream 4.9:1, and white on the green button 5.3:1.
3. **Restrained scope.** One plan, one CTA, three features and three questions. At 390px the page reflows cleanly with no overflow.

## Priority Issues

**[P1] The page ends with no call to action**
- **Why it matters**: "Start the 14-day trial" appears once, in the hero. Readers decide after Pricing or the FAQ, and at that point there is nothing to click. On mobile the hero button is about five screens up. The page then closes on the Privacy and Terms stubs, so by the peak-end rule the last impression is boilerplate.
- **Fix**: Put the CTA inside the `.plan` card ("Start the 14-day trial, no card"). Add a short closing section after the FAQ that restates "Books that close themselves" and repeats the button. Optionally add a compact CTA to the header.
- **Suggested command**: `gc sling experiment/impeccable.conductor polish --formula`

**[P1] No proof or trust signals for a product that touches bank data and the books**
- **Why it matters**: The purchase asks the reader to connect a bank and let software "file" their books. The page offers no screenshot, sample report, testimonial, security statement, or named company. The one data answer ("It stays in your account, and you can delete it") says the reader has control but not where the data is stored or how it is protected. A cautious reader will notice the dodge, and the confident headline reads as unverified.
- **Fix**: Show the output as ledger typography, not a stock screenshot: one bank line matched to a spreadsheet row, or an excerpt of the month-end report. Under Bank import, add one concrete security line (how the connection works, read-only access, where data lives). Rewrite the FAQ data answer to state storage and protection.
- **Suggested command**: `gc sling experiment/impeccable.conductor polish --formula`

**[P2] Legal stubs sit in `<main>` with the same weight as Pricing**
- **Why it matters**: `#privacy` and `#terms` are full sections with h2s, each holding one third-person sentence ("the customer") that repeats the FAQ. They flatten the hierarchy at the most important part of the scroll, break the warm second-person voice, and look like placeholders, which erodes trust. The footer links only jump back to them.
- **Fix**: Move Privacy and Terms to their own pages, or at least out of `<main>` into a smaller footer treatment. Keep the reassurance in second person in the FAQ, where readers look for it.
- **Suggested command**: `gc sling experiment/impeccable.conductor polish --formula`

**[P2] "Files the month" is ambiguous, and the plan card doesn't say what $18 buys**
- **Why it matters**: A reader who takes "files" to mean filing taxes will either hesitate or be disappointed later. The plan card lists no inclusions, and the free accountant seat is buried in the FAQ, so the reader cannot judge value where the price is.
- **Fix**: Replace "files the month" with the concrete outcome, for example "reconciles the month and produces a report for your accountant". Add 3–4 inclusion lines to the plan card: bank accounts, spreadsheet sources, the monthly close report, and one accountant seat free.
- **Suggested command**: `gc sling experiment/impeccable.conductor polish --formula`

**[P3] Flat hierarchy and a generic visual identity (cream-palette)**
- **Why it matters**: Every section below the hero has the same h2 size, 3.5rem padding and rule, so Pricing looks as important as Terms. The h2 → h3 gap is 0.75rem, so "What it does" and "Bank import" run together. The cream and green system, which the detector flagged, makes the page forgettable, and nothing visual supports "Ledger".
- **Fix**: Give Pricing and the closing CTA more visual weight than the other sections, and increase the space after h2s. Give the features a ledger treatment: a ruled table, tabular numerals, or a month-closed mark. Choose the background as part of a deliberate palette (for example ledger-paper white with a ruled accent) rather than the default cream. Consider a heading or figure face with character, such as a tabular serif for the price.
- **Suggested command**: `gc sling experiment/impeccable.conductor polish --formula`

## Persona Red Flags

**Jordan (Confused First-Timer)**: The lead's "files the month" and Monthly close's "the close is done" are unexplained terms, and Jordan may read "files" as filing taxes. Clicking "Start the 14-day trial" gives no preview of what happens next (upload a spreadsheet? connect a bank?). There is no demo, sample report, or screenshot to look at before committing. Jordan is likely to hesitate at the hero button.

**Riley (Deliberate Stress Tester)**: The `#privacy` and `#terms` "policies" are one sentence each, and Riley will read them as placeholders. The FAQ says data "stays in your account" but never says where the account lives or what happens to bank credentials. Edge cases go unanswered: more than one business, more than one accountant (only "one accountant at no charge"), Excel versus Google Sheets, and what happens when a transaction cannot be matched. Riley leaves without trusting the product.

**Casey (Distracted Mobile User)**: At 390px the only CTA is on the first screen. After reading Pricing, Casey has to scroll about five screens back up, and there is no repeated or sticky CTA within thumb reach. `scroll-padding-top: 5rem` is set on a header that is not sticky, so every anchor jump leaves an unexplained 80px gap above the heading. On the positive side, tap targets meet 44px and the page loads instantly. Casey is lost at the end of the FAQ.

## Minor Observations

- The nav omits `#features` ("What it does").
- The plan name "Harbor" just repeats the brand. With one plan, drop it or use a descriptive label.
- `.price span` ("a month after the trial") is visually disconnected from the 2.25rem "$18". "$18/month" plus a trial line would read tighter.
- The `.skip` link hides at `top: -4rem`. A wrapped or larger label could peek into view, and clip-based hiding is more robust.
- The CTA links to an external domain with no cue.
- The `.name` link has no hover or focus style beyond the global outline.
- There is no favicon or Open Graph image, which matters for how a Persuade page travels.
- The footer "Contact:" line is the only human touch. No company name or location appears, which counts for a finance product.
- The `--rule` colour (`#d8d0b8`) is the only structural device. Repeated at equal weight, it adds to the flat rhythm.

## Questions to Consider

- The headline promises books that close themselves. What if the page showed one spreadsheet row becoming a reconciled, closed month, instead of describing it in three paragraphs?
- The accountant can make or block the sale. What would one line written directly to the accountant do for trust?
- If "Harbor" means safe keeping, where on the page does the reader feel their data is safe?
- Why does the page end on legal text? What should a hesitating reader see last?
- Is the cream and green restraint a brand decision or the absence of one? If a competitor copied this layout and swapped the copy, would anyone notice?

---

> **Trend for `mol-do-work-index-html`: 23/32. This is the first run for this target, so there is no trend yet.**
> Wrote `.impeccable/critique/2026-09-28T09-26-26Z__mol-do-work-index-html.md`.

## Questions for the user

1. **Priority direction.** The critique found three kinds of problem: conversion structure (no CTA after Pricing or the FAQ, and the page ends on legal stubs), trust (no proof of the product and a vague data answer, which matters for a bank-connected product), and visual identity (generic cream and green, flat hierarchy, and nothing that says "ledger"). Which should be fixed first?
   - a) Conversion structure: repeat the CTA in the plan card and a closing section, and move Privacy and Terms out of `<main>`.
   - b) Trust and proof: add a ledger-styled excerpt of a matched transaction or month-end report, a security line under Bank import, and a clear data answer.
   - c) Visual identity: a deliberate palette in place of the flagged `cream-palette` background, ledger typography, and stronger weight for Pricing.

2. **Design intent.** The quiet cream-and-green, system-font look reads as "tasteful default" rather than as a bookkeeping product, and the detector flagged the cream background as a reflex choice. Was that restraint intentional?
   - a) Yes, keep the calm, paper-like tone and only make it more specific (ledger rules, tabular figures, a "closed" mark).
   - b) No, give it a sharper, more precise character: crisp white, ruled columns, a tabular serif for figures.
   - c) No, make it warmer and more human: lean into "Harbor" and safe keeping, and talk directly to the owner and their accountant.

3. **Scope.** There are 5 priority issues (2 P1, 2 P2, 1 P3) and 9 minor observations. How much should the next pass take on?
   - a) The two P1s only: the missing end-of-page CTA and the proof and trust gap.
   - b) All five priority issues.
   - c) Everything, including the minor observations (nav `#features` link, "$18/month" formatting, skip-link hiding, favicon and Open Graph).

4. **Constraints.** Are any parts off-limits?
   - a) Keep the headline and lead copy exactly as written. Change the structure and visuals only.
   - b) Keep the single-plan, single-price structure, and don't add tiers or plan comparisons.
   - c) Nothing is off-limits.
