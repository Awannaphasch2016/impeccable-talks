Method: dual-agent (A: impeccable.design-reviewer step smd-8wa · B: impeccable.evidence-collector step smd-v7z)

# Critique: Harbor Ledger landing page (`index.html`)

Mode: **Persuade**. No PRODUCT.md or DESIGN.md exists, so the page's own CSS and markup are the only design authority. Both assessments worked from source only, because no browser automation was available in this environment and nothing was rendered.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Anchor nav and native `<details>` give clear feedback. The hero CTA doesn't say what happens next (bank login? upload?), and it leaves for `app.harborledger.example` without warning. |
| 2 | Match System / Real World | 2 | The main promise relies on bookkeeping jargon: "close" the books and "files the month" (filed with whom?). The audience, people who keep books in a spreadsheet, may not use those words. |
| 3 | User Control and Freedom | 3 | A short page, hash anchors that keep Back working, and collapsible FAQ. There is no Sign in for returning customers and no CTA after the FAQ. |
| 4 | Consistency and Standards | 3 | The visual system is consistent but the copy isn't: "reads the spreadsheet you already keep" vs "stores the spreadsheet you upload", "$18 / month after the trial" vs "only if you choose the paid plan", plan "Harbor" vs product "Harbor Ledger". |
| 5 | Error Prevention | 3 | Billing is spelled out well (no card, nothing billed without opting in), but "$18 / month after the trial" still reads like auto-renewal. |
| 6 | Recognition Rather Than Recall | 3 | Labelled nav and one consistent CTA label. The main reassurance ("no card") sits in the pricing card, not next to the first CTA. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface with no repeat-use workflow to speed up. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and undecorated, but flat: the features block has no heading, the plan name is a plain `<p>`, and the one-sentence Privacy and Terms sections get the same weight as Pricing. |
| 9 | Error Recovery | n/a | No inputs, forms or async actions on the page, so no error state is possible here. Signup errors happen in the external app. |
| 10 | Help and Documentation | 2 | Three FAQ entries and a mailto link. The questions a visitor about to hand over bank data would ask go unanswered: which banks, read-only or not, file formats, how to cancel, what the accountant sees. |
| **Total** | | **22/32** | **Acceptable** (69%, just below the 70% Good line) |

Applicable maximum: 32. H7 and H9 were scored n/a.

## Design Specificity Verdict

**LLM assessment:** **The copy is specific but the visuals are generic.** The structure is the standard SaaS starter: hero with one CTA, three-column feature grid, one pricing card, FAQ accordion, legal sections, footer. A meal-kit or a password manager could use it without moving anything. All of the product character is in the writing ("Books that close themselves.", "the spreadsheet you already keep", "A report your accountant can read"), and those lines belong to this product. The visuals don't support them. The page uses the system font stack, a proportional-figure price, no ruled lines, and no picture of a spreadsheet, a closed month or the report. It avoids the usual template tells (no gradients, glass, emoji icons or stock hero art), but its distinctiveness comes from what it leaves out, not from anything it adds. Bookkeeping offers plenty to draw on and none of it is used: ledger rules, tabular numerals, a month-end "closed" mark, a spreadsheet row turning into a reconciled line.

**Deterministic scan:** `impeccable detect` scanned 1 file and returned 2 warnings (exit 2):
- `skipped-heading` (quality): `<h1>` "Books that close themselves." at `index.html:244` is followed by `<h3>` "Bank import" at `:254` (also `:258`, `:262`). The first `<h2>` is "Pricing" at `:271`. **Both sources agree.** The design review found the same gap independently, as a screen-reader outline problem and as a sighted-hierarchy problem (the three columns have no visible label). This is a true positive.
- `cream-palette` (slop): `--cream: #faf6ee` at `index.html:10`, used as the page background at `:24`. **The two sources partly disagree.** The design review counted cream plus `#1f7a4d` green as the page's one authored choice ("ledger paper and money"). The detector is literally correct and not a false positive, and in context it points at the real weakness: cream on the system font stack is the stock look of calm indie-SaaS. The cream reads as "ledger paper" only if something else says ledger, such as rules, tabular numerals or a report. On its own it is interchangeable. The ruling is to keep the palette, earn it, and not recolour.

The detector caught nothing the design review missed. The design review found much that static rules can't see: contradictory copy, the missing trust and data-security story, no closing CTA, a `scroll-behavior: smooth` with no `prefers-reduced-motion` guard (`index.html:20`), and the squeezed 3-column grid at 640–760px.

**Visual overlays:** none. No browser automation tool was available, so live-server injection was never tried and there are no overlays in a **[Human]** tab. The fallback signal is the CLI scan above.

## Overall Impression

