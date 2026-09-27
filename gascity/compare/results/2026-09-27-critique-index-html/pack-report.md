Method: dual-agent (A: impeccable.design-reviewer step imp-dal · B: impeccable.evidence-collector step imp-6td)

# Critique: `index.html` (Northwind Analytics marketing page)

Mode: **Persuade**. There is no DESIGN.md or PRODUCT.md, so the incumbent code is the only design authority. There is no ignore list.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Pricing, Docs, Start free and all three footer links are `href="#"`. A click silently jumps to the top, and the nav shows no current location. |
| 2 | Match System / Real World | 3 | The copy is plain and benefit-led, but "events your product already emits" assumes a product-engineering reader the page never names. |
| 3 | User Control and Freedom | 3 | Nothing traps the user. Dead `#` links move the scroll position unasked, and the brand isn't a home link. |
| 4 | Consistency and Standards | 3 | Tokens are used consistently. The exceptions are the hard-coded `#4338ca` hover and `#fff`, an h2 that inherits `line-height: 1.6`, and a brand that isn't a link. |
| 5 | Error Prevention | 2 | Six live-looking links, including the primary CTA, lead nowhere, so the page manufactures the visitor's most common error. |
| 6 | Recognition Rather Than Recall | 3 | Everything is labeled, but the facts needed to decide (price, what "free" includes, how data gets in) are neither shown nor reachable. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface with one linear reading path, so accelerators don't apply. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean, with one clear action. The page is thin rather than focused: emoji tiles and a redundant "Features" eyebrow. |
| 9 | Error Recovery | n/a | There are no forms or error-producing flows. Dead links are counted under H1 and H5. |
| 10 | Help and Documentation | n/a | Persuade surface. The "Docs" link is dead (counted under H1 and H5). |
| **Total** | | **19/28** | **Acceptable (68%)** |

The applicable maximum is **28** because 7 heuristics were scored. Heuristics **7, 9 and 10** are n/a.

## Design Specificity Verdict

**Category-interchangeable.** The words are Northwind's, but nothing visual is.

**LLM assessment (A):** The page follows the default SaaS template: brand-left/links-right header, centered hero with h1, grey subhead and indigo pill, then eyebrow, H2, a 3-up emoji card grid and a legal footer. The palette is unmodified Tailwind (slate-900 `#0f172a`, slate-500 `#64748b`, slate-200 `#e2e8f0`, indigo-600 `#4f46e5`, indigo-700 hover, indigo-50 tint). Type is the system stack with no numeric or mono voice, which is a real miss for a product whose subject is numbers. The page sells live dashboards and shows no chart, no event and no motion. Swap in a CRM's name and three card titles, and no pixel would need to change. The one authored element is the copy: "No pipeline to build, no warehouse to babysit" positions against a named alternative, and the visuals do none of that work.

**Deterministic scan (B):** `impeccable detect --json index.html` exited 2 with **4 warnings across 2 slop rules**. There were no false positives, and each finding was checked against the source.
- `icon-tile-stack` ×3 flags the 40×40 rounded `--accent-soft` tile above each card h3 ("Live dashboards" `index.html:205–206`, "Ad-hoc queries" `:210–211`, "Alerts that matter" `:215–216`), all styled by one rule, `.card .icon` at `:128–138`. It is one component, so one fix.
- `kicker-above-heading` ×1 flags `<p class="section-title">Features</p>` above the H2 "Built for teams that ship" (`:201–202`, styled at `:99–107`).

**Where they meet:** The reviewer and the detector agree independently on both flagged patterns. A called the emoji tiles placeholder-grade and the "FEATURES" eyebrow redundant before seeing any detector output. The detector adds a firmer framing: these two patterns are the universal AI/template feature-card signature, not just weak choices. **A caught issues the detector does not cover:** the six dead `href="#"` links, the unmodified Tailwind palette and system font, the emoji glyphs themselves (as opposed to their tile), the tokens bypassed by `#4338ca`/`#fff`, the cramped mobile header, and the absent product visual. The detector's issues are a subset of the reviewer's. The detector confirms the template diagnosis but misses the most damaging problem (dead conversion links). One tooling gap: every detector finding reported `line: 0`, so the line numbers above were matched by hand.

**Visual overlays:** None are available. The session had no browser automation (no browser tool, no Chromium/Chrome/Firefox binary, no Playwright or Puppeteer), so overlay injection and the mutation preflight never ran, and there is no **[Human]** tab to look at. The fallback signal is the CLI scan above. No rendered contrast, overflow or computed-style evidence exists. Contrast figures below were calculated from the tokens, and the mobile layout was reasoned from the CSS, not observed.

## Overall Impression

A calm, legible, accessible page with a sharp headline and a broken spine. Nearly every link, including the only CTA, goes nowhere, and the page sells a live-data product without showing a single piece of data. The biggest opportunity is to make the page *prove* "live": a real (or convincingly live-looking) chart in the hero, driven by the product's own idea of events arriving, would fix the specificity problem and the persuasion problem together.

## What's Working

