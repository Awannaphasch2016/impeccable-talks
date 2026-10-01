Method: dual-agent (A: general-purpose sub-agent "Critique Assessment A design review" · B: general-purpose sub-agent "Critique Assessment B detector evidence")

# Critique: `index.html` (Northwind Analytics landing page)

**Mode:** Persuade (a marketing landing page with one conversion CTA).

**Context:**
- There is no PRODUCT.md or DESIGN.md, so the incumbent code is the only design authority.
- There is no `.impeccable/critique/ignore.md`.

**Visual inspection:** unavailable in both assessments. The machine has no browser binary, Playwright or Puppeteer, and the session exposes no native browser tool.
- Layout behaviour is reasoned from the CSS.
- Contrast ratios are computed from the actual hex values.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Only `:hover` states exist (lines 58, 91, 173). There is no `:focus-visible` or `:active` style. Every `href="#"` click jumps silently to the top. |
| 2 | Match System / Real World | 3 | Plain, confident copy. "events your product already emits" and "Ad-hoc queries" assume instrumentation and BI vocabulary. |
| 3 | User Control and Freedom | 3 | Little to escape from, but the `.brand` wordmark (line 179) is not a home link. |
| 4 | Consistency and Standards | 3 | Tokens are used consistently. The hover colour `#4338ca` is hard-coded outside `:root` (line 91). |
| 5 | Error Prevention | 2 | 6 of 7 destinations are `href="#"`. "Start free" doesn't say what happens (trial or free tier? card required?). |
| 6 | Recognition Rather Than Recall | 3 | Everything is text-labelled. Pricing is only behind a dead link, and the page gives no cost signal. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: no repeated workflow to accelerate. |
| 8 | Aesthetic and Minimalist Design | 3 | Clean and uncluttered. The "Features" eyebrow repeats the nav label and the h2's job, and the emoji tiles carry no information. |
| 9 | Error Recovery | 2 | No inputs. The one failure path, dead links, fails silently. |
| 10 | Help and Documentation | n/a | Persuade surface. The "Docs" nav entry points to `#`. |
| **Total** | | **21/32** | **Acceptable (66%)** |

Heuristics 7 and 10 are scored n/a (Persuade surface), so the applicable maximum is 32.

## Design Specificity Verdict

**LLM assessment: category-interchangeable.** Swap "Northwind Analytics" and the three card titles and this page could sell a CRM, a CI tool or a password manager unchanged.
- **Palette is stock Tailwind:**
  - `--ink #0f172a` is slate-900, `--muted #64748b` is slate-500 and `--line #e2e8f0` is slate-200.
  - `--accent #4f46e5` is indigo-600, `--accent-soft #eef2ff` is indigo-50, and the hover `#4338ca` is indigo-700.
- **Type:** the system font stack (line 20) with no display face.
- **Brand:** a plain 18px bold `<div>` with no mark.
- **Structure is the default SaaS skeleton:**
  1. a centred hero,
  2. an uppercase accent eyebrow over a centred h2,
  3. three bordered cards with emoji in tinted squares,
  4. a footer.

The page is coherent, but only the way a template is coherent.

The copy is more specific than the design. "No pipeline to build, no warehouse to babysit" has a voice the layout never carries. The biggest missed opportunity is that an analytics product shows no chart, no number, no event stream and no UI anywhere. The data itself is the obvious visual material, and none of it is used.

**Deterministic scan:** `impeccable detect --json index.html` exited 2 with **4 warnings, all in category `slop`**. It independently confirms the "template" verdict.

| Rule | Count | Location |
|---|---|---|
| `icon-tile-stack` | 3 | index.html:205–206, 210–211, 215–216 (tile CSS `.card .icon` at :128–138): 40×40 rounded `--accent-soft` squares holding 📊 🔍 🔔 above each `<h3>` |
| `kicker-above-heading` | 1 | index.html:201–202 (CSS `.section-title` at :99–107): the uppercase, tracked, accent-coloured "Features" `<p>` above the h2 "Built for teams that ship" |

**Where the review and the detector agree:**
- Both flag the emoji tiles and the "Features" eyebrow.
- The design review reached those as a judgment: decoration without information, and a redundant eyebrow. The detector classifies them as banned generator patterns.

**What the detector adds:** the eyebrow is not just redundant. `kicker-above-heading` is an outright ban, so it should be deleted, not restyled.

**What the review caught that the detector cannot:**
- the absent product visual,
- the dead links,
- the missing reassurance,
- the stock palette,
- the mobile header overflow.

**False positives:** none. All four findings match the source.

**Detector gap:** the detector reported `"line": 0` for every finding. The line numbers above were looked up by hand from each snippet.

**Visual overlays:** none. No browser was available, so there was no live-server, no `detect.js` injection and no console output. No user-visible overlay exists.

## Overall Impression

A tidy, competent page with a good paragraph trapped inside a default template. The copy knows what Northwind is for. The design could belong to anyone. The single biggest opportunity is to **show the product**: this is an analytics tool whose landing page contains zero data.

