Method: dual-agent (A: impeccable.design-reviewer step xpr-3mp · B: impeccable.evidence-collector step xpr-9jf)

# Critique: Harbor Ledger landing page (`mol-scoped-work/index.html`)

Mode: **Persuade** (marketing landing page; primary action is "Start the 14-day trial"). No PRODUCT.md or DESIGN.md exists, so the page is the only statement of intent. No ignore list.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Nothing says the CTA leaves for `app.harborledger.example` or what the next screen asks for; the header nav has no current-section state. |
| 2 | Match System / Real World | 3 | "Files the month" is ambiguous (reads as tax filing); the price is spelled out as "18 dollars a month" instead of the `$18/mo` people scan for. |
| 3 | User Control and Freedom | 4 | Static page with a working skip link, anchor nav, brand link and native back; nothing to get trapped in. |
| 4 | Consistency and Standards | 3 | Voice switches from "you" to "the customer" in Privacy and Terms; the plan "Harbor" vs. the product "Harbor Ledger" is never explained. |
| 5 | Error Prevention | 3 | "No card" appears only at Pricing, not beside the hero CTA; "Books that close themselves" / "files the month" set up a wrong expectation of tax filing. |
| 6 | Recognition Rather Than Recall | 4 | Everything is visible and text-labelled; the page is short enough that nothing must be remembered. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: one linear read, one action. |
| 8 | Aesthetic and Minimalist Design | 3 | Uncluttered, but hierarchy is flat: every section below the hero gets identical padding, rule and h2, so one-sentence legal stubs weigh as much as Pricing. |
| 9 | Error Recovery | n/a | No inputs, forms or error states on this page; signup is off-page. |
| 10 | Help and Documentation | n/a | Persuade surface; the FAQ is judged as objection handling below. |
| **Total** | | **23/28** | **Good (82%)** |

Applicable maximum is 28: heuristics 7, 9 and 10 were scored n/a. The score measures usability, and on that axis the page is hard to misuse. It is much weaker as persuasion, which is where every priority issue below sits.

## Design Specificity Verdict

**LLM assessment.** Split verdict: **the copy is authored for this product; the visuals are category-interchangeable.** Lines like "reads the spreadsheet you already keep" and "a report the accountant can read without asking you to explain your spreadsheet" come from a real understanding of the buyer, a small-business owner who keeps books in a spreadsheet and hands them to an accountant. A competitor could not reuse them. The visual system is a different story: cream background, one green accent (`#1f7a4d`), the system-ui font stack, a single centred column and hairline rules between sections. Swap in a newsletter tool or a scheduling app and nothing would look wrong. The two touches that hint at paper and a ledger (the warm "paper" ground and the ruled dividers) are too faint to read as intentional; `--rule` is only 1.41:1 against the cream. Missed character opportunities: the page never shows a spreadsheet row, a matched bank line, a "closed" state or the accountant report; no tabular figures, column rules or double-underlined total; "Harbor" gets no visual expression; and the one number on a bookkeeping product's page, its price, is written in words.

**Deterministic scan.** `impeccable detect --json mol-scoped-work/index.html` exited 2 with **1 finding, 1 rule, 1 file**:

- `cream-palette` (warning, category: slop): page background rgb(250, 245, 230), from the token `--cream: #faf5e6` at `mol-scoped-work/index.html:10`, applied to `body` at line 19 and reused as the skip-link background at line 35. The detector reports line 0 because it is a page-level computed-style check; the real source lines are 10 and 19.

**Where they meet.** The two assessments were formed independently and agree. The detector flagged the cream ground as the reflexive "tasteful" default, and the design review, without seeing that output, named the cream background as the first item in its list of interchangeable choices. **Not a false positive.** The colour is a named token in a four-token palette, which shows some intent, but with no DESIGN.md recording a palette decision and nothing else on the page building the paper/ledger idea, the cream is doing the generic job the rule describes. The detector caught nothing the review missed; the review caught everything else in this verdict (typography, layout sameness, absent product artefact) that a single-rule scan cannot see. Treat the cream finding as a symptom of Priority Issue 5, not a standalone fix: repainting the background without giving the page a ledger identity would just trade one default for another.

**Visual overlays.** None. Browser visualization was not attempted: the session exposed no browser automation tool and no Chromium or Playwright binary, and no live URL existed. No user-visible overlay is available; the fallback signal is the CLI detector result above. (The design review did look at headless-Chromium screenshots at 1280px and 390px, which is where the layout and touch-target observations below come from.)

## Overall Impression