1. **The copy has a point of view.** "No pipeline to build, no warehouse to babysit" and "you are never reading yesterday's numbers" are outcome-framed and positioned against a specific alternative. This is the most Northwind-specific material on the page and should drive the visual redesign.
2. **Restraint and hierarchy.** There is one primary action and one saturated color used only for action and emphasis. A clean h1 → h2 → h3 ladder makes the page scannable in seconds. Cognitive-load checklist: 0 failures. The first viewport has 4 actionable items, and no decision point exceeds 4 options.
3. **Sound, accessible foundations.** Colors are `:root` tokens, and contrast passes AA: muted text 4.76:1, accent 6.29:1, white on button 6.29:1 (7.9:1 on hover). The h1 uses `clamp()`, the grid uses `auto-fit`, and there's no `outline: none`, so default focus rings survive.

## Priority Issues

**[P0] The primary CTA and most navigation go nowhere**
- **What:** `Start free` (`index.html:195`), `Pricing` and `Docs` (`:182–183`), and `Privacy`/`Terms`/`Contact` (`:227–229`) are all `href="#"`.
- **Why it matters:** A Persuade page has one job, conversion, and the visitor can't complete it. Each dead click also jumps to the top without explanation, which reads as a broken site. A missing Privacy page behind a product that asks for your event data is a trust failure.
- **Fix:** Point `Start free` at the real signup URL. Give Pricing and Docs real destinations, add on-page `#pricing`/`#docs` sections, or remove the links. Do the same for the legal links. Never ship a live-looking link to nowhere.
- **Suggested command:** `gc sling impeccable-pack/impeccable.conductor harden --formula`

**[P1] The page never shows the product**
- **What:** It sells analytics but has no chart, dashboard, event stream or UI. The hero is text only, and each feature card leads with an emoji instead of evidence.
- **Why it matters:** Analytics buyers judge by what the charts look like and how fast they appear. "Dashboards your team will actually open" and "Charts update as events arrive" are claims the page never backs. With no visual, there is no reason to prefer Northwind.
- **Fix:** Put a product view in or directly beside the hero: a real dashboard crop, or a small HTML/SVG chart that ticks as "events arrive". Replace each card's emoji tile with a real UI fragment: a sparkline for Live dashboards, a plain-language query with a chart result for Ad-hoc queries, an alert row for Alerts that matter. This also clears all three `icon-tile-stack` findings.
- **Suggested command:** `gc sling impeccable-pack/impeccable.conductor visualize --formula`

**[P1] The visual language is a stock template, not Northwind (detector-confirmed)**
- **What:** Unmodified Tailwind slate and indigo, the system font, a centered symmetric hero, and an eyebrow + H2 + three icon-tile cards. The detector flags the kicker (`:201`) and all three icon tiles (`:205`, `:210`, `:215`) as template-slop signatures.
- **Why it matters:** Nothing is memorable. A visitor comparing three analytics tools in tabs won't remember which one this was, and the template look suggests a thin product.
- **Fix:** Take the visual idea from the product itself: live events and moving numbers. Use a tabular or mono face for figures, an accent that isn't indigo-600, and a timeline or stream motif. Move hero text left with the live chart on the right. Delete the "Features" kicker and let the H2 speak, and rewrite "Built for teams that ship" to name the actual team. Drop the icon containers.
- **Suggested command:** `gc sling impeccable-pack/impeccable.conductor bolder --formula` (then `typeset`, then `colorize`)

**[P1] No closing argument, no pricing signal, no reassurance**
- **What:** The page ends straight after the features section. `Start free` has no qualifier. There is no proof (customers, numbers, testimonials) and nothing on security, privacy or setup effort. The footer comes after ~112px of dead space (`.features` 72px padding + `footer` 40px margin).
- **Why it matters:** Instrumenting product events is an engineering and data-governance commitment. By the peak-end rule, visitors remember a strong hero and a blank ending. The interested-but-unconvinced leave with their doubts unanswered.
- **Fix:** Add a closing band before the footer: a 2–3 line install snippet that proves "no pipeline", one line on free-tier limits ("Free up to N events/month, no card"), a one-line data and privacy promise, and the CTA again. Add the same qualifier under the hero button.
- **Suggested command:** `gc sling impeccable-pack/impeccable.conductor clarify --formula`

**[P2] The mobile header and links are cramped and hard to tap**
- **What:** `.nav` has no `flex-wrap`, and its links use `margin-left: 28px` with no padding. At 375px, "Northwind Analytics" (18px bold) plus three links and 84px of margins doesn't fit, so the brand breaks onto two lines and the links wrap raggedly. Nav and footer targets are about 24px tall, and footer `margin-left: 24px` indents the first link when the row wraps. This was reasoned from the CSS; no rendered view was available.
- **Why it matters:** Mobile visitors from ads and social see a broken-looking header before the headline, and small, tight targets cause mis-taps.
- **Fix:** Replace `margin-left` with `gap` and add `padding: 12px 8px` to reach 44px targets. Below ~480px, drop Docs from the header (keep it in the footer) so the header stays on one line.
- **Suggested command:** `gc sling impeccable-pack/impeccable.conductor adapt --formula`

