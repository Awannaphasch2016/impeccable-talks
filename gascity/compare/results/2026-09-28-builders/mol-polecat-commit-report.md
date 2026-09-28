Method: dual-agent (A: impeccable.design-reviewer step xpr-vqm · B: impeccable.evidence-collector step xpr-cc7)

# Critique: Harbor Ledger landing page (`mol-polecat-commit/index.html`)

Mode: **Persuade**. No PRODUCT.md or DESIGN.md exists, so the page is judged on its own. No ignore list applied.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | The trial lifecycle is clear (14 days, no card, nothing billed). The page never says what happens right after clicking the CTA, and the nav shows no current section. |
| 2 | Match System / Real World | 3 | "Close" and "files the month" are accounting shorthand, and the page never says where the month is filed. "18 dollars a month" is written in prose and names no currency. |
| 3 | User Control and Freedom | 3 | No card is needed and nothing auto-bills. The page doesn't say how to cancel or export on the paid plan. |
| 4 | Consistency and Standards | 3 | The tokens and CTA label are consistent. The voice switches from "you" to "the customer" in Privacy and Terms, and in pricing the h3 "Harbor" (1.125rem) is smaller than the `.price` line (1.5rem), so the hierarchy is inverted. |
| 5 | Error Prevention | 2 | Nothing tells visitors whether *their* setup is supported (spreadsheet apps, banks, countries), and the month-doesn't-match-the-bank path is never mentioned. |
| 6 | Recognition Rather Than Recall | 3 | It's all on one page, but the buying facts are scattered: the free accountant seat is only in the FAQ, and the trial-end and deletion rules are spread across Pricing, FAQ, Privacy and Terms. |
| 7 | Flexibility and Efficiency | n/a | A single linear Persuade path with no repeated expert tasks. |
| 8 | Aesthetic and Minimalist Design | 3 | Calm and uncluttered, but every section below the hero has the same weight, the legal stubs fill full sections, and the trial-end rule appears three times. |
| 9 | Error Recovery | n/a | The page has no inputs, forms or error states. The reconciliation-failure gap is scored under #5. |
| 10 | Help and Documentation | 2 | The 3-item FAQ plus an email address skips the questions buyers actually ask: security and bank access, supported tools, what "filed" produces, and cancellation. |
| **Total** | | **22/32** | **Acceptable** (69%, one point short of Good). #7 and #9 scored n/a, so the maximum is 32. |

## Design Specificity Verdict

**LLM assessment:** The copy belongs to this product and the visuals don't. Lines like "Reads the spreadsheet you already keep" and "a report the accountant can read without asking you to explain your spreadsheet" name a real audience and a real pain, and no other product could reuse them. The composition could belong to any product: a cream background, one green accent, system-ui type, stacked full-width sections split by hairline rules, a 3-column feature row, and a price set as a bold sentence. Swap the copy and it fits a note-taking app or a newsletter tool. The product is never shown: no ledger row, no bank line, no closed month, no sample report. The hairline rules hint at ruled ledger paper, but the hint looks accidental.

**Deterministic scan:** `impeccable detect --json` exited 2 with **1 finding, 1 rule, 1 file**: `cream-palette` (warning, slop category) on `mol-polecat-commit/index.html`. It is a page-level rule, so no line number is given. The source is `--cream: #faf5e6` in `:root` (line 10), used as the `body` background (line 19) and on the skip link (line 35). **It agrees with the LLM review:** the detector independently flagged the same "safe tasteful default" surface that the design review called category-interchangeable. **Not a false positive:** the match is exact, and the token is literally named `--cream`. With no brand document, nothing shows the cream is a deliberate brand choice. Everything else the review raised (missing product imagery, trust gaps, the mechanism contradiction, flat hierarchy, tap targets) is structural or about the copy, which pattern rules can't see, so the detector's single hit covers only a small part of the problem.

**Visual overlays:** None. The evidence assessor had no browser automation tool in this session (no exposed browser tool, no resolvable Playwright driver, and no `live-server` subcommand in this launcher), so overlay injection was never attempted and **no user-visible overlay exists**. The CLI scan above is the fallback signal. The design reviewer did inspect the page visually in headless Chromium at 1280×800, 1280×2200 and 390px wide.

## Overall Impression

The page is honest, accessible and restrained, and it reads like a very good wireframe with the product left out. The hero promise, "Books that close themselves", is the strongest moment on the page. Everything after it asks the visitor to take the claim on faith, just when they are being asked to hand over bank access. **Biggest opportunity: show a closed month.** One real-looking product artifact would solve the generic look, the trust gap and the unclear mechanism together.

## What's Working