The headline is strong and the page is honest, fast and readable. But it asks a visitor to connect their bank and upload their financial spreadsheet on the strength of copy alone. It never shows the product and barely addresses the risk. **The biggest opportunity is to make the hero *show* a month closing:** spreadsheet rows matched to bank lines, reconciled, ending in an accountant-ready report. That single change supplies the missing proof and the missing visual identity together.

## What's Working

1. **Restraint and readability.** 18px body text, a 42ch hero measure and 1.5 line height. Ink on cream is about 16:1 and the white-on-green CTA is about 5.3:1 (about 8:1 on hover). There are no fonts, images or scripts to wait for, and nothing competes with the words.
2. **Honest pricing.** "No card", "nothing is billed unless you start the paid plan" and one visible price appear in the pricing card, FAQ and Terms. That kind of transparency is rare and builds trust. It just hasn't reached the hero.
3. **A solid accessibility baseline.** Skip link, `:focus-visible` outlines (about 7.4:1), underlined inline links, native `<details>`/`<summary>`, 44px minimum button height, `lang="en"`, a labelled primary nav and a real meta description. The one structural lapse is the skipped heading level, which both sources flagged.

## Priority Issues

**[P1] The core promise is stated but never shown**
- **Why it matters:** "Books that close themselves" is a big claim for someone who reconciles by hand. With no screenshot, example row or sample report, the visitor has to trust an $18/month bank-connected service on words alone. This is also why the design feels generic: the product's most distinctive moment, spreadsheet to closed month, isn't on the page.
- **Fix:** Rebuild the hero as a demonstration. On the left, three or four recognisable spreadsheet rows. In the middle, the matching bank lines ticked off. On the right, a "March · closed" result. Put a real excerpt of the accountant report under the third feature. Set all figures in tabular numerals (`font-variant-numeric: tabular-nums`) and use hairline ledger rules, so the cream background finally reads as ledger paper.
- **Suggested command:** `gc sling score-mol-do-work/impeccable.conductor bolder --formula`

**[P1] No reassurance at the highest-stakes moment (bank and financial data)**
- **Why it matters:** For a finance tool, trust is the conversion bottleneck. Everything the page says about data is one vague FAQ answer ("you can delete it whenever you ask": ask whom, and how?) and a one-sentence Privacy section. The footer "Privacy policy" link lands on that one sentence, which looks like there is no real policy. There's no social proof either: no customer, accountant or number.
- **Fix:** Add a short "Your data" block beside pricing covering read-only bank access (name the provider), encryption, where data lives, and how to delete it (a button, not "ask"). Move Privacy and Terms to real pages. Add one named quote, preferably from an accountant, because the product promises a report "your accountant can read".
- **Suggested command:** `gc sling score-mol-do-work/impeccable.conductor clarify --formula`

**[P2] Copy contradicts itself and leans on jargon**
- **Why it matters:** A careful visitor who notices "reads the spreadsheet you already keep" (`index.html:245`, `:255`) next to "stores the spreadsheet you upload" (`:305`) starts doubting everything else. "Files the month" can be read as tax filing, which the product may not do. "$18 / month after the trial" contradicts "Billing starts only if you choose the paid plan". The plan called "Harbor" inside "Harbor Ledger" adds noise.
- **Fix:** Pick one data model ("connect" or "upload") and use it everywhere, including the meta description at `:7`. Replace "files the month" with the concrete result ("hands you a finished monthly report"). Change the price line to "$18 / month if you keep it". Drop the plan name or give it meaning.
- **Suggested command:** `gc sling score-mol-do-work/impeccable.conductor clarify --formula`

**[P2] The page ends on legal boilerplate with no closing CTA**
- **Why it matters:** A visitor who reads the FAQ is persuaded or close to it. At that point the page offers nothing to click and ends on "Terms: The trial lasts 14 days". By the peak-end rule, they remember the headline and a legal stub. On a phone the nav doesn't stick, so the only way forward is to scroll back up.
- **Fix:** Move Privacy and Terms to their own pages, linked from the footer. After the FAQ, add a closing band that restates the promise and "14 days, no card", with the CTA inside easy thumb reach.
- **Suggested command:** `gc sling score-mol-do-work/impeccable.conductor layout --formula`

**[P2] Flat hierarchy: no features heading, and the reassurance is far from the CTA** *(detector: `skipped-heading`)*
- **Why it matters:** The outline jumps from h1 to h3 (`index.html:244` to `:254`), so heading navigation skips a level, and sighted visitors get no label for the three columns. "The 14-day trial needs no card" (`:275`) is the strongest objection-remover and it isn't at the first decision point. The pricing card doesn't say what the plan includes. One free accountant seat is buried in the FAQ.
- **Fix:** Add a visible h2 to the features section that makes a claim, e.g. "What happens each month". Put "No card needed" directly under the hero CTA. Add a 3–4 item "includes" list to the pricing card: bank import, monthly close, accountant report, one free accountant seat. Give the plan name and price real typographic weight.
- **Suggested command:** `gc sling score-mol-do-work/impeccable.conductor typeset --formula`

