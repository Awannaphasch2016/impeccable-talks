Method: dual-agent (A: impeccable.design-reviewer step xpr-bcz · B: impeccable.evidence-collector step xpr-2lr)

# Critique: `factory/index.html` (Harbor Ledger landing page)

Mode: **Persuade**. No PRODUCT.md, DESIGN.md or ignore list exists, so this critique judges the page against its own claims and nothing else. The assessment files did not record their step ids, so the ids above come from this workflow's step records.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | The anchor nav has no current-section state, and the header is not sticky, so the reader loses their place after the first scroll. |
| 2 | Match System / Real World | 3 | Plain language overall, but "Monthly close" and "files the books for you" are never explained. Files with whom: the tax authority, the accountant, or an archive? |
| 3 | User Control and Freedom | 3 | The skip link and anchors work. Below the fold there is no route back to a CTA, and nothing previews what happens after "Start the 14-day trial". |
| 4 | Consistency and Standards | 3 | The nav says "FAQ" but the heading says "Questions". The voice shifts from "you" to "the customer" in Privacy and Terms. |
| 5 | Error Prevention | 2 | Nothing lets visitors check whether they qualify: which spreadsheet tools, banks, countries or business types. Unqualified visitors sign up and only then find out. |
| 6 | Recognition Rather Than Recall | 3 | The page is short and everything is visible. The one mismatch is the nav label vs. the heading, and the header has no CTA. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface. It is one linear read with no expert path. |
| 8 | Aesthetic and Minimalist Design | 3 | The hero hierarchy is strong and nothing is cluttered. Below the fold, five sections get identical weight, and the palette is the generic cream default (see detector). |
| 9 | Error Recovery | n/a | No forms, inputs or error states on the page. Signup happens off-page. |
| 10 | Help and Documentation | n/a | Persuade surface. The FAQ is judged under personas instead. |
| **Total** | | **20/28** | **Good (71%, one point above Acceptable)** |

Applicable maximum is 28, with heuristics 7, 9 and 10 scored n/a. At 71% the page clears the Good band by a single point. The structure is sound. The persuasion is thin.

## Design Specificity Verdict

**LLM assessment:** clean and honest, but interchangeable. All of the page's specificity is in the copy. The visual system could sell a note-taking app, a newsletter tool or a CRM without changing a token: one 44rem column, a cream page, one green accent, system-ui type, and a 1px rule between every section. The product's own material is a spreadsheet that becomes a matched, closed month and a readable report, and it never appears. Apart from `$18` there are no figures, no tabular numerals, no column rules and no ledger grid. "Books that close themselves." is the most distinctive line on the page, and the design does nothing to make it vivid.

**Deterministic scan:** `impeccable detect --json factory/index.html` exited 2 with **1 finding: `cream-palette`** (warning, slop category) on the body background `#faf5e8` (token `--page`, `factory/index.html:10`, applied at `:21`). It reports `line: 0` because it is a page-level finding. No other rule fired.

**Where the two agree and disagree:**
- **They agree in substance.** Assessment A, working without the detector, singled out the warm paper tone as the only visual choice that even *might* nod to the domain ("might suggest ledger paper"), then concluded that the visual layer as a whole is category-interchangeable. The detector flags the same color as the reflexive "tasteful" default. With no DESIGN.md to show the cream was chosen on purpose, and nothing else on the page (rules, grids, figures) to back up a ledger reading, the detector's reading wins: **this is not a false positive.** The cream reads as default taste, not ledger paper. It could *become* ledger paper if the page adopted real ledger structure, which is the fix in P2 below.
- **The detector caught nothing the review missed.** The review caught everything the detector structurally can't: the unshown core claim, the missing trust content, the legal stubs, and the pacing. These are content and persuasion failures, which a pattern scanner does not see.
- **Neither caught it cleanly:** the review measured footer links at about 38px tap height (`footer a { padding: 0.4rem 0 }` at `:73`). The detector did not flag it, and B scanned only a 1440×900 viewport with no mobile pass, so this rests on the review's arithmetic alone.

**Visual overlays:** Assessment B injected the detector into a headless Chromium it ran itself over a temporary localhost server. The console reported `[impeccable] 1 anti-pattern found: cream-palette` on `body`, and one overlay banner rendered. That browser was unattended and has been shut down, and the servers were stopped. **You have no live overlay to look at.** The fallback signal is the CLI result above, which matched the browser run exactly. `factory/index.html` was not modified (the md5 matched before and after).

## Overall Impression

