Method: dual-agent (A: impeccable.design-reviewer step xpr-vjh · B: impeccable.evidence-collector step xpr-2s6)

# Critique: Harbor Ledger landing page (`impeccable-build/index.html`)

Mode: **Persuade**. No PRODUCT.md or DESIGN.md exists, so the page was judged on its own terms. No ignore list. Neither assessor had a browser, so nothing here comes from rendered pixels. Assessment A read the full source and worked out both breakpoints. Assessment B ran the mechanical detector. I spot-checked the synthesis claims against the source (placeholder hrefs, hero ledger rows, section padding).

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | No current-section state in the nav. The CTA leaves the site with no hint of the next step. The pricing double-rule animation plays on load, off-screen, and nobody sees it. |
| 2 | Match System / Real World | 3 | The ledger metaphor is fluent, but "files the month" is never defined (it reads as a tax filing). The hero "total" ($0.00) is not the sum of its column. |
| 3 | User Control and Freedom | 3 | Skip link, anchors and Back all work. The header offers only Pricing and FAQ: no Features link and no CTA. |
| 4 | Consistency and Standards | 3 | "Harbor plan" in the hero vs "Harbor / One plan" in pricing. `.total` means "sum" in one place and "the plan" in another. The page says "reads your spreadsheet" but Privacy says "upload". |
| 5 | Error Prevention | 3 | The surprise-charge fear is headed off well ("Card needed to start: None"). But both CTAs point at a `.example` host. |
| 6 | Recognition Rather Than Recall | 3 | Price and terms are always visible. The product itself has to be imagined: no supported sources, no closed month, no report. |
| 7 | Flexibility and Efficiency | n/a | A Persuade surface with one linear read and one action. Accelerators do not apply. |
| 8 | Aesthetic and Minimalist Design | 3 | Restrained, with one accent and one CTA style. But the trial terms appear 4 times and two of the three features repeat the lede, which uses up the space proof should fill. |
| 9 | Error Recovery | n/a | No form, input or stateful control on the page. Signup happens off-site. |
| 10 | Help and Documentation | 2 | The FAQ answers three easy questions and none of the hard ones (sources, bank security, cancelling, data after the trial, who runs this). The only contact is a placeholder address. |
| **Total** | | **23/32** (72%) | **Good, low end.** Heuristics 7 and 9 scored n/a. |

The scores are Assessment A's and I let them stand. The detector's only findings are layout false positives (below), so nothing it found moves a score. The placeholder links are a release blocker, but they are a content-integrity problem, not a design-system failure, so I kept them out of the heuristic scores and made them the top priority issue instead.

## Design Specificity Verdict

**LLM assessment.** The visual language is authored for this product. The content and structure are category-interchangeable. The page is laid out as a ledger. It has ruled `dl` rows with ink rules opening each group, tabular right-aligned figures, section headings in a 4/12 margin column beside an 8/12 ruled column, and a paper-and-ink palette with a single ledger green. The hero worksheet closes with an accountant's double rule that draws itself on load, which stages "books that close themselves" as an event. That is the best idea on the page, and no other product could reuse it unchanged. Underneath, though, the skeleton is stock SaaS: hero → 3 features → pricing → FAQ → legal → footer. The copy could sit on any "spreadsheet to books" tool. The page never shows the product doing its one job, never names its audience, and spends its one signature device on trial terms rather than on a closed month. So the styling makes an authored promise that the content never backs up.