## Persona Red Flags

**Jordan (First-Timer):** Reads "Books that close themselves" and "files the month" without knowing either term; neither is explained. Scrolls through three feature columns with no screen or example, so still can't picture what happens after clicking "Start the 14-day trial". Wants to know how deletion works, finds "whenever you ask", and the only contact route is a footer mailto. Clicks the CTA and lands on `app.harborledger.example` with no idea whether a bank login or a file upload comes next. **Likely to drop off at the CTA click.**

**Riley (Stress Tester):** Spots the contradictions within a minute: "reads" vs "upload", "after the trial" vs "only if you choose", "Harbor" vs "Harbor Ledger". Clicks "Privacy policy" and "Terms" in the footer, gets one sentence each, and concludes there's no real policy. Can't find answers to the obvious edge cases: several spreadsheets, an unsupported bank, a second accountant (the first is free, so what does the next cost?), a month that won't reconcile. The page never admits the books might *not* close on their own. **Leaves with less trust than they arrived with.**

**Casey (Distracted Mobile):** Reads the FAQ on a phone, is ready to start, and finds no CTA below it. The non-sticky nav is off-screen at the top, so Casey has to scroll the whole page back up. On a large phone in landscape or a small tablet (640–760px), the features grid jumps straight to three ~180–200px columns of 18px text, and "A report your accountant can read" wraps into a narrow tower. **The conversion window closes during the scroll back up.**

## Minor Observations

- `.no-card { color: var(--ink); }` (`index.html:176`) sets the colour the text already inherits, so the rule does nothing. It was probably meant to mute or emphasise the line.
- The pricing card border `#e2dbc9` on cream is about 1.28:1, so the card barely reads as a card and the price has no visual anchor.
- `html { scroll-behavior: smooth; }` (`:20`) has no `prefers-reduced-motion: reduce` guard.
- The features grid goes from 1 to 3 columns at 640px (`:143`) with no 2-column step.
- The "Pricing" h2 sits over a single card. Either shrink the section or make the card carry more.
- No "Sign in" link for existing customers.
- No favicon and no Open Graph or Twitter meta, so shared links will look bare, which is a missed referral surface for a Persuade page.
- `.site-name` is a `<span>`, not a home link. That's harmless on a one-page site, but unexpected.
- FAQ summaries use the default disclosure triangle. It's native and fine, just unstyled.

## Questions to Consider

- What if the hero *were* a month closing, with the visitor's kind of spreadsheet on one side and the finished accountant report on the other?
- Who is the buyer: the owner with the spreadsheet, or the accountant who reads the report? Would "invite your accountant" convert better than "do it yourself"?
- If the books close themselves, what does the owner still have to do? Would admitting that one step make the promise *more* believable?
- Would you connect your own bank feed on the strength of a one-sentence privacy section?
- Is the plainness a deliberate choice ("simple, like your spreadsheet") or just unfinished? If it's deliberate, what would make it look *authored* rather than default?

---

> **Trend for `index-html`:** first run for this target, no trend yet (22/32).
> Wrote `.impeccable/critique/2026-09-27T18-53-39Z__index-html.md`.

## Questions for the user

1. **Priority direction.** The report found three kinds of problem: missing proof (no product visual), missing trust (bank and data security, stub legal pages) and copy problems (contradictions and jargon). Which should be fixed first?
   - a) **Proof first:** rebuild the hero as a spreadsheet-to-closed-month demonstration with tabular numerals and ledger rules.
   - b) **Trust first:** a "Your data" block, real Privacy and Terms pages, and an accountant quote.
   - c) **Copy first:** fix "reads" vs "upload", "files the month" and the price line. It's the cheapest pass and it unblocks the other two.

2. **Design intent.** The detector flagged the cream `#faf6ee` background as generic, and the design review found that the plainness (system fonts, no imagery) reads as unfinished rather than chosen. Was the quiet look deliberate?
   - a) **Yes, keep it quiet but make it authored:** keep cream and green, add ledger rules, tabular and old-style figures and one sample report. No new colours.
   - b) **Warmer and more human:** keep cream but bring in a real typeface and an accountant or owner voice.
   - c) **More confident fintech:** move off cream to a crisper palette with a bolder product visual as the hero.

3. **Scope.** There are 5 priority issues (2 × P1, 3 × P2) plus 9 minor observations. How much should the next pass cover?
   - a) The two P1s only (product proof and the data-trust block).
   - b) All five priority issues.
   - c) Everything, including the minor fixes (reduced-motion guard, pricing-card border contrast, OG meta, favicon, Sign in link).

4. **Constraints.** Should anything stay as it is?
   - a) The headline "Books that close themselves." and the current feature copy are fixed.
   - b) Pricing and billing wording is set by legal or ops, so change only its placement, not its words.
   - c) Nothing is off-limits.