A disciplined, accessible page with a strong promise and almost no proof. The hero and the risk reversal under the CTA are the best moments. After that the page asks a small-business owner to hand over bank data and their books, and it offers three one-sentence claims, a one-sentence privacy "policy", and an ending made of legal boilerplate. **The single biggest opportunity is to show the book closing:** put the spreadsheet → matched transactions → closed month → accountant report sequence on the page. That one move would fix the credibility gap and the missing design identity together.

## What's Working

1. **A focused offer with risk reversal at the point of action.** There is one plan, one price and one CTA label ("Start the 14-day trial"), used for both CTAs with the same URL. "No card needed." sits directly under the button, and the FAQ answers the biggest subscription fear ("What happens when the trial ends?") plainly. Nothing competes with the one action.
2. **The accessibility foundation is genuinely good.** It has a skip link, a labelled `nav`, `aria-labelledby` on every section, a visible `:focus-visible` outline, a 44px minimum-height CTA, `prefers-reduced-motion` handling, a semantic `<dl>` FAQ, 18px/1.6 body text, and strong contrast (white on `#1f7a4d` is about 5:1). There is no overflow at 390px, and the detector found no mechanical faults beyond the palette.
3. **The hero copy names the real objection.** "Reads the spreadsheet you already keep … without a new system to learn" goes straight at switching cost, which is what actually stops this audience.

## Priority Issues

Command note: this pack ships only the `critique` formula. The commands below are Impeccable skill commands. After a fix, run `gc sling experiment/impeccable.conductor critique --formula` again to measure it against this run.

**[P1] The core claim is stated but never shown**
- **Why it matters:** on a Persuade page for a trust-heavy financial product, a claim with no demonstration reads as a hope. "Books that close themselves" has no evidence anywhere on the page. The feature line "Bring in your bank transactions" (`:110`) even hints at manual work that the headline denies.
- **Fix:** add a before/after band directly under the hero. Show three or four real-looking spreadsheet rows, the bank lines they matched to, and an excerpt of the month-end report, built in HTML with tabular numerals and column rules, and link a full sample report. Rewrite the Bank import line so it says who does the matching.
- **Suggested command:** `clarify` for the copy, then `visualize` for the proof band.

**[P1] No trust content at the high-stakes moment (bank data, books, "files")**
- **Why it matters:** the visitor is deciding whether to trust software with their money records. The page gives nothing on how the bank connection works (read-only? which provider?), how data is secured, who runs the company, what "files the books" (`:114`) actually does, or what happens when a match is wrong. The accountant is named twice as a beneficiary and never quoted. A cautious owner would email support before signing up, which makes this at least P1.
- **Fix:** add a short "How your data is handled" block covering the connection type, read-only access, the deletion path and the storage location. Add a one-line definition of "files the month". Add one real accountant's quote only if one genuinely exists. Do not invent social proof.
- **Suggested command:** `harden`, then `clarify`.

**[P2] Visitors can't self-qualify**
- **Why it matters:** there is no statement of supported spreadsheet tools (Excel? Google Sheets?), banks, countries or business types. Qualified visitors hesitate, and unqualified visitors start a trial and churn. This is the one heuristic scored 2.
- **Fix:** put one line under the lede or under the hero CTA: "Works with Excel and Google Sheets, and banks in …"
- **Suggested command:** `clarify`.

**[P2] The page ends on placeholder-looking legal stubs, with no closing CTA**
- **Why it matters:** by the peak-end rule, the last impression carries the most weight. `#privacy` and `#terms` are full `<main>` sections with the same h2 weight as Pricing, and each holds one third-person sentence (`:153`, `:160`). For a finance product, a one-sentence "Privacy policy" reads as unfinished and erodes the trust the page most needs. After the FAQ there is no way to act without scrolling back up.
- **Fix:** move Privacy and Terms to their own pages, or give them footer-level treatment with real content. End `<main>` with a short closing CTA plus the "no card" reassurance, directly after Questions.
- **Suggested command:** `layout`.