*Note: this pack currently installs only the `critique` formula. The command names above are Impeccable's commands for the fix, and they will need matching formulas before they can be slung.*

## Persona Red Flags

Selected for a landing page: Jordan, Riley and Casey, with Sam as a secondary check. No `## Design Context` exists, so no project-specific personas were generated.

**Jordan (Confused First-Timer):** Gets the promise but not the mechanics. "Turns the events your product already emits into dashboards" never says what an event is or how it gets in. "Start free" gives no hint of what comes next (a form? a sales call? a card?), and clicking it does nothing. Looking for help, Jordan clicks "Docs" and then "Contact", and both are dead. There is no path to a human. Jordan concludes the site is broken and leaves.

**Riley (Deliberate Stress Tester):** Five secondary links (`Pricing`, `Docs`, `Privacy`, `Terms`, `Contact`) look real and fail silently, and so does the CTA. That is the "appears to work but silently fails" pattern six times. The page claims live updates, plain-language queries and smart alerts, and demonstrates none of them. There is no Privacy page for a product that ingests your event data, which Riley logs as a trust failure, not a cosmetic one.

**Casey (Distracted Mobile User):** At phone width the header wraps into a two-line brand and ragged links. The only CTA sits in the upper-middle of the hero, and there is no repeat CTA near the thumb at the end of the page. Nav and footer targets are about 24px tall with 24–28px margins, so fat-finger taps are likely. The page is short and has no image, so there is nothing to remember on return.

**Sam (Accessibility, secondary):** The emoji icons lack `aria-hidden`, so screen readers announce "bar chart", "magnifying glass tilted left" and "bell" before each heading. The header and footer `<nav>` elements have no `aria-label`, so they can't be told apart. There is no `<main>` landmark and no skip link. Contrast and default focus rings hold.

## Minor Observations

- Hard-coded colors bypass the tokens: `.btn:hover { background: #4338ca }` and `color: #fff`. Add `--accent-strong` and `--on-accent`.
- `.features h2` (32px) inherits `line-height: 1.6` from `body`. Tune it to ~1.2 to match the h1's deliberate 1.1.
- The type scale is crowded: 13/14/15/17/18/19px. Adjacent steps (17 vs 15, 18 vs 19) barely register as different, so consolidate to a clear ratio.
- Card borders (`#e2e8f0` on white, 1.23:1) are faint enough that the grid barely reads as a grid on poor screens.
- The brand is plain text with no mark and no link home (`index.html:179`).
- There is no brand-consistent `:focus-visible` on `.btn` to match the hover treatment.
- There is no `<meta name="description">` or Open Graph data, so shared links to this persuasion page render as bare URLs.
- Detector tooling: every finding reported `line: 0`, so a line-accurate overlay or polish pass will need hand-mapping until that is fixed.

## Questions to Consider

- The product's promise is live data. Why is the one page selling it completely still?
- If the hero were a dashboard instead of a sentence, would you still need the subhead?
- Who is "your team": the engineer who instruments events, or the PM who reads the charts? The page speaks to both and persuades neither.
- What does "free" cost in events, seats, days or a card, and why make the visitor click (into nothing) to find out?
- "No pipeline to build" is the sharpest claim here. What if three lines of install code proved it instead of an emoji?

---

> **Trend for `index-html`: 19/28.** This is the first run for this target, so there is no trend yet.
> Wrote `.impeccable/critique/2026-09-27T15-56-45Z__index-html.md`.

## Questions for the user

1. **Priority direction.** The five issues fall into three areas. Which one should the action plan start with?
   - **A. Conversion plumbing:** make `Start free`, Pricing, Docs and the legal links real (P0), plus the mobile header (P2).
   - **B. Show the product:** a live-looking chart in the hero, and real UI fragments replacing the emoji icon tiles (P1).
   - **C. Northwind's own visual identity:** new type, a non-indigo accent, an asymmetric hero, and removing the kicker and icon-tile template signatures (P1).

2. **Design intent.** The page currently reads as a neutral, interchangeable Tailwind SaaS template, while the copy is confident and slightly irreverent ("no warehouse to babysit"). Which tone should the visuals take?
   - **A. Instrument-panel precise:** a mono or tabular numeric face, dark or high-contrast data surfaces, a ticking live chart as the hero.
   - **B. Warm and editorial:** a serif or humanist headline face, generous whitespace, product fragments framed like annotated figures.
   - **C. Keep the current calm, neutral tone:** just replace the stock palette and emoji so it's recognisably Northwind.

3. **Scope.** There are 5 priority issues (1 P0, 3 P1, 1 P2) plus 8 minor observations. How much should the plan take on?
   - **A. P0 only:** fix the dead links now and ship.
   - **B. Top 3:** dead links, show the product, visual identity.
   - **C. Everything:** all five priority issues plus the minor observations (tokens, h2 line-height, type scale, a11y landmarks, meta tags).

4. **Constraints.** Is anything off-limits?
   - **A. Keep the copy as written:** it is the page's strongest asset, so change only visuals and structure.
   - **B. Pricing and Docs don't exist yet:** remove those links rather than building on-page sections.
   - **C. Nothing is off-limits:** copy, structure and links can all change.