This is a calm, honest, accessible page with excellent buyer-specific copy, and it asks the visitor to take its central claim entirely on faith. "Books that close themselves" is a strong promise for someone who dreads month-end, and nothing on the page shows it happening: no screenshot, no sample report, no number, no customer. For a product that will hold bank transactions, it is also silent on how the bank connects and who sees the data, then ends on a one-sentence privacy policy. **Single biggest opportunity: show the artefact.** Put the report the accountant receives (or a spreadsheet row beside its matched bank line, marked "Closed: March") directly under the hero. That one addition is proof, product character and ledger visual identity at once.

## What's Working

1. **Copy written for the buyer, not the category.** It names the buyer's real objects (their spreadsheet, their bank, their accountant) and their real fear (learning a new system). "Without a new system to learn" defuses switching anxiety in the lede, exactly where it arises.
2. **One action, stated honestly.** Both CTAs read "Start the 14-day trial" with identical styling. No card, nothing billed after the trial and a free accountant seat are all stated plainly, with no dark-pattern hedging. Cognitive load is low: no decision point exceeds 3 options.
3. **Solid accessibility foundations.** Working skip link, `aria-labelledby` on every section, a labelled nav, a 3px ink `:focus-visible` ring (15.8:1), green links at 4.88:1 and white-on-green buttons at 5.32:1 (7.57:1 on hover), 44px minimum button height, `prefers-reduced-motion` honoured, and a fluid `clamp()` h1 that holds at 390px.

## Priority Issues

1. **[P1] The promise has no proof.**
   - **Why it matters:** In Persuade mode proof carries the page. "Books that close themselves" invites "sure they do", and the spreadsheet-to-closed-month transformation is inherently visual. The emotional journey peaks at the hero and drops straight into three unillustrated sentences.
   - **Fix:** Directly under the hero (or as the body of "What it does"), show one concrete artefact: the accountant report, or a spreadsheet row next to its matched bank line with a "Closed: March" state. Add one line of real social proof if it exists; do not invent any.
   - **Suggested command:** `gc sling experiment/impeccable.conductor bolder --formula`

2. **[P1] Bank-connection trust gap.**
   - **Why it matters:** "Brings in your bank transactions" is the moment a finance buyer tenses, and it is the highest-stakes point in this funnel. The only data answer, "Your data stays in your account, and you can delete it", is vague enough to read as evasion. A visitor who won't connect a bank won't start the trial.
   - **Fix:** Add a short security block or FAQ entry stating how the bank connects (read-only? through what kind of provider?), who can see the data (you plus your one invited accountant) and what deletion removes. Rewrite the existing FAQ answer with those specifics.
   - **Suggested command:** `gc sling experiment/impeccable.conductor clarify --formula`

3. **[P2] The page ends on legal stubs instead of a close.**
   - **Why it matters:** After the FAQ, where objections have just been answered and intent is highest, `<main>` continues with one-sentence "Privacy policy" and "Terms" sections at full section weight, written about "the customer". There is no final CTA. Peak-end: the visitor's last memory is paperwork, and a one-sentence privacy policy actively lowers trust for a product holding bank data.
   - **Fix:** Add a closing CTA band after the FAQ restating "14 days, no card". Move Privacy and Terms out of `<main>` to real pages or a visually subordinate footer, and keep the voice as "you".
   - **Suggested command:** `gc sling experiment/impeccable.conductor layout --formula`

4. **[P2] Reassurance is in the wrong place, and "files the month" is ambiguous.**
   - **Why it matters:** Most first clicks happen at the hero CTA, but "The 14-day trial needs no card" appears only at Pricing. "Files the month" doesn't say filed where or with whom; a first-timer reads tax filing, which becomes churn or a support ticket when the product doesn't do it.
   - **Fix:** Add microcopy under the hero button: "14 days free · no card". Replace "files the month" with the concrete outcome, e.g. "closes the month and hands your accountant a report".
   - **Suggested command:** `gc sling experiment/impeccable.conductor clarify --formula`

5. **[P3] Visually generic; the product's own material is unused.** (Corroborated by the detector's `cream-palette` finding.)
   - **Why it matters:** The copy builds differentiation and the visuals give it back. The system font stack, reflexive cream ground, single accent and uniform section rhythm could belong to any quiet SaaS; a bookkeeping product should feel exact.
   - **Fix:** Take the identity from the ledger: tabular numerals for figures, column-rule motifs, `$18/month` set as a real figure, and a ground colour chosen as part of that paper/ledger system rather than the default warm off-white (or commit to paper properly with visible rules). Vary the section rhythm so the hero and Pricing dominate and supporting sections recede.
   - **Suggested command:** `gc sling experiment/impeccable.conductor typeset --formula`

Note: only the `critique` formula is currently installed in this pack, so the suggested commands other than critique will need their formulas added before they can be slung.

## Persona Red Flags

