# Assessment A: Design Review

Target: `index.html` (Northwind Analytics marketing page), mode **Persuade**. There is no DESIGN.md or PRODUCT.md, so the incumbent code is the only design authority. No live URL was named and no headless browser was available in this session. I formed this review by reading the source and working out how it renders (layout at 1080px and 375px, and contrast calculated from the tokens). I did not run the detector and did not look at any detector output.

## Design specificity verdict

**Verdict: category-interchangeable. The words are specific to the product but nothing else is.**

- **Structure is the default SaaS template:** a header with the brand on the left and three links on the right, then a centered hero (h1, grey subhead, one indigo pill button), then a small-caps accent eyebrow ("FEATURES"), a centered H2, a 3-up card grid with emoji icons in rounded tinted squares, and a footer with copyright and legal links. Change the name and this page could sell a CRM, a password manager or a CI tool.
- **The palette is Tailwind's defaults, unchanged:** `#0f172a` (slate-900), `#64748b` (slate-500), `#e2e8f0` (slate-200), `#4f46e5` (indigo-600), hover `#4338ca` (indigo-700), `#eef2ff` (indigo-50). No color decision belongs to Northwind.
- **Typography is the system font stack** with no pairing, no numeric or mono voice, and no typographic idea. That is a real gap for a product whose whole subject is numbers.
- **Icons are emoji** (📊 🔍 🔔). They render differently on each platform and suggest a placeholder.
- **The page never shows the product.** It sells dashboards "your team will actually open", yet shows no chart, no dashboard and no event, and has no motion. The product's big idea is live data ("Charts update as events arrive") and the page is completely static.
- **What is authored is the copy.** "No pipeline to build, no warehouse to babysit" and "you are never reading yesterday's numbers" are specific and positioned against a named alternative (a warehouse). The visual design does none of that work.

## Heuristic scores

| # | Heuristic | Score 0-4 or n/a | Key issue |
|---|-----------|------------------|-----------|
| 1 | Visibility of System Status | 2 | Pricing, Docs, Start free and all three footer links are `href="#"`. Clicking one silently jumps to the top with no feedback. The nav has no current-location state. |
| 2 | Match System / Real World | 3 | Copy is plain and benefit-led. "Events your product already emits" and "Ad-hoc queries" assume a product-engineering reader, which is probably right, but the page never says who it is for. |
| 3 | User Control and Freedom | 3 | Nothing traps the user. Dead `#` links move the scroll position without being asked, and the brand is not a link home. |
| 4 | Consistency and Standards | 3 | Tokens are used consistently and nav and footer links behave alike. Some conventions are broken: the brand/logo is not a home link, the hover color and `#fff` are hard-coded outside the tokens, and the h2 inherits body `line-height: 1.6` while the h1 is tuned to 1.1. |
| 5 | Error Prevention | 2 | There are no inputs, but six live-looking links (including the primary CTA) lead nowhere, so the page builds in the most common visitor error: clicking something that looks real and isn't. |
| 6 | Recognition Rather Than Recall | 3 | Everything visible is labeled. The facts a buyer needs to decide (price, what "free" includes, how data gets in) are neither shown nor linked to anything that works. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: one linear reading path, and accelerators do not apply. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and uncluttered with one clear primary action. The minimalism leaves the page thin rather than focused: decorative emoji, and a redundant "Features" eyebrow repeating the nav and H2. |
| 9 | Error Recovery | n/a | No forms or error-producing flows. The dead-link failure is counted under H1 and H5. |
| 10 | Help and Documentation | n/a | Persuade surface. The "Docs" link exists but is dead (counted under H1 and H5). |
| **Total** | | **19/28** | **Acceptable (68%)**. H7, H9 and H10 are n/a. |

Applicable maximum: 28 (7 heuristics scored). n/a heuristics: 7, 9, 10.

## Cognitive load

Checklist result: **0 failures, so cognitive load is low.**

- Single focus: pass. There is one CTA and nothing competes with it.
- Chunking: pass. 3 nav links, 3 feature cards, 3 footer links.
- Grouping: pass. Cards are bordered, and sections are separated by rules and spacing.
- Visual hierarchy: pass. The h1 is at 54px, the indigo button is the only saturated element, and the H2 clearly leads the features section.
- One thing at a time: pass.
- Minimal choices: pass. The first viewport has 4 actionable items (Features, Pricing, Docs, Start free). No decision point shows more than 4 options.
- Working memory: pass.
- Progressive disclosure: pass. Nothing is hidden, though there is little to disclose.