## What's Working

1. **Copy with a point of view.** "Northwind turns the events your product already emits into dashboards your team will actually open. No pipeline to build, no warehouse to babysit." It names the pain and the outcome in two sentences. The card copy also ends on benefits ("never reading yesterday's numbers", "only when something actually moves").
2. **An unambiguous primary action with sound contrast.** The only saturated element on the page is `.btn`:
   - White on `#4f46e5` is 6.29:1, and 7.9:1 on hover.
   - The button is about 54px tall.
   - Body ink is 17.85:1.
   - `--muted` is 4.76:1, which passes AA, narrowly.
3. **Fluid foundations:**
   - The h1 uses `clamp(32px, 5vw, 54px)` at line-height 1.1.
   - The hero paragraph is capped at 620px (about 65 characters).
   - The card grid uses `repeat(auto-fit, minmax(260px, 1fr))`, so it collapses without media queries.

## Priority Issues

**[P1] The product is invisible**
- **Why it matters:**
  - The central claim, "dashboards your team will actually open", has no evidence on the page.
  - Buyers of analytics tools judge by the charts.
  - This absence is the main reason the page reads as category-interchangeable.
  - The only "visuals" are three emoji (lines 205, 210, 215), which the detector also flags as a template pattern.
- **Fix:**
  - Put a credible product view beside or under the hero, such as a live-looking dashboard panel or a sparkline that ticks as "events arrive".
  - Replace the emoji tiles with small feature-specific visuals: a mini live chart, a plain-language query turning into a chart, an alert threshold line being crossed.
  - Drop the tinted icon container entirely.
- **Suggested command:** `/impeccable bolder` (then `/impeccable delight` for the live-data motif)

**[P1] The primary CTA and most navigation go nowhere**
- **What:** `href="#"` on "Start free" (line 195), Pricing and Docs (lines 182–183), and Privacy, Terms and Contact (lines 227–229).
- **Why it matters:**
  - The page's only conversion action scrolls to the top and does nothing. If this file ships as-is, that is a P0.
  - Pricing and Docs fail silently.
  - Dead legal links erode trust at the moment you are asking for someone's product data.
- **Fix:**
  - Wire real destinations.
  - Until they exist, remove the links rather than ship dead anchors.
  - Point "Start free" to a real signup route.
- **Suggested command:** `/impeccable harden`

**[P1] No reassurance or proof at the conversion moment, and no closing CTA**
- **What:** "Start free" stands alone, with:
  - no microcopy,
  - no pricing signal,
  - no data-handling or security note,
  - no logos or testimonial.
  
  The page also ends after the third card and goes straight to "© 2026 Northwind Analytics".
- **Why it matters:**
  - Connecting product event data to a third party is a trust decision. "Free for how long? Card required? Where does my data go?" all go unanswered exactly where the visitor hesitates.
  - By the peak-end rule, the last thing a convinced reader sees is a copyright line, and they must scroll back up to convert.
- **Fix:**
  - Add one line under the button using the real terms, e.g. "Free up to N events/month · No credit card · Connect in 5 minutes".
  - Add a logo strip or one testimonial.
  - Add a closing section before `<footer>` that restates the promise and repeats "Start free".
- **Suggested command:** `/impeccable clarify` (copy), `/impeccable layout` (closing section)

**[P2] Template-default visual identity**
- **What:**
  - stock Tailwind slate/indigo tokens (lines 8–15),
  - the system font stack,
  - a plain-text `.brand`,
  - the eyebrow + centred h2 + three-card skeleton (lines 201–203).
- **Why it matters:** nothing about the page is memorable as "Northwind", and the copy's voice is lost.
- **Fix:**
  - Delete the `.section-title` "Features" kicker outright. The detector bans it, and the h2 carries the section.
  - Pair a distinctive display face with the body text.
  - Derive the accent from the data-viz palette the product actually uses.
  - Give the wordmark a mark.
  - Consider a left-aligned hero with the product visual on the right instead of centred text in a 1080px container.
- **Suggested command:** `/impeccable typeset`, `/impeccable colorize`

**[P2] Mobile header and footer link rows break down, with small touch targets**
- **What:** `.nav` has no `flex-wrap`, and every `.nav a` carries `margin-left: 28px` (line 55). At 390px the row needs about 430px against about 342px available.
  - The likely result is a two-line "Northwind Analytics" and ragged nav links.
  - Because the margin also applies to the first link on each wrapped line, wrapped rows start indented.
  - The footer wraps (line 162) with the same `margin-left: 24px` (line 170), so Privacy/Terms/Contact drop below the © line indented.
  - Nav links are about 24px tall and footer links about 22px.
- **Why it matters:** a phone visitor's first impression is a cramped, misaligned header, and the small links cause mis-taps.
- **Fix:**
  - Replace per-link `margin-left` with `gap` on the flex containers.
  - Below about 600px, keep only "Pricing" plus a compact "Start free".
  - Pad links to at least 44px hit areas.
