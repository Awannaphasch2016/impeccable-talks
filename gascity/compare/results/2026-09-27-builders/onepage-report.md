Method: dual-agent (A: impeccable.design-reviewer step id not recorded · B: impeccable.evidence-collector step id not recorded)

# Critique: `index.html` (Harbor Ledger landing page)

Workflow `sop-2wi`. Target `index.html`, slug `index-html`, mode **Persuade**. The project has no PRODUCT.md or DESIGN.md, so the page's own code is the design authority. Neither assessment file recorded its step id, so the Method line above says so instead of guessing.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Anchor nav works. The header doesn't stick, nav shows no current section, and the CTA doesn't say it leaves for `app.harborledger.example`. |
| 2 | Match System / Real World | 3 | Plain second-person voice. "Files the month" and "the close" are bookkeeping jargon, and the legal copy switches to third-person "the customer". |
| 3 | User Control and Freedom | 3 | Nothing traps the visitor. Once they scroll down, the only way back to the nav or the CTA is to scroll up again: no sticky header and no back-to-top link. |
| 4 | Consistency and Standards | 2 | `#privacy` and `#terms` are the same two sentences word for word. The input is "the spreadsheet you already keep" in the hero and FAQ, but "pulls in your bank transactions" under Features. |
| 5 | Error Prevention | 2 | On a Persuade page the error is a wrong expectation. The visitor can't tell what data it needs (spreadsheet? bank login?), what "files" means, or what $18 buys. |
| 6 | Recognition Rather Than Recall | 3 | The page is short and easy to scan. The only CTA sits above the price and the "no card" reassurance, so the visitor has to remember the button and scroll back to it. |
| 7 | Flexibility and Efficiency | n/a | Single marketing page with no repeat-use tasks to speed up. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and restrained. The legal text is duplicated in the main flow, every section has the same weight, and the price box's hierarchy runs backwards. |
| 9 | Error Recovery | n/a | No inputs, forms or error-producing interactions here. Signup errors happen off-page. |
| 10 | Help and Documentation | 2 | A 3-item FAQ and a mailto exist. They skip what a finance buyer asks: bank-access security, supported banks and formats, what the report contains, how to cancel. |
| **Total** | | **21/32** | **Acceptable (66%)** |

Applicable maximum is 32. Scored n/a: #7 (Persuade surface) and #9 (no error-producing interactions). The detector's one finding is about palette provenance, not usability, so it doesn't move any score.

## Design Specificity Verdict

**Mostly category-interchangeable.** The copy is partly authored for this product. The composition and visual language are not.

**LLM assessment.** The headline "Books that close themselves." and the line "reads the spreadsheet you already keep and files the month" belong to this product. They name a real starting point and a real pain, and they are the page's only authored moment. Everything after them follows the stock SaaS order: hero, a 3-up "What it does" grid (h3 plus one sentence each), a single price box, an FAQ, a footer. Swap in any invoicing, payroll or CRM name and nothing breaks. Every section gets `padding: 3rem 0` and the same 1px `--line` rule, so Pricing and the legal text rank the same, and the page reads like a document, not a pitch. The system font stack and one-green palette are tasteful, but nothing in them says "ledger": no tabular numerals, no column motif, and no spreadsheet or closed month anywhere. The biggest missed opportunity is the product's own output. The hero promises a transformation from spreadsheet to closed books and never shows it.

**Deterministic scan.** `impeccable detect --json index.html` (engine 4.0.0) exited 2 with **1 finding in 1 rule: `cream-palette` (warning, slop)**. It fired on the `rgb(250, 246, 238)` page background. The detector reports this at "line 0" (page level); the real source is `--cream: #faf6ee` at `index.html:9`, applied at `index.html:25`.
- **Where they agree.** The detector and the design review reach the same conclusion from different directions. The detector flags the cream background as a reflexive "tasteful" default. The review found the palette quiet but not specific to a ledger. Neither found anything that makes the page look like Harbor Ledger rather than any calm SaaS page.
- **What the detector missed.** Every priority issue below is about structure or content, which a pattern scanner can't see: the duplicated legal text, a CTA missing where the visitor decides, the inverted price hierarchy, the contradictory input model, the missing proof. With one warning, the detector makes this page look far healthier than it is.
- **False positives.** None. The value is real and applied to `body`. With no DESIGN.md recording the cream as a deliberate choice, the warning stands. The fix doesn't have to be a new color, though: committing to the cream as a paper-ledger surface (ruled columns, tabular figures) would turn a default into a decision.

**Visual overlays.** None. This session exposes no browser tool, and no browser binary or Playwright cache is installed, so no overlay was injected, no console output was read and no screenshots were taken. Nothing is visible in a **[Human]** tab. The only fallback signal is the CLI scan above. The layout was judged from the CSS: a 780px column, and a 3-up grid that becomes one column at 640px and below.

## Overall Impression