**Jordan (First-Timer, small-business owner new to bookkeeping tools):** "Files the month" and "when the month agrees with the bank" assume Jordan knows what closing and reconciliation mean; "files" reads as filing taxes. The page never says which spreadsheet qualifies (Excel? Google Sheets? any layout?), so Jordan can't tell whether *their* spreadsheet works before clicking. Nothing previews what "Start the 14-day trial" will ask for next.

**Riley (Stress Tester):** "Books that close themselves" is untestable from the page, and the obvious edge case (what happens when the month does *not* agree with the bank?) is never addressed. Pricing, FAQ and Terms each restate the same trial facts while cancellation, supported banks, spreadsheet formats and what "delete" covers go unanswered. The one-sentence "Privacy policy" presented as *the* privacy policy is a credibility and legal gap Riley will flag.

**Casey (Distracted Mobile User):** At 390px the hero CTA sits in the first screen at ≥44px, which is good. The second CTA is about 2.5 screens down and there is none at the end. Header nav links are about 37px tall and footer links about 26px with 0.5rem gaps, both under the 44px touch target.

**Sam (Accessibility-Dependent):** No major flags. The heading outline "Pricing > Harbor" gives a lone h3 with only a price paragraph under it, and the skip link relies on default link styling on a cream background (visible on focus, but unstyled).

## Minor Observations

- **Features grid (desktop):** "A report the accountant can read" wraps to two lines while the other titles take one, so the three body paragraphs start at different heights.
- **Hero measure:** the lede is capped at 34rem in a 60rem container but the h1 is not, leaving the right ~40% empty: neither deliberately asymmetric nor centred.
- **Feature heading gap:** 0.25rem between each feature h3 and its paragraph, against 0.75rem elsewhere; on mobile the h3 nearly merges with the text above.
- **Pricing hierarchy:** the plan name "Harbor" (h3, 1.125rem) is smaller than the price line (1.5rem), orphaning the label above its value.
- **`#top` anchor** sits on the hero section, not the page top, so the brand link scrolls to just below the header.
- **Nav coverage:** no header link to "What it does", although the section has an id.
- **Hard-coded hover colour** `#17603c` instead of a token beside `--green`.
- **Meta description** repeats the lede verbatim and misses the chance to say "no card".
- **Section rules** (`--rule` #d9d0b8) are 1.41:1 against the cream and nearly vanish on low-quality screens.

## Questions to Consider

- The product's output is a report "the accountant can read". Why isn't that report the hero image? What would the page look like if it *were* the report?
- If the books close themselves, what does the visitor see when they don't? Would showing the one mismatch Harbor Ledger flags be more convincing than claiming nothing needs attention?
- Who is this page talking to: the owner, or the accountant who might recommend it? The free accountant seat suggests the accountant is a growth channel, yet the page never addresses them.
- Is "18 dollars a month" a deliberate plain-spoken voice choice? If so, why doesn't the visual language carry the same plain-ledger personality?
- Would you trust a company holding your bank transactions whose entire privacy policy is one sentence?

> **Trend for `mol-scoped-work-index-html`: 23/28. First run for this target, no trend yet.**
> Wrote `.impeccable/critique/2026-09-28T10-06-40Z__mol-scoped-work-index-html.md`.

## Questions for the user

1. **Priority direction.** The report found two P1 persuasion gaps and a P3 identity gap. Which should the next pass tackle first?
   - **Proof:** put the accountant report or a matched spreadsheet/bank row under the hero (Issue 1).
   - **Trust:** add a bank-connection and data-access block, and replace the one-sentence privacy stub (Issues 2 and 3).
   - **Identity:** give the page a ledger look with tabular figures, column rules, `$18/month` and a deliberate ground colour instead of the flagged cream (Issue 5).

2. **Design intent.** The copy is plain-spoken ("18 dollars a month") while the visuals are a generic quiet-SaaS cream. Which direction is intended?
   - **Keep it quiet and paper-like:** keep the restraint, but commit to paper/ledger cues (visible rules, tabular numerals) so the cream reads as chosen.
   - **Exact and confident:** a crisper, more precise ledger aesthetic with a new ground colour and figures set large.
   - **Warmer and friendlier:** lean into "Harbor" and the small-business owner with more colour and a human tone.

3. **Scope.** There are 5 priority issues. How much should the next pass take on?
   - **P1s only:** add proof and fix the bank-trust gap (Issues 1 and 2).
   - **P1s and P2s:** also add the closing CTA, move the legal stubs, add hero microcopy and replace "files the month" (Issues 1–4).
   - **All five:** include the visual identity rework (Issues 1–5).

4. **Constraints.** Is the product claim fixed?
   - **Change freely:** "Books that close themselves" and "files the month" can both be rewritten.
   - **Keep the headline:** keep "Books that close themselves", clarify only "files the month".
   - **Copy is final:** limit changes to layout and visuals.