1. **Copy written for a specific person.** It targets people who already keep a spreadsheet and have an accountant, and it promises a concrete, believable result: the accountant can read the report without an explanation. The terms are transparent: no card, nothing auto-billed, one free accountant seat.
2. **Accessibility and front-end craft.** It has a skip link, `aria-labelledby` sections, and visible `:focus-visible` outlines that also show on the green button. Smooth scroll respects reduced motion, buttons are at least 44px tall, and the h1 uses `clamp()`. Contrast passes AA throughout (body 15.8:1, links 4.88:1, button text 5.32:1), and it reflows at 390px with no horizontal scroll.
3. **Very low decision load.** There is one plan and one CTA label, and the nav has two links. No decision point shows more than 4 options, and nothing competes with the primary action.

## Priority Issues

**[P1] The core promise is never shown, so the page reads as a template**
- **Why it matters:** On a Persuade page for a product that handles money, visitors can't picture "a month that closes itself", so the headline reads as marketing. It is also why the detector's `cream-palette` flag fits: without a product artifact, the neutral palette and hairlines are all the identity the page has. At desktop width the right ~45% of the hero is empty cream.
- **Fix:** Put the product's own artifact in or right under the hero: a spreadsheet row matched to its bank line, a "March — closed ✓" state, or an excerpt of the accountant report. Use `font-variant-numeric: tabular-nums` and ledger-style column rules. Then either commit to the cream as a deliberate "ledger paper" choice (ruled lines, a numeric face) or replace it with a palette that comes from the product.
- **Suggested command:** `visualize` then `colorize`/`typeset` (Impeccable commands; this pack currently ships only the `critique` formula, so re-run with `gc sling experiment/impeccable.conductor critique --formula` after fixing).

**[P1] No reassurance where the visitor is asked for bank and financial data**
- **Why it matters:** The "Bank import" card asks for bank access and says nothing about how the connection works, whether it is read-only, security, or which banks and countries are supported. The data answer in the FAQ ("Your data stays in your account") has no specifics, and Privacy and Terms are one sentence each. For careful bookkeepers, trust is the whole conversion barrier, and a one-line privacy policy looks like a placeholder.
- **Fix:** Add a one-line trust note inside the Bank import card (connection method, read-only, encryption, coverage). Rewrite the data FAQ with concrete facts. Move Privacy and Terms to real pages linked from the footer.
- **Suggested command:** `clarify` (copy) and `harden` (trust and edge content).

**[P1] The mechanism is unclear and contradicts itself**
- **Why it matters:** The hero says it "reads the spreadsheet you already keep" (line 129), which suggests a live connection. Privacy says it "stores the spreadsheet the customer uploads" (line 179), which suggests a one-off upload. The page never names Excel or Google Sheets, never says where "files the month" sends anything, and never says what happens when a month *doesn't* agree with the bank. Visitors can't tell whether their setup fits, and a careful reader who catches the contradiction stops trusting the page.
- **Fix:** Add a 3-step "How it works" (connect or upload your sheet → match bank lines → close and send the report). Name the supported tools and where the month is filed. Add the mismatch path ("If something doesn't match, Harbor Ledger shows you the lines to check before filing"). Reword Privacy to describe the same single mechanism.
- **Suggested command:** `clarify`.

**[P2] Flat hierarchy after the hero, and the page ends on legal text**
- **Why it matters:** Features, Pricing, FAQ, Privacy and Terms all get the same padding, rule and h2, so the pricing decision looks no more important than the one-line Terms stub. Inside pricing, the plan name "Harbor" (h3) is smaller than the price line, and it means nothing with only one plan. The free accountant seat is only in the FAQ. The last thing a visitor sees is boilerplate, so the peak-end moment is wasted.
- **Fix:** Give pricing its own container with "$18 / month" (state the currency), a short "includes" list (bank import, monthly close, report, 1 free accountant seat) and the no-card line next to the CTA. Remove the "Harbor" label. End with a closing block that restates the promise and the no-card reassurance and repeats the CTA, then the footer.
- **Suggested command:** `layout`, then `polish`.

## Persona Red Flags

**Jordan (First-Timer):** "Close" and "files the month" are never explained, and Jordan reads "files" literally and wonders whether this files their taxes. The "Harbor" h3 in pricing looks like the name of something Jordan should recognize, and it isn't. After "Start the 14-day trial", nothing says which spreadsheet to connect, how long setup takes, or what the first screen is. The one pass: the green CTA is findable within 5 seconds above the fold.