Caveat: the load is low mostly because the page says very little. The failure is under-informing, not overloading. A visitor ends the page without the facts needed to act (price, setup effort, trust signals), which moves the effort into a later context switch: hunting for pricing or docs elsewhere. Here that switch is impossible because those links are dead.

## Emotional journey

1. **Arrival (moderate peak):** "Know what your data is doing" is calm and confident, and the subhead names a real pain (pipelines, warehouses). This is the best moment on the page.
2. **The ask, too early and unsupported:** "Start free" appears right after two sentences, with no qualifier (free for how long? up to what volume? card required?) and no picture of what you get. Instrumenting a product's events is a high-stakes commitment (engineering time, data leaving the building), and the page offers no reassurance at all: no security or privacy note, no setup snippet, no "5 minutes to first chart".
3. **Features (flat):** three short, well-written cards whose emoji icons and template layout reduce their credibility. There is nothing to look at.
4. **Valley:** a curious visitor clicks Pricing or Docs and nothing happens. The page scrolls to the top. That is where trust drops.
5. **End (flat, fails peak-end):** the page stops right after the feature cards. There is no closing argument, no second CTA and no proof. The last thing a visitor sees is a footer of dead legal links. By the peak-end rule the visitor remembers the hero and a blank ending, which does not persuade.

## Strengths

1. **The copy has a point of view.** "No pipeline to build, no warehouse to babysit" positions against a specific alternative. The feature lines are framed around outcomes ("you are never reading yesterday's numbers"; "hear about it only when something actually moves"). This is the most product-specific material on the page and should drive the visual design.
2. **Restraint and a clear hierarchy.** There is one primary action, one saturated color used only for action and emphasis, and a clear h1 → h2 → h3 ladder, so the page is easy to scan in seconds.
3. **Sound, accessible foundations.** Colors are tokens on `:root`. Contrast passes AA: muted text is 4.76:1, accent is 6.29:1, white on the button is 6.29:1 (7.9:1 on hover). The h1 uses `clamp()` and the grid is `auto-fit`, so the layout adapts without breakpoints. No `outline: none` was found, so default focus rings survive.

## Priority issues

**[P0] The primary CTA and most navigation go nowhere**
- **What:** `Start free` (`index.html:195`), `Pricing` and `Docs` (`:182-183`), and `Privacy`/`Terms`/`Contact` (`:227-229`) are all `href="#"`.
- **Why it matters:** On a Persuade page the one job is conversion, and a visitor cannot complete it. Every dead click also jumps the page to the top with no explanation, which reads as a broken site.
- **Fix:** Point `Start free` at the real signup URL. If Pricing and Docs don't exist yet, either remove them or add an on-page `#pricing` section. Never ship a live-looking link to nowhere. Give legal links real destinations or remove them.

**[P1] The page never shows the product**
- **What:** The page sells an analytics product but has no chart, dashboard, event stream or UI of any kind. The hero is text only.
- **Why it matters:** Buyers of analytics tools judge by what the charts look like and how fast they appear. "Dashboards your team will actually open" is a claim the page never backs up. Without a visual, the page gives no reason to prefer Northwind over any competitor.
- **Fix:** Put a real product view in or directly under the hero: an actual dashboard crop, or a small live-looking chart built in HTML/SVG that ticks as "events arrive". This demonstrates the central "live" claim. Give each feature card a small real UI fragment (a sparkline, a query input with a chart result, an alert row) instead of an emoji.

**[P1] The visual language is a stock template, not Northwind**
- **What:** Tailwind slate and indigo defaults, the system font, a centered hero, an eyebrow + H2 + three emoji cards.
- **Why it matters:** Nothing is memorable. A visitor who opens three analytics tools in tabs will not remember which one this was, and the template look suggests a thin product.
- **Fix:** Choose a visual idea from the product itself: live events and numbers that move. For example, a tabular or mono face for figures, an accent color that isn't indigo-600, a timeline or stream motif, and drawn icons (or none). Break the centered symmetry, for example with the hero text on the left and the live chart on the right.

**[P1] No closing argument, no pricing signal, no reassurance**
- **What:** The page ends straight after the features section. "Start free" has no qualifier. There is no proof (customers, numbers, testimonials) and nothing on security, privacy or setup effort.
- **Why it matters:** Connecting product events is an engineering commitment involving data governance. Visitors who are interested but not yet convinced reach the end with nothing to convert them and nothing to settle their doubts, so they leave.
- **Fix:** Add a closing band before the footer. Include a two- or three-line install snippet (this backs up "events your product already emits … no pipeline"), one line on free-tier limits ("Free up to N events/month, no card"), a one-line data and privacy promise, and the CTA again. Add a qualifier under the hero button too.