**Deterministic scan.** `impeccable detect --json impeccable-build/index.html` exited 2 with **4 findings, 1 rule (`cramped-padding`, warning), 1 file**, all reported at line 0. By document order and snippet shape they map to `section#features` (L310), `section.pricing#pricing` (L330, "border-top+bg on all sides"), `section#faq` (L343) and `section.legal` (L363).
- **All 4 are false positives.** `.section` carries `padding-block: clamp(2.5rem, 6vw, 4.5rem)` (L189), which is 40–72px under the top rule. `.section.legal` keeps 32px (L235). The children sit in `.wrap`, which has `padding-inline: var(--gutter)`, 16–48px. The rule appears to measure the child `.wrap`/`h2` against the section's border box without crediting the section's own padding. "On all sides" for pricing contradicts the gutter padding outright. This conclusion rests on source reading only, not rendered geometry.
- **What the detector missed.** Everything that matters here. Placeholder conversion URLs, the ledger that doesn't add up, fourfold repetition, the missing trust content, load-time animation of an off-screen element, and the lack of a closing CTA are all content, IA or timing problems. No static pattern rule sees them.
- **The detector and the LLM agree** on the palette. The `cream-palette` rule did not fire on the `#f6f0e1` / `#ede5cf` paper tones, and Assessment A judged the paper palette a motivated, product-specific choice (ledger stock) rather than a default warm-neutral. I agree with both. Here the cream means ledger paper, not decoration.
- **Contrast** (from A's calculations; the detector reported nothing): every live text pair passes AA. Green on paper is 4.68:1, white on green 5.32:1, ink-soft on paper-deep 7.95:1.

**Visual overlays.** None are available. There was no browser tool in this session, so neither `detect.js` injection nor a live server ran, and nothing is highlighted in a **[Human]** tab. The fallback signal is the complete CLI scan above.

## Overall Impression

This is a well-crafted page with a real idea: bookkeeping rendered as a bookkeeper's page, ending in a double rule. It is persuasive about exactly one thing, that the trial costs nothing, and it says it four times. It is silent about everything a skeptical owner needs before handing over bank data. It also ships with a signup button that goes nowhere. **Biggest opportunity:** point the ledger device at the product's output. Show a messy month going in and a closed, double-ruled month coming out, so the headline becomes a demonstration instead of a slogan.

## What's Working

1. **The ledger is the layout, not a decoration on it.** Ruled rows, tabular right-aligned figures, margin-column headings and paper stock make the metaphor structural. The self-drawing double rule under the hero total is a genuine piece of product character.
2. **The hero worksheet answers the commitment fear before it forms.** "Card needed to start: None" and "Billed if you do nothing: $0.00" sit right beside the CTA, in the product's own format. That is honest, specific and persuasive.
3. **Solid craft floor.** There is a skip link, visible `:focus-visible` rings, 44px+ nav targets, a full-width button under 26rem, reduced-motion respected for the animation, smooth scroll and transitions, one accent color, AA contrast on every text pair, semantic `dl` ledgers, and no scripts or images, so it is light on a slow connection.

## Priority Issues

**[P0 at release] The conversion path and the only contact route point to placeholder hosts**
- **What:** Both "Start the 14-day trial" buttons (L296, L338) link to `https://app.harborledger.example/signup`. The only contact is `mailto:hello@harborledger.example` (L384). An owner comment flags the email. Nothing flags the signup URL.
- **Why it matters:** On a Persuade page the CTA is the whole job. Shipped like this, every convinced visitor hits a dead host and cannot even write in. Task completion is blocked.
- **Fix:** Replace both hrefs with the real signup and contact addresses before release. Until then, add an owner comment on each signup `href` that matches the one on the email, so no later editor misses it.
- **Suggested command:** `gc sling experiment/impeccable.conductor harden --formula`

**[P1] The page claims the product's result but never shows it**
- **What:** The lede says it "reads the spreadsheet you already keep and files the month". Nothing shows a spreadsheet going in, a closed month coming out, or the "report your accountant can read". The page's one visual device is spent on trial terms.
- **Why it matters:** Persuasion depends on belief. The visitor can't tell whether their sheet qualifies, or whether "files" means closed books or a tax filing. The confident H1 reads as a slogan.
- **Fix:** In "What it does", build a before/after ledger. Show 3–4 raw rows from a typical sheet, then the closed month (categorized totals, reconciled to bank, double rule), then a two-line excerpt of the accountant report. Name the sources (e.g. Excel, Google Sheets, CSV). Define "files the month" in one plain sentence.
- **Suggested command:** `gc sling experiment/impeccable.conductor clarify --formula`

**[P1] No reassurance at the highest-trust moment**
- **What:** "Bank import" gets one vague sentence. Privacy is two sentences. Nothing covers read-only access, the connection provider, encryption, where data lives, export or deletion, what happens after the trial lapses, or who runs the company. The footer's "Privacy policy" lands on that two-sentence row.
- **Why it matters:** Connecting a bank and handing over the books is a far bigger ask than $18/month. Visitors who would happily pay will still leave if they can't tell who holds their financial data.
- **Fix:** Add a "Your data" ledger of 4 rows at most: bank access (read-only, via which provider), storage and encryption, export and deletion, data after the trial. Add a real company or person identity. Point "Privacy policy" at an actual policy.
- **Suggested command:** `gc sling experiment/impeccable.conductor clarify --formula`

**[P2] Repetition takes the space substance should have, and the hero ledger doesn't add up**
- **What:** The trial terms appear 4 times: the hero worksheet, the pricing ledger, FAQ "What happens when the trial ends?", and the Terms row. "Monthly close" repeats the lede word for word ("no new system to learn"). "A report your accountant can read" is followed by "A plain report your accountant can open and read". In the hero, a `.total` row of $0.00 sits under 14 days / None / $18.00, which is not a sum.
- **Why it matters:** Each repeat makes the visitor re-read for new information and signals there is nothing else to say. A ledger that doesn't foot, shown first to an audience that includes accountants, undercuts the page's whole metaphor.
- **Fix:** Keep the trial terms in the hero worksheet and the pricing ledger only. Give each feature one concrete fact (what it connects to, what it produces, how long it takes). Replace the duplicate FAQ with real questions: which spreadsheets, cancelling, a second accountant, data after the trial. Relabel the hero's last row so it isn't styled as a sum (e.g. a "due today" row set off by the double rule, not `.total`), or make the column actually foot.
- **Suggested command:** `gc sling experiment/impeccable.conductor distill --formula`

**[P2] The page ends on fine print, and its signature moment plays to an empty room**
- **What:** There is no CTA after the FAQ and none in the header. The page ends on Privacy, Terms and a placeholder email. Both `close-rule` animations fire 0.25s after load and last 1.1s (L169). The pricing one is off-screen, and below 52rem the hero worksheet stacks under the CTA and below the fold, so mobile visitors miss that one too.
- **Why it matters:** By the peak-end rule, the last impression is "Terms: The trial is 14 days." The most memorable device is wasted where it should land hardest.
- **Fix:** Add a closing band after the FAQ with one line restating the promise, the final double-ruled total, and the CTA. Trigger `close-rule` on scroll into view, keeping the reduced-motion fallback, or drop it from pricing so the hero and the closing band own it. Add a compact "Start trial" link to the header.
- **Suggested command:** `gc sling experiment/impeccable.conductor animate --formula`

(Only the `critique` formula is installed in this pack today. The commands above name the Impeccable command each fix belongs to.)

## Persona Red Flags

Personas selected for a landing page: Jordan, Riley, Casey. CLAUDE.md has no `## Design Context`, so no project-specific persona was generated.

**Jordan (confused first-timer).** Jordan reads "files the month" as a tax filing and hesitates. There is no list of supported spreadsheet tools or formats, so Jordan can't tell whether their Google Sheet qualifies. "Start the 14-day trial" leaves for another domain with no hint of what comes next (account? upload? bank connection?). The only help route is `hello@harborledger.example`. Jordan leaves at the CTA.

**Riley (stress tester).** The first ledger on the page doesn't foot: 14 days / None / $18.00 "total" $0.00. The data model contradicts itself: the lede says the product "reads the spreadsheet you already keep", Privacy says it "stores the spreadsheet you upload", and "Bank import" is a third path, with no word on which one stays in sync. "One accountant can be invited at no charge" implies a charge for a second one that the single-plan pricing never states. Cancelling, data after the trial lapses, and multiple businesses are all unanswered. "Privacy policy" and "Terms" resolve to one or two sentences each, which Riley reads as unfinished or evasive.

**Casey (distracted mobile user).** Below 52rem the reassurance ($0.00, no card) sits after the button and below the fold, and its draw-in animation has already finished by the time Casey gets there. Once convinced at the bottom of the page, Casey finds no CTA after the FAQ and none in the header, so they must scroll back to pricing. On the plus side: a full-width button, 44px nav targets, and a page with no images or scripts that loads fast on a weak connection.

## Minor Observations

- **Fallback typography:** the stack leads with Avenir Next / Segoe UI. On Linux and Android the 800-weight headings fall back to Helvetica or Arial and lose character. Self-host a face or pick a closer fallback.
- **Latent contrast failure:** green link text on `--paper-deep` would be 4.23:1, below AA. No link sits there today, but any future inline link in the pricing band or worksheet would fail.
- **Hairline visibility:** the `--rule` hairline (#b9ad8f) is 1.96:1 on paper, and it carries most of the row structure. Low-vision users may read the ledgers as unruled text.
- **CSS cleanup:** `.section` declares `padding-block` twice (L189). `.worksheet` padding is overridden by a second `.worksheet { padding-bottom }` (L186). `.legal .wrap` is redeclared as `1fr` in the media query with no effect.
- **Headings:** the worksheet title "The trial, line by line" is a `<p>`. `aria-labelledby` covers screen readers, but heading navigation skips the page's key reassurance.
- **Nav:** there is no current-section state and no Features link, so two of five content sections can't be reached from the header.
- **Print:** `@media print` changes only the background. Pricing and terms are exactly what this audience prints for their accountant, so hide the header and nav and tighten the layout.
- **Theme:** `color-scheme: light` only. That is deliberate for the paper metaphor and acceptable, but worth a conscious decision.

## Questions to Consider

- The headline promises books that close themselves. Why does the page show a trial that costs nothing and never a closed book?
- Who is this for: a freelancer with a Google Sheet, a café owner, or their bookkeeper? Choosing would change every sentence.
- Would an accountant trust a product whose first ledger doesn't add up?
- What if the whole page *were* one month being closed, with rows accumulating as you scroll, reconciling at pricing, and the double rule landing on the final CTA?
- Is "no new system to learn" true when step one is creating an account on a new web app and connecting a bank? What are the visitor's first ten minutes, and why aren't they on the page?

---

> **Trend for `impeccable-build-index-html`:** First run for this target, no trend yet (23/32, heuristics 7 and 9 n/a).
> Wrote `.impeccable/critique/2026-09-28T09-36-54Z__impeccable-build-index-html.md`.

## Questions for the user

1. **Priority direction.** The critique found three kinds of problem: a broken conversion path (placeholder signup and contact hosts), missing proof of what the product does (no before/after, "files the month" undefined), and missing trust content (bank access, data custody, who runs the company). Which should the first pass tackle?
   - A. Release blockers first: real signup and contact URLs, a real privacy policy link.
   - B. Proof first: a before/after ledger that shows a month being closed, plus supported sources.
   - C. Trust first: a "Your data" ledger and company identity next to Bank import and Privacy.

2. **Design intent: what the ledger device is for.** Right now the page's signature double rule is spent on trial terms ($0.00 billed), and the hero "total" doesn't foot. Was centering the page on "the trial is free" deliberate?
   - A. Yes, keep the trial as the hero story. Just make the hero ledger arithmetically honest and move the product proof lower.
   - B. No, move the double rule to the product's output (a closed month) and demote the trial terms to pricing.
   - C. Go further: make the whole page one month being closed, with rows accumulating down the page and the double rule landing on a closing CTA.

3. **Scope.** There are 5 priority issues (1 P0, 2 P1, 2 P2) plus 8 minor observations.
   - A. The P0 and both P1s only (URLs, product proof, trust content).
   - B. All 5 priority issues, including the de-duplicated copy, closing CTA and scroll-triggered animation.
   - C. Everything, including minor polish (font fallback, print stylesheet, heading semantics, CSS cleanup).

4. **Constraints.** Assessment A and I both rated the visual system (paper palette, ruled rows, margin-column headings, single green accent) as the page's strength. Should it be held fixed?
   - A. Yes, the visual system is locked. Change only copy, content and IA.
   - B. Mostly locked. Allow new ledger sections and a header CTA, but no palette or type changes.
   - C. Open. Typography and palette may change too (e.g. to fix the Linux/Android font fallback).