This is a calm, honest, well-built page with one genuinely good line. It spends that line and then coasts. The hero earns curiosity. Features stay flat. Pricing, where the visitor decides, gets the weakest treatment and no button. The page ends on two identical legal paragraphs. **Biggest opportunity: show the product's output, a messy spreadsheet becoming a closed month, and put the trial button wherever the visitor has just been reassured.**

## What's Working

1. **A concrete, product-specific promise.** "Books that close themselves" plus "the spreadsheet you already keep" meets a skeptical small-business owner where they already are. It asks for no migration and uses no hype, and it's the one element no competitor could lift unchanged.
2. **A sound, accessible foundation.** Semantic landmarks (`header`, `nav`, `main`, `section`, `footer`), a real `<dl>` for the FAQ, `<address>`, underlined links, a visible 3px focus outline, correct h1 → h2 → h3 order, and a working 640px breakpoint. All text pairs pass WCAG AA: ink on cream 16.15:1, green on cream 4.93:1, white on the button 5.32:1. At about 5.8 KB with no images, fonts or JS, it loads instantly anywhere.
3. **The right reassurances.** "The trial needs no card", "nothing is billed unless you start the paid plan", "one accountant can be invited at no charge". These are exactly what this audience worries about. They're just placed where the visitor can't act on them.

## Priority Issues

The command that picks these up is `gc sling score-onepage/impeccable.conductor polish --formula`. This pack currently ships only `critique.toml`, so that formula has to be installed before the command will run.

**[P1] No call to action where the visitor decides, and the page ends without one**
- **Why it matters:** The only CTA, "Start the 14-day trial", is in the hero. Pricing, FAQ, footer and header have none. The visitors who scroll are the ones who needed convincing, and what convinces them ("no card", "nothing is billed") sits below the button. Once persuaded, they have nowhere to click. On a phone that means scrolling all the way back up one-handed. This costs conversions directly.
- **Fix:** Put the trial button in `.price-box`, right under "The trial needs no card". Repeat it after the FAQ as a closing band with one line of copy. Add a compact version to the header. Use the same label everywhere.
- **Suggested command:** `gc sling score-onepage/impeccable.conductor polish --formula`

