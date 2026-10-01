Method: dual-agent (A: impeccable.design-reviewer step smc-vjm · B: impeccable.evidence-collector step smc-dgp)

# Critique: Harbor Ledger landing page (`index.html`)

Target `index.html` · slug `index-html` · mode **Persuade** · design context: none (no PRODUCT.md or DESIGN.md, so the page's own code is the only design authority) · ignore list: none.

> **Caveat on evidence.** Neither assessor could render the page. No browser binary or browser-automation tool exists in this environment. Every layout judgement below, including the 375px and wide-viewport claims, comes from reading the CSS, not from screenshots. The deterministic scan ran fully.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Static page, and anchor jumps work. The primary CTA leaves for another domain with no cue, and the nav shows no current section. |
| 2 | Match System / Real World | 3 | Mostly plain language. "Files the month" and "closes the books" are accounting shorthand the page never defines, and the plan name "Harbor" means nothing. |
| 3 | User Control and Freedom | 3 | The skip link, anchor nav and native back all work, and nothing traps the reader. The brand is a `<span>`, not a link back to the top. |
| 4 | Consistency and Standards | 2 | `#terms` repeats `#privacy` word for word. The footer's "Privacy policy" link lands on two sentences. The hero's "without a new system" contradicts the "imports your bank transactions directly" feature. |
| 5 | Error Prevention | 2 | "No card" and "nothing is billed" prevent billing surprises. But both CTAs point at a domain that doesn't resolve, and bank access, data after the trial, and deletion are left ambiguous. |
| 6 | Recognition Rather Than Recall | 3 | A short page, with trial terms repeated beside each CTA. The header nav leaves out Features. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: there are no expert workflows to speed up. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and focused. Spoiled by the duplicated legal block and a cramped three-column grid inside a 44rem column. |
| 9 | Error Recovery | n/a | No inputs or error-producing interactions on this surface. The dead-link risk is scored under H5. |
| 10 | Help and Documentation | n/a | Persuade surface. The FAQ is judged under H2, H5 and H6. |
| **Total** | | **19/28** | **Acceptable (68%)** |

Applicable maximum: 28. Heuristics scored n/a: 7, 9, 10.

## Design Specificity Verdict

**Verdict: the words are authored and the design is interchangeable.** Swap the copy and this page sells a CRM, a VPN or a note app.

**LLM assessment (A).** The copy belongs to one product: "Books that close themselves," "the spreadsheet you already keep," "a report your accountant can read," "the trial needs no card." It is restrained and honest. None of the visual layer depends on that product. The page is a system-font stack on cream, one green button, a three-up feature list, a single price card, an FAQ, and legal and footer blocks: the standard SaaS landing template. The product is never shown. A spreadsheet, a closed month and an accountant-ready report are all concrete things that could be pictured, and none appears, so the copy has to carry all of the persuading on its own.

**Deterministic scan (B).** `impeccable detect --json index.html` exited 2 with **1 finding, 1 rule, 1 file**:

- `cream-palette` (warning, category *slop*): "cream/beige page background rgb(250, 246, 238)".
- The detector reports `line: 0` because this is a page-level check. B traced it by hand to `--cream: #faf6ee` (index.html:10). `body { background: var(--cream) }` uses it at index.html:28 and `.skip-link` at index.html:52.

**Where the two agree.** They reached the same conclusion from opposite directions. A called the palette a hint that "only reads as calm fintech." The detector flags the same cream as the reflexive default "tasteful" surface. **This is not a false positive.** The value is really cream, the token is literally named `--cream`, and nothing in the repo records it as a deliberate brand choice.

**Where they differ, and the resolution.** The detector's remedy is to change the colour. A's is to *commit* to it: cream plus ledger green is one step from ledger paper, which would mean ruled rules, tabular figures in the price, and a pricing card styled like a closing statement. **The finding holds for the page as built.** The cream becomes authored only if the rest of the page commits to the ledger idea. Left alone, the detector is right.

**What only the review caught.** The detector's coverage is narrow: one rule fired, and it checks visual patterns only. It says nothing about the dead CTAs, the duplicated legal text, the self-contradicting hero, or the CSS specificity bug in the price card. All of the P0 and P1 issues below come from the review alone.

**Visual overlays.** None. The mutable-injection preflight could not run because there is no browser, so the live server was never started and `detect.js` was never injected. No user-visible overlay exists for this run; the CLI scan above is the fallback signal.

## Overall Impression

The page is honest, quiet and fast: one price, no card, no dark patterns, 7.5KB, and a sound accessibility base. It is also unfinished where a finance buyer looks hardest:

- The sign-up goes nowhere.
- The Terms are a copy of the Privacy text.
- The riskiest claim, connecting your bank so the software can close your books, gets no evidence and no reassurance.

**Biggest opportunity:** show the product. A small "your spreadsheet in → closed month and accountant report out" visual would give the design an identity, settle the hero's contradiction, and supply the trust evidence the page lacks, all in one move.

## What's Working

1. **Honest, specific, low-pressure commercial copy.** One plan at $18/month, a 14-day trial with no card, and "nothing is billed unless you choose," stated twice. No inflated claims. For a buyer handing over financial data, this restraint is an asset. Keep it through every revision.
2. **A solid accessibility foundation.**
   - Skip link, landmarks, `aria-labelledby` sections and a correct h1 → h2 → h3 outline.
   - A 3px `:focus-visible` outline and 44px minimum button height.
   - Every measured contrast passes AA: ink on cream 16.15:1, green links on cream 4.93:1, white on the green button 5.32:1 (7.66:1 on hover).
3. **Tight focus and a tiny footprint.** One action repeated with the same label, no scripts, no webfonts, no images. Cognitive load is low (0 of 8 checklist items fail), and the page loads instantly on any connection.

## Priority Issues

**[P0] Both sign-up CTAs point to a domain that doesn't resolve**
- **What:** Both "Start the 14-day trial" buttons link to `https://app.harborledger.example/signup`. `.example` is a reserved TLD, and the packet confirms it doesn't resolve.
- **Why it matters:** The page exists to convert, and its only conversion path ends in a browser DNS error. Nothing else here matters until this works.
- **Fix:** Point both CTAs at the real sign-up. If none exists yet, change the action to a working waitlist or `mailto:` and relabel it to say what happens ("Join the waitlist").
- **Suggested command:** `gc sling score-mol-polecat-commit/impeccable.conductor polish --formula`

**[P1] The Terms section is a word-for-word copy of the Privacy section, and neither is a real policy**
- **What:** `#terms` repeats `#privacy`. The footer's "Privacy policy" link lands on a two-sentence section.
- **Why it matters:** The product asks for bank transactions and accounting data. Legal text is where cautious buyers and their accountants go to check trust. A visible copy-paste error there says nobody has checked, which does more damage than having no Terms link at all.
- **Fix:** Write real Terms, or remove the Terms section and its footer link until they exist. Move the full policies to their own pages, and keep a one-line plain-language summary on the landing page, labelled as a summary and linked to the full text.
- **Suggested command:** `gc sling score-mol-polecat-commit/impeccable.conductor polish --formula`

**[P1] The page asks for high-stakes trust, shows no evidence, and its only visual choice is the category default**
- **What:** Bank connection and an automatic month-end close are presented with:
  - no product visual and no sample output;
  - no line on security or bank access;
  - no human review step and no social proof.

  The one visual decision the page makes, the cream background, is the default the detector flags (index.html:10).
- **Why it matters:** In Persuade mode, reassurance matters most at the high-stakes moment. Here that moment ("imports your bank transactions directly," "closes the books for you") is the least supported part of the page. And because the design is generic, nothing visual tells the reader this is a real, specific product.
- **Fix:**
  - Show the artifact: a spreadsheet-in → closed-month-report-out visual, or a real excerpt of the accountant report.
  - Add one line on bank access: read-only, which provider, no stored credentials.
  - Say whether the user approves the close before it is filed.
  - Then either commit the palette to the ledger idea (ruled rules, tabular figures, a statement-styled price card) or replace it.
- **Suggested command:** `gc sling score-mol-polecat-commit/impeccable.conductor polish --formula`

**[P2] The core message contradicts itself and leans on undefined terms**
- **What:** The hero promises it "reads the spreadsheet you already keep… without a new system to learn," yet the first feature is a direct bank connection. The page never says what "files the month" means (filed where, and with whom?) or which spreadsheets it supports (Excel, Google Sheets, CSV).
- **Why it matters:** First-time readers take claims literally. A contradiction in the first two sections makes them doubt the rest.
- **Fix:** State the loop in one concrete line near the hero, for example: "Connect your bank, point us at your Google Sheet, and each month you get a closed ledger and a PDF for your accountant." Rename the features to match those three steps.
- **Suggested command:** `gc sling score-mol-polecat-commit/impeccable.conductor polish --formula`

**[P2] The page ends on duplicated legal text, with no closing CTA and two key FAQ questions unanswered**
- **What:** After the FAQ come two identical legal blocks and a footer, with no final call to action. The FAQ skips what happens to the data when the trial ends, and whether users can delete it themselves ("you can delete it whenever you ask" sounds like emailing support).
- **Why it matters:** This is the peak-end problem. The most engaged reader, the one who scrolled everything, gets the weakest content and no next step. Pricing is the emotional peak, and the page ends in a valley.
- **Fix:**
  - Add a closing CTA block right after the FAQ that repeats the price and "no card."
  - Answer data-after-trial and self-serve deletion in the FAQ.
  - Move the legal summaries into the footer.
- **Suggested command:** `gc sling score-mol-polecat-commit/impeccable.conductor polish --formula`

## Persona Red Flags

**Jordan (Confused First-Timer)**
- Reads "closes the books" and "files the month" and can't tell whether "filing" involves the tax authority.
- Nothing on the page shows that the product works with *Jordan's* spreadsheet.
- Nothing says who the product is for (freelancer, small business, bookkeeper), so Jordan can't place themselves.
- Clicks "Start the 14-day trial" with no hint of what comes next (account creation? connecting a bank straight away?) and lands on a DNS error. **Abandons at the first click.**

**Riley (Deliberate Stress Tester)**
- Opens Terms and finds the Privacy text again, word for word.
- Clicks the CTA: it looks like it works and fails silently off-site.
- Logs the mismatch between "delete it whenever you ask" and the lack of any self-serve control.
- Asks what "invite *one* accountant" means for someone with two, or with a bookkeeper as well.
- Notices "no new system" conflicting with bank import, and that nothing covers data retention after the trial. **Concludes the page was never proofread and distrusts the product that handles their money.**

**Casey (Distracted Mobile User)**
- Header and footer nav links are inline text about 24px tall (from CSS, not measured), below the 44×44 touch-target guideline and only 1.25rem apart.
- The hero CTA sits in the top half of the first screen, outside the thumb zone. There is no sticky or bottom CTA, and the next CTA comes only after the features.
- On the plus side, there are no heavy assets and the single column below 40rem is simple.

## Minor Observations

- **Price card CSS specificity bug.** `.price-card p` (0,1,1) overrides `.price` (0,1,0). The intended `margin: 0 0 0.25rem` becomes `0 0 1.25rem`, which pushes "$18/month" away from its qualifier, "After your 14-day trial." Fix: use the selector `.price-card .price`.
- **Cramped feature columns at 40rem and up.** Three columns in a 44rem wrap leave about 12.5rem (~200px) each, roughly 25–30 characters per line, so "A report your accountant can read" wraps to 2–3 lines. Widen this section, or stack the features as a numbered "how it works" sequence, which also serves the P2 fix.
- **No CTA in the header.** Two anchor links waste the most-scanned spot on the page.
- **Headings name the section type** ("Features," "Pricing," "FAQ") and add nothing to the argument.
- **The plan name "Harbor" repeats the brand** and tells the reader nothing about what's included.
- **Proportional figures in the price.** Tabular or old-style numerals would be a cheap typographic signature for a ledger product.
- **Inconsistent link hover.** Body links *lose* their underline on hover while nav links *gain* one.
- **The CTAs don't signal an off-site destination** to screen-reader users. There is no `:active` state, and button hover changes colour only.
- **"14-day trial" appears six times.** That's fine beside the CTAs and padding in the legal text.
- **Email is the only contact**, with no response-time hint or sign of a human on the other end.
- **No print styles**, though an accountant-facing product may well get printed.
- **Detector location.** `cream-palette` reports `line: 0`. The real lines are index.html:10, 28 and 52.

## Questions to Consider

- The whole promise rests on "the spreadsheet you already keep," so why is there no spreadsheet on the page?
- Would an accountant trust "closes the books *for you*"? Would "prepares your close for one-click approval" convert better *because* it gives up some autonomy?
- The cream-and-green palette almost says "ledger paper." What would the page look like if it committed: ruled lines, tabular figures, a pricing card styled like a closing statement?
- Who keeps their books in a spreadsheet today: a freelancer, a two-person shop, a side business? What changes if the first line names them?
- On a trust-sensitive finance page, the privacy and terms text is the least finished part. What does that tell the reader?

---

> **Trend for `index-html`: 19/28. First run for this target, no trend yet.**
> Wrote `.impeccable/critique/2026-09-27T19-57-38Z__index-html.md`.

## Questions for the user

The report lists 5 Priority Issues (1 P0, 2 P1, 2 P2), so these questions are required.

1. **Is the `app.harborledger.example/signup` link a placeholder, and what should the CTAs do today?** (P0)
   - A: A real sign-up URL exists. Supply it and both CTAs will point there.
   - B: There is no sign-up yet. Turn both CTAs into a working waitlist or `mailto:` labelled "Join the waitlist."
   - C: Leave it as a known placeholder and treat the P0 as out of scope for this pass.

2. **Which problem should be fixed first?**
   - A: **Trust hygiene.** Fix the dead CTAs and the Terms-copied-from-Privacy block, and add real policy pages or remove the stubs (P0 + P1).
   - B: **Evidence of the product.** Add a spreadsheet-in → accountant-report-out visual, a bank-access line and an approve-before-close statement (P1).
   - C: **Message clarity and page ending.** Settle the "no new system" vs. bank-import contradiction, define "files the month," and add a closing CTA after the FAQ (both P2s).

3. **Is the cream background (`--cream: #faf6ee`, flagged by the detector as a reflex default) a deliberate brand choice?**
   - A: Commit to it as ledger paper: ruled rules, tabular figures, a pricing card styled like a closing statement.
   - B: Replace it with a deliberate palette built around the ledger green.
   - C: Keep it as it is. Treat the detector finding as accepted and add it to `.impeccable/critique/ignore.md`.

4. **How much should the next pass take on, and is anything off-limits?**
   - A: P0 + P1 only (3 issues), with the copy's wording left untouched.
   - B: All 5 priority issues, with copy edits allowed where the hero contradicts the features.
   - C: All 5 priority issues plus the minor observations (price-card specificity bug, cramped feature grid, header CTA, link-hover consistency).