- **Suggested command:** `/impeccable adapt`

## Persona Red Flags

**Jordan (first-timer)**
- "Start free" doesn't say what is free or what happens next.
- "events your product already emits" is never shown or defined.
- The h3 "Ad-hoc queries" (line 211) is analyst jargon.
- Jordan never sees a Northwind dashboard, so the promise stays abstract.
- The only help path, "Docs" (line 183), is `href="#"`.

**Riley (stress tester)**
- Pricing, Docs, Privacy, Terms, Contact and Start free all silently scroll to the top. That is 6 dead destinations, and the page never admits it.
- Between about 600px and 880px, `minmax(260px, 1fr)` yields 2 columns, so "Alerts that matter" sits orphaned alone on the second row.
- The emoji "illustrations" render differently on Apple, Segoe and Noto.
- `© 2026` is hard-coded.

**Casey (distracted mobile user)**
- The header likely wraps into a two-line brand plus indented nav links at 390px.
- Nav and footer links are 22–24px tall.
- There is no CTA after the features and no sticky action, so once past the hero the conversion is never in the thumb zone. Casey has to scroll back up.

## Minor Observations

- **Screen readers:** the emoji in `.card .icon` lack `aria-hidden="true"`, so screen readers announce "bar chart", "magnifying glass tilted left" and "bell" before each h3.
- **Landmarks:**
  - The two `<nav>` elements (lines 180, 226) are unlabelled.
  - There is no `<main>` landmark and no skip link.
- **Focus:** there is no designed `:focus-visible` style. The browser defaults survive but are unstyled.
- **Faint decoration:**
  - The `.icon` tile background `#eef2ff` is 1.12:1 on white, so it nearly vanishes.
  - Card borders `#e2e8f0` are 1.23:1, so the cards read as ghost outlines.
- **Muted text:** `--muted` at 14–15px sits at 4.76:1. It passes AA but has no margin, so any lightening fails.
- **Spacing:** values are ad hoc (96/80/72/48/40/32/28/24/20) with no scale. The hero is padded 96px top, 80px bottom, and the features section 72px.
- **Metadata:** there is no `meta description`, favicon or Open Graph tags, so shared links render bare.

## Questions to Consider

- If Northwind's product *is* live data, why does its page contain no data? What if the hero itself were a dashboard updating in real time?
- The copy says "no warehouse to babysit". What would a design as blunt and specific as that line look like, rather than one as safe as the indigo button?
- Who is this for: the engineer who instruments events, or the PM who reads dashboards? Choosing one would change every headline.
- What does a still-unsure visitor do after the third card? Why does the page leave them with nothing but a copyright line?

---

> **Trend for `index-html` (last 5 runs): 21 (out of 32).** First run for this target, no trend yet.
> Wrote `.impeccable/critique/2026-09-27T15-54-40Z__index-html.md`.

**Run bookkeeping:**
- No live server was started because no browser was available, so none is running.
- The temp body file was cleaned up.
- The detector reported `line: 0` for all four findings. The line numbers above were looked up by hand.
- Interactive question tool: unavailable (unattended run). Questions are listed below with their options.

## Questions for the user

The report lists 5 Priority Issues, so the questions are required.

1. **Priority direction:** the review found three problem areas. Which should we tackle first?
   - **A. Show the product:** replace the emoji tiles and the empty hero with real data visuals (`/impeccable bolder`, `/impeccable delight`).
   - **B. Make conversion work:** wire the dead `href="#"` links, add reassurance microcopy under "Start free", and add a closing CTA (`/impeccable harden`, `/impeccable clarify`, `/impeccable layout`).
   - **C. Fix mobile:** fix the header and footer wrapping and the 22–24px touch targets (`/impeccable adapt`).

2. **Design intent:** the page currently reads as stock Tailwind slate/indigo with the system font. Was that deliberate?
   - **A. Keep the restrained, neutral look.** Only remove the banned patterns: the "Features" kicker and the icon tiles.
   - **B. Push toward a data-native identity:** a data-viz-derived palette, a display typeface, and a wordmark with a mark (`/impeccable typeset`, `/impeccable colorize`).
   - **C. Go bold and blunt to match the copy's voice** ("no warehouse to babysit"). This would be a redesign, which needs `/impeccable init` first because there is no PRODUCT.md.

3. **Scope:** how much should the next pass take on?
   - **A. Top 3 only:** the P1s (product visual, dead links, reassurance and closing CTA).
   - **B. All 5 priority issues,** including identity and mobile.
   - **C. All 5 plus the minor observations:** aria-hidden emoji, `<main>` and skip link, focus styles, spacing scale, meta/OG tags.

4. **Constraints:** should anything stay as it is?
   - **A. The hero headline and subhead copy.** They are the page's strongest asset.
   - **B. The indigo brand colour,** if it is already used elsewhere.
   - **C. Nothing is off-limits.**