**[P2] The mobile header and links are cramped and hard to tap**
- **What:** `.nav` has no `flex-wrap`, and its links use `margin-left: 28px` with no padding. At 375px, "Northwind Analytics" (18px bold) plus three links with 84px of margins does not fit, so the brand breaks onto two lines and the links wrap raggedly. Tap targets for nav and footer links are about 24px tall, well under 44px. In the footer, `margin-left: 24px` on links indents the first link when the row wraps.
- **Why it matters:** Mobile visitors from ads and social see a broken-looking header before the headline. Small, closely spaced targets cause mis-taps.
- **Fix:** Use `gap` instead of `margin-left`. Add vertical padding to links (for example `padding: 12px 8px`) to get 44px targets. Below about 480px, drop Docs or move secondary links into the footer so the header stays on one line.

## Persona red flags

Selected for a landing page: Jordan, Riley, Casey. Sam's checks were run as secondary. There is no Design Context, so I generated no project-specific personas.

**Jordan (Confused First-Timer):**
- Within 5 seconds Jordan knows the promise but not the category's mechanics. "Turns the events your product already emits into dashboards" assumes Jordan knows what product events are and that the product already emits them. Nothing defines "events" or shows how they get in.
- "Start free" gives no clue what happens next (a signup form? a sales call? a credit card?), and clicking it does nothing, so Jordan concludes the site is broken.
- Jordan looks for help and clicks "Docs": dead. "Contact": dead. There is no path to a human.

**Riley (Deliberate Stress Tester):**
- Every secondary link (`Pricing`, `Docs`, `Privacy`, `Terms`, `Contact`) appears to work and fails silently by jumping to the top. This is the "appears to work but silently fails" red flag, six times over.
- The page claims "live", "plain language" queries and alerts, and demonstrates none of them. Riley reads this as a gap between promise and delivery.
- There is no Privacy page behind a product that asks for your event data. Riley flags that as a trust failure, not a cosmetic one.

**Casey (Distracted Mobile User):**
- The header wraps into a two-line brand plus ragged links at phone width. The only CTA is in the upper-middle of the hero, and there is no repeat CTA lower down near the thumb when Casey finishes reading.
- Nav and footer targets are about 24px tall with 24-28px margins between them, so fat-finger taps are likely.
- The page is light and fast, but a very short page with no visual gives Casey nothing to remember when they come back later.

**Sam (Accessibility, secondary):**
- The emoji icons have no `aria-hidden`, so screen readers announce "bar chart", "magnifying glass tilted left" and "bell" before each card heading. That is noise.
- The two `<nav>` elements (header and footer) have no `aria-label`, so they can't be told apart in a landmarks list. There is no `<main>` landmark and no skip link.
- Contrast passes and default focus rings survive, so the basics hold.

## Minor observations

- Hard-coded colors bypass the tokens: `.btn:hover { background: #4338ca }` and `color: #fff`. Add `--accent-strong` and `--on-accent`.
- `.features h2` (32px) inherits `line-height: 1.6` from `body`, which is loose for a display heading. The h1 is tuned to 1.1 and the h2 should be too (about 1.2).
- The type scale is crowded: 13, 14, 15, 17, 18 and 19px are all used. Adjacent steps like 17 vs 15 (card h3 vs card body) and 18 vs 19 barely register as different. Consolidate to a clearer ratio.
- The "FEATURES" eyebrow repeats both the nav link and the section's purpose, and adds nothing. "Built for teams that ship" is a stock phrase. Name the team instead (product engineers? growth PMs?).
- Card borders (`#e2e8f0` on white) are 1.23:1, very faint. This is acceptable because the cards are decorative containers, but on low-quality screens the grid barely appears as a grid.
- The brand is plain text with no mark and no link home.
- There is no custom `:focus-visible` style on `.btn`. The browser default works, but there's no brand-consistent focus treatment to match the hover.
- There is no `<meta name="description">` or Open Graph data, so shared links to this persuasion page will render as bare URLs.
- `footer { margin-top: 40px }` comes after `.features { padding: 72px 0 }`, giving about 112px of dead space before a footer that has nothing to say.

## Provocative questions

- The product's promise is live data. Why is the one page selling it completely still?
- If the hero were a dashboard instead of a sentence, would you still need the subhead?
- Who exactly is "your team": the engineer who instruments events, or the PM who reads the charts? The page speaks to both and persuades neither.
- What does "free" cost me in events, seats, days or a credit card? Why make me click (into nothing) to find out?
- If you replaced "Northwind Analytics" with a CRM's name and rewrote three card titles, would any pixel of the design need to change?
- "No pipeline to build" is the sharpest claim here. What if the page proved it with three lines of install code rather than an emoji?