**Riley (Stress Tester):** Riley catches the "reads the spreadsheet you already keep" (hero) vs. "stores the spreadsheet the customer uploads" (Privacy) contradiction straight away. The page never covers the edge case its own copy raises (a month that doesn't reconcile), or multiple businesses, several bank accounts, unsupported banks, or accountant access beyond the one free seat. "You can delete it" covers data, not the subscription, so cancellation and export are undefined. The trial-end rule is stated nearly word for word in both FAQ and Terms, which invites a line-by-line comparison.

**Casey (Distracted Mobile):** At 390px wide the hero CTA sits around y=280–320px, out of thumb reach, and there's no sticky or bottom CTA, so after the hero the next chance to act is two sections down. The nav links (Pricing, FAQ) are about 37px tall and the footer links (Privacy policy, Terms, email) about 26px, all under 44×44. The one pass: about 6 KB and no images, so it loads fine on slow connections.

## Minor Observations

- **Measure:** `.wide` (60rem) applies to every section, so FAQ, Privacy and Terms prose runs to 90+ characters per line at 1280px. Cap prose at about 38–42rem, as the lede (34rem) already is.
- **Dead style:** `.wrap`'s 44rem max-width is always overridden, because every `.wrap` also has `.wide`.
- **Feature row alignment:** "A report the accountant can read" wraps to two lines at desktop, so that column's body text starts lower than the other two.
- **Typography has no voice:** the system-ui stack works, but a ledger product is the obvious place for a distinctive numeric face, or at least tabular figures.
- **Voice shift:** the page says "you" everywhere else and "the customer" in Privacy and Terms.
- **No CTA in the header**, and nav hover feedback is only a change in underline thickness, with no current-section state.
- **Skip link:** `<main id="main">` has no `tabindex="-1"`, so in some browsers focus doesn't move into main.
- **Share metadata:** there's a meta description but no Open Graph tags, social image or favicon, which matters for a page meant to be shared.
- **Hairline rules** (#d9d0b8 on #faf5e6, 1.41:1) are decorative, so the low contrast is acceptable, but they are the page's only structural device.

## Questions to Consider

- If the books really close themselves, what does a closed month *look like*, and why can't a visitor see one before signing up?
- Could the month that *doesn't* agree with the bank be the most persuasive moment on the page instead of the one it avoids?
- Does the product *connect to* the spreadsheet or *take an upload* of it? Pick one and design the page around it.
- Is the cream-and-green restraint reading as "trustworthy accounting" or as "template"? What single visual choice would make this page unmistakably a ledger?

---

> **Trend for `mol-polecat-commit-index-html`:** First run for this target, no trend yet (22/32, with heuristics 7 and 9 scored n/a).
> Wrote `.impeccable/critique/2026-09-28T09-34-31Z__mol-polecat-commit-index-html.md`.

## Questions for the user

1. **Priority direction.** The critique found four problem areas: (a) the promise is never shown, so the page looks like a template; (b) no trust detail around bank and data access; (c) the unclear connect-vs-upload mechanism and the missing mismatch path; (d) flat hierarchy with a legal-text ending. Which should be fixed first?
   - **Show the product:** add a closed-month or matched-bank-line artifact to the hero (fixes (a) and gives the page an identity).
   - **Trust and clarity copy first:** the Bank import trust line, a concrete data FAQ, "How it works", the mismatch sentence, and removing the contradiction ((b) + (c)).
   - **Conversion structure:** a pricing container with "$18 / month", an includes list, a closing CTA block, and legal moved to separate pages ((d)).

2. **Design intent: the cream background.** The detector flagged `--cream: #faf5e6` as the default "tasteful" surface, and the design review found the visuals category-interchangeable. Was the cream chosen on purpose?
   - **Yes, keep it and make it intentional:** lean into ledger paper (ruled column lines, tabular or numeric type, a clear accountant's-book feel).
   - **No, replace it:** move to a palette taken from the product (e.g. crisp white with ink and one ledger accent), with the product artifact carrying the warmth.
   - **Undecided:** keep the colors for now and only add the product artifact, then re-critique.

3. **Scope.** There are 4 priority issues (3 × P1, 1 × P2) and about 9 minor observations. How much should the next pass take on?
   - **The three P1s only** (show the product, trust copy, mechanism clarity).
   - **All four priority issues**, including the pricing and closing-block restructure.
   - **Everything**, including the minor fixes (prose measure, tap targets, skip-link `tabindex`, OG metadata, feature row alignment).

4. **Constraints.** The fixes for issues (b) and (c) mean changing claims about the product itself (read-only bank access, supported spreadsheet tools, where the month is filed, the upload vs. connect mechanism). How should the fix pass handle facts the page doesn't state?
   - **Leave placeholders:** write marked `[TBD: …]` slots for facts the product team must confirm; don't invent specifics.
   - **Use the connect model:** treat "reads the spreadsheet you already keep" as true and reword Privacy to match.
   - **Use the upload model:** treat "uploads" as true and reword the hero to match.