**[P1] Privacy policy and Terms are the same two sentences, inline in `main`**
- **Why it matters:** `#privacy` and `#terms` both read "Harbor Ledger stores the spreadsheet the customer uploads and deletes it when the customer asks. The trial is 14 days…". Checking the legal links is a standard trust check before handing a product your bank data. Finding duplicated, placeholder-grade text there reads as careless at the exact moment trust is on the line. It's also the last thing on the page, so the page ends on doubt.
- **Fix:** Write distinct Privacy and Terms content. The privacy text must cover bank data, not just the spreadsheet. Move both out of the persuasive flow onto their own pages, or into a small de-emphasized block after the footer, and keep the footer links.
- **Suggested command:** `gc sling score-onepage/impeccable.conductor polish --formula` (the copy itself needs an owner; it's content, not styling)

**[P1] The page asserts the transformation but never shows it (root of the specificity verdict and the `cream-palette` warning)**
- **Why it matters:** "Books that close themselves" is a big claim made to an audience that's skeptical by trade. There's no screenshot, sample report, before/after, number or proof, and each feature is one abstract sentence. The product's most distinctive asset is missing from its own page. That's why the layout reads as a template and why the palette reads as a default.
- **Fix:** Directly under the hero, show a few rows of a messy spreadsheet beside the resulting closed-month summary or accountant report, set in `font-variant-numeric: tabular-nums`. Make the three features point at parts of that figure. Then decide the cream on purpose: commit to it as ledger paper with column rules and balanced figures, or replace it.
- **Suggested command:** `gc sling score-onepage/impeccable.conductor polish --formula`

**[P2] Pricing hierarchy is inverted and the offer is underspecified**
- **Why it matters:** `.price-box .amount` sets the plan name "Harbor" at 2rem bold and "— $18/month after the trial" as a 1rem regular `<span>`. The number the visitor came for is the smallest thing in the box, and screen readers announce "Harbor dash eighteen dollars…". Nothing says what the plan includes.
- **Fix:** Make "$18" the large figure with a small "/month" beside it and "Harbor" as a small label above. Add 3-4 inclusions (bank import, monthly close, accountant report, one free accountant seat), then "14-day trial, no card", then the CTA from the first issue.
- **Suggested command:** `gc sling score-onepage/impeccable.conductor polish --formula`

**[P2] Contradictory description of what the product ingests, and no answer on bank security**
- **Why it matters:** The hero, FAQ and privacy text say it works from "the spreadsheet you already keep". The first feature says it "pulls in your bank transactions". A visitor can't picture setup: upload a spreadsheet, connect a bank, or both? The most sensitive data flow, a bank connection, is the one the reassurance copy never mentions. The FAQ asks only "Where does my spreadsheet data go?"
- **Fix:** State the input model once, plainly (for example "Connect your bank and point it at the spreadsheet you already keep"), and match every other mention to it. Add an FAQ entry on how the bank connection works, what access it has, and how to revoke it.
- **Suggested command:** `gc sling score-onepage/impeccable.conductor polish --formula`

## Persona Red Flags

**Jordan (First-Timer, small-business owner):** "Files the month" and "the close" go unexplained, so Jordan doesn't know what gets filed or where. After reading Pricing and FAQ, Jordan finds no next step and doesn't think to scroll back to the hero button. "You can delete it whenever you ask" raises a question: ask whom? It sounds like emailing support, not a self-serve control.

**Riley (Stress Tester):** Clicks "Privacy policy", then "Terms", and gets the same paragraph twice, a broken promise in the footer. Notices that "pulls in your bank transactions" contradicts "the spreadsheet you already keep", and that nothing mentions bank security. "Accountant-ready report" names no format (PDF? CSV? a QuickBooks or Xero export?), so the claim can't be checked.

**Casey (Distracted Mobile User):** Reaches Pricing and FAQ on a phone with intent to act. The only CTA is at the top, and the header doesn't stick. The header and footer links are bare inline text with no padding, so each tap target is about 24px tall, well under 44px. On the plus side, the page loads instantly on a weak connection.

## Minor Observations

- Seven 1px hairlines at 1.37:1 contrast (`section + section`, header, footer) give the page a ruled-document feel. That could become a deliberate ledger motif. Today it reads as default separation.
- The nav offers Pricing and FAQ but not "What it does", even though `#features` has an id.
- Focus styles use `:focus` rather than `:focus-visible`, so mouse clicks also draw the outline. It's cosmetic, and the ring stays visible on cream.
- No `scroll-margin-top` on the anchored sections. That's harmless now, but it's needed as soon as the header becomes sticky.
- Links have no hover state and `.btn` has no `:active` state, only the `.btn:hover` darken.
- The 3-up grid at 780px leaves about 240px per column, so each feature wraps to 4-5 short lines. It's also the element most responsible for the template feel.
- The feature copy repeats itself: "so the close is done without extra work" restates the headline.
- No `<meta name="description">`, favicon or Open Graph tags, so shared links will preview bare.
- The footer email is the only human touchpoint. For a finance product, one sentence about who is behind Harbor Ledger would add trust.
- There's no skip link. That's acceptable with only two header links, but add one if the nav grows.

## Questions to Consider

- If the whole promise is "the spreadsheet you already keep", why doesn't a single cell of it appear on the page?
- Is the cream and hairline treatment meant to evoke a paper ledger? If yes, why not commit with tabular numerals, column rules and a figure that visibly balances? If no, what makes this look like Harbor Ledger?
- What does an owner who hates bookkeeping fear most about software that "pulls in" their bank transactions, and where on this page is that answered?
- Should the last thing a visitor reads be two identical legal paragraphs, or a closing line with a button?
- Does naming the single plan "Harbor" help anyone, or does it just take the typographic spot that belongs to "$18"?

---

> **Trend for `index-html`:** 21/32. This is the first run for this target, so there's no trend yet.
> Wrote `.impeccable/critique/2026-09-27T18-17-51Z__index-html.md`.

## Questions for the user

1. **Priority direction.** The five issues fall into three groups. Which should be fixed first?
   - **A. Conversion path:** trial CTA in the price box, a closing CTA band, a header CTA, and the inverted `$18` price hierarchy fixed.
   - **B. Trust and accuracy:** distinct Privacy and Terms moved out of `main`, one consistent spreadsheet-vs-bank input story, and an FAQ entry on bank security.
   - **C. Specificity and proof:** a spreadsheet → closed-month figure under the hero, with tabular numerals and features that point at it.

2. **Design intent: the cream background.** The detector flagged `--cream: #faf6ee` as a reflexive default (`cream-palette`), and the review found nothing in the page that says "ledger". Was the cream deliberate?
   - **A. Yes, it's paper. Commit to it:** ruled columns, tabular figures and hairlines used as a ledger motif, cream kept.
   - **B. No, it was a default. Replace it** with a palette chosen for Harbor Ledger, and keep the green.
   - **C. Keep the look as is.** Fix only structure and copy, and add the cream to `.impeccable/critique/ignore.md`.

3. **Scope.** There are 5 priority issues (3 × P1, 2 × P2) plus about 10 minor observations. How much should the next pass take on?
   - **A. The three P1s only:** CTA placement, legal text, proof figure.
   - **B. All five priority issues.**
   - **C. Everything,** including the minor observations: meta and OG tags, nav tap targets, `:focus-visible`, the missing "What it does" nav link.

4. **Constraints.** Is any copy off-limits? This matters because the legal text and the input-model fix require product facts the page doesn't state.
   - **A. The headline and hero line stay word for word.** Everything else can change.
   - **B. The legal text needs sign-off.** Restructure where it appears, but don't rewrite its content.
   - **C. Nothing is fixed.** Rewrite copy wherever the issues call for it.