**[P2] The visual system has no pacing and no domain character (confirmed by the detector's `cream-palette`)**
- **Why it matters:** every section gets identical type, padding and rules, so nothing below the fold steers the eye to the offer. The palette is the generic cream-plus-one-accent default the detector flags. Harbor Ledger is forgettable next to any other bookkeeping tool.
- **Fix:** give sections different weights, with Pricing and the new proof band heavier and legal lighter. Take the visual language from the product itself: tabular numerals, ledger column rules and a distinct face for figures. Either commit to the cream *as ledger paper* with ruled structure that earns it, or pick a background from a deliberate palette.
- **Suggested command:** `layout`, then `typeset` and `colorize`.

## Persona Red Flags

Selected for a landing page: Jordan, Riley and Casey. There is no Design Context, so no project-specific persona was derived.

**Jordan (First-Timer):** reads "At month end, Harbor Ledger files the books for you" literally and wonders whether it submits taxes. "Monthly close" is never defined. Nothing says what happens after clicking "Start the 14-day trial" (upload a spreadsheet? connect a bank?). The only help is `hello@harborledger.example` in the footer, far from the CTA. Jordan stalls at the CTA, unsure what they are committing to.

**Riley (Stress Tester):** spots that "close themselves" contradicts "Bring in your bank transactions". Asks what happens with a bookkeeper *and* an accountant, since the FAQ says "one accountant". Asks what "you can delete it" covers and whether it includes the bank transactions. Flags the one-sentence Privacy policy as unfinished. Finds nothing in Terms about cancellation, refunds or annual billing. Riley concludes the product isn't ready.

**Casey (Distracted Mobile):** at 390px the only CTAs are in the hero and inside the pricing card. The header isn't sticky and has no CTA, so from the FAQ or the footer Casey has to scroll all the way back up to act. The footer links are about 38px tall, below the 44px target. The page is light and fast, which helps.

## Minor Observations

- The nav label "FAQ" (`:88`) points to a heading reading "Questions" (`:138`). Pick one.
- The voice switches from "you" to "the customer" in Privacy and Terms.
- Emphasis is inverted: the trial and "no card" message appears four times (hero note, pricing card, FAQ, Terms), while each product mechanic appears once.
- The plan is named "Harbor" (`:128`), which adds nothing. Lead the card with what's included.
- The price has no tax or currency context and no annual option.
- `.note` ("No card needed.") is 1rem and muted, although it is the strongest reassurance on the page.
- The feature list reads as notes (bold h3 plus one sentence) rather than a considered layout.
- There is no favicon and no OG/social image. The meta description is good.
- Evidence gap: B's browser run covered only 1440×900. Neither run checked mobile width mechanically.

## Questions to Consider

- If the promise is "books that close themselves", why does the page never show a closed book?
- Could the spreadsheet itself, with its rows, columns and totals, *be* the design language, instead of a cream page that could sell anything?
- Does "files the month" mean filing with an authority? If so, the page is underselling a big claim or hiding a risky one.
- Who is the accountant here: the buyer's ally, a second buyer, or the person being partly replaced? The page mentions them twice and never speaks to them.
- Why does the page spend four sentences on the free trial and none on what happens when Harbor Ledger matches a transaction wrong?

---

> **Trend for `factory-index-html`: first run for this target, no trend yet (20/28, heuristics 7, 9 and 10 n/a).**
> Wrote `.impeccable/critique/2026-09-28T09-18-56Z__factory-index-html.md`.

## Questions for the user

1. **Where should the first pass go?** The report found three kinds of problem: missing proof of the core claim, missing trust content around bank data, and a generic visual system with no pacing.
   - **A. Proof first:** build the spreadsheet → matched transactions → closed month → report band under the hero (P1 #1). This fixes credibility first and gives the visual system its motif as a side effect.
   - **B. Trust first:** add the "How your data is handled" block, define "files the month", and replace the one-sentence Privacy and Terms stubs (P1 #2 and P2 #4).
   - **C. Visual identity first:** re-pace the sections and bring in ledger typography and figures (P2 #5). Choose this only if the proof and trust copy are waiting on facts you don't have yet.

2. **Was the cream background (`#faf5e8`) a deliberate brand choice?** The detector flagged it as the default "tasteful" palette, and the review found nothing else on the page backing a ledger reading.
   - **A. Keep it, and make it ledger paper:** add column rules, tabular numerals and a figure face so the cream earns its place.
   - **B. Replace it:** pick a background from a deliberate palette (for example a cooler paper, or a bank-statement white with a strong ink and green system).
   - **C. It's intentional brand, leave it:** say so, and it goes into `.impeccable/critique/ignore.md` so later runs drop the finding.

3. **What does "files the books" / "files the month" actually do?** The answer changes both the copy and how much trust content the page needs.
   - **A. It submits filings to a tax authority.** That's a big claim, so it needs its own explanation, the jurisdictions covered, and error-handling reassurance.
   - **B. It closes and archives the month and produces the accountant report.** Reword to "closes the month" and drop "files".
   - **C. It hands the closed month to the accountant.** Reframe around the accountant handoff and speak to the accountant directly.

4. **How much should the plan cover?** The report lists 5 priority issues (2 P1, 3 P2) plus 9 minor observations.
   - **A. The two P1s only** (proof band and trust block).
   - **B. All five priority issues,** minor observations left for polish.
   - **C. Everything, including the minor observations** (FAQ/Questions label, voice, the "Harbor" plan name, footer tap targets, favicon/OG image).
