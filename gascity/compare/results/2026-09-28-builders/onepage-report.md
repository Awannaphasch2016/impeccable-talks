Method: dual-agent (A: impeccable.design-reviewer step xpr-zgp · B: impeccable.evidence-collector step xpr-u3q)

# Critique: Harbor Ledger landing page (`onepage/index.html`)

Mode: **Persuade**. There is no PRODUCT.md, DESIGN.md or surface brief, so this critique is based on the code alone. There is no ignore list.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Nothing says what happens after "Start the 14-day trial". The visitor is sent to another domain with no preview of the next step (account, spreadsheet connection, bank link). |
| 2 | Match System / Real World | 3 | The language is plain, but "files the month" / "files the books" reads as a tax or regulatory filing to an owner or accountant. |
| 3 | User Control and Freedom | 3 | A short anchor-linked page with no traps. There is no sign-in link for returning customers, and the brand name does not link to the top. |
| 4 | Consistency and Standards | 2 | Billing is described three different ways (lines 129, 147, 162). The voice shifts from "you" to "the customer" in Privacy and Terms. The plan is called "Harbor" in one place and "the paid plan" in another. |
| 5 | Error Prevention | 2 | "Billed after the 14-day trial" suggests the trial converts automatically. The supported spreadsheet formats and banks are never named, so a visitor can start a trial that cannot work for them. |
| 6 | Recognition Rather Than Recall | 3 | Everything fits in one scroll, but the answer to "will I be charged?" has to be pieced together from Pricing, the FAQ and Terms. |
| 7 | Flexibility and Efficiency | n/a | Persuade surface: a one-page marketing site has no expert workflow to accelerate. |
| 8 | Aesthetic and Minimalist Design | 3 | Uncluttered. However, the one-sentence legal stubs get the same visual weight as Pricing, and the feature copy repeats itself. |
| 9 | Error Recovery | 2 | There are no forms, but a visitor unsure whether the product fits them (which spreadsheet, which bank, what happens when matching fails) has nowhere to go except a footer email address. |
| 10 | Help and Documentation | n/a | Persuade surface: a landing page does not need product documentation. The FAQ is judged under heuristics 5 and 9. |
| **Total** | | **20/32** | **Acceptable** (62.5%) |

Applicable maximum: 32. Heuristics 7 and 10 were scored n/a.

## Design Specificity Verdict

**The words are specific to this product; the visuals are not.**

**LLM assessment**: The copy clearly belongs to Harbor Ledger. "Reads the spreadsheet you already keep", "a report your accountant can read" and "one accountant can be invited at no charge" only make sense for a bookkeeping tool sold to owners who keep their books in a spreadsheet. The visual design has nothing comparable. The page is one centered column of identical bands (h2, paragraph, hairline rule), set in `system-ui` on cream with one green accent. A newsletter, a notes app or a dental practice could use the same visual layer unchanged. Neither "ledger" nor "harbor" shows up anywhere visually: no ruled columns, no tabular figures, no mark, no picture of the spreadsheet or the month-end report. The one product-specific object the page promises, the report your accountant can read, never appears. That is the biggest missed opportunity for product character.

**Deterministic scan**: `impeccable detect --json onepage/index.html` exited 2 with **1 finding under 1 rule**:
- `cream-palette` (warning, slop): page background `rgb(250, 246, 234)`, defined as `--cream: #faf6ea` at `onepage/index.html:10` and applied through `body { background: var(--cream) }` at line 19. The detector reports line 0 because it reads computed style.

**Where the two agree**: the detector's one finding supports the reviewer's verdict. The cream background is the "safe tasteful off-white" that makes this page interchangeable with others. The reviewer read the cream and green as "faintly bookkeeping". The detector reads the cream as a reflexive default. With no DESIGN.md naming cream as a brand color, nothing contradicts the detector, so **the finding stands as a true positive**.

**What the detector could not see**: the detector only checks mechanical patterns. It reported nothing on the three most serious problems the reviewer found (contradictory billing copy, the unaddressed bank-access question, no product evidence), and it did not flag the flat hierarchy of identical bands. There are no detector false positives to dismiss.

**Visual overlays**: none. The evidence collector's session had no browser automation tool and no live URL, so `detect.js` was never injected and **no overlay is visible in any browser tab**. The only mechanical signal is the CLI scan above.

## Overall Impression

The hero promise is strong and specific: "Books that close themselves." The page then fails to back it up. It shows no evidence, contradicts itself on billing next to the CTA, says nothing about the bank access it depends on, and ends on two one-line legal stubs instead of a call to action. The visual layer is competent and accessible but generic.

**The single biggest opportunity**: show one real closed month. A sample month-end report set in tabular figures with ledger rules would give visitors proof of the promise and give the page the visual identity it currently lacks.

## What's Working

1. **The copy has a real audience and a real point of view.** "Reads the spreadsheet you already keep … without a new system to learn" names the reader's current habit and answers the switching-cost objection in one line. Pitching the product through the accountant (a readable report and a free accountant seat) is a smart, specific angle.
2. **The accessibility groundwork is unusually solid.** The page sets `lang`, uses correct landmarks and `aria-labelledby` sections, and has a clean h1 → h3 outline. Focus rings are 3px ink with an offset. Smooth scrolling is turned off for reduced-motion users. CTAs are at least 44px tall. Contrast passes AA: ink on cream 16.1:1, white on green 5.3:1, green links 4.9:1.
3. **The offer is simple and honest.** There is one plan and one price ($18/month), the trial needs no card, and both CTAs use the same label. There are no dark patterns to remove.

## Priority Issues

**[P1] Billing terms contradict each other where the visitor decides**
- **What**: `onepage/index.html:129` says "Billed after the 14-day trial." The FAQ at `:147` says "nothing is billed unless you start the paid plan." Terms at `:162` says "Billing starts only when the customer chooses the paid plan." The first line suggests automatic conversion; the other two say billing is opt-in.
- **Why it matters**: this is the question that decides whether a cautious owner clicks, and the contradiction sits right next to the price and CTA. It reads as either carelessness or a trap, and a product that handles someone's books cannot afford either. A visitor who notices will stop and email support.
- **Fix**: choose the true policy and use one sentence for it everywhere. Put it under the price, for example "14 days free, no card. After that, $18/month only if you choose to continue." Repeat the same wording in the FAQ and Terms.
- **Suggested command**: `clarify`

**[P1] The page asks for bank access but never explains it**
- **What**: the "Bank import" feature "pulls in your bank transactions", but the page never says how the bank is connected, which banks are supported, whether access is read-only, or how to disconnect. The data FAQ covers only the spreadsheet, and its answer is "It stays in your account." Privacy is a single third-person sentence.
- **Why it matters**: for a small-business owner, bank access is the biggest barrier to signing up. Leaving it unanswered stalls the visitor right at the trial decision.
- **Fix**: add an FAQ item on the bank connection that covers the method, read-only scope, where credentials live, and how to disconnect. Rewrite the data answer to say where the data is stored and who can see it. Link to a real privacy policy instead of the one-line stub.
- **Suggested command**: `clarify`

**[P1] The core promise is never shown, and the visuals are interchangeable with any other page**
- **What**: there is no sample report, no spreadsheet-to-ledger view and no product image of any kind. The visual layer is system-ui on the detector-flagged cream (`--cream: #faf6ea`, line 10), with identical section bands.
- **Why it matters**: on a Persuade page, evidence is what converts. A claim as strong as "books that close themselves" makes visitors want proof. The generic visuals also mean nothing on the page is recognizably Harbor Ledger.
- **Fix**: add one real artifact. A cropped month-end report, or a spreadsheet row matched to a bank transaction, would work. Set it in tabular figures with ruled ledger lines, and let that artifact set the page's type, rules and palette. Replace the default cream with a background chosen for the ledger world (for example paper-white with ruled-column accents), not the warm off-white.
- **Suggested command**: `typeset`, then `colorize`

**[P2] The page ends on legal boilerplate instead of a close**
- **What**: after the FAQ come two h2 sections, Privacy and Terms, each holding one sentence written about "the customer", and then the footer. There is no CTA after the objections have been answered.
- **Why it matters**: under the peak-end rule, the last moment carries a lot of weight. At the point where the visitor is best informed and most ready to act, they get thin legalese. The stubs also flatten the hierarchy by giving boilerplate the same weight as the offer.
- **Fix**: end `main` with a short closing CTA band after the FAQ ("14 days free, no card"). Move Privacy and Terms out of `main` to real pages, or to a visually subordinate footer.
- **Suggested command**: `layout`

**[P2] "Files the books" is ambiguous and may promise too much**
- **What**: the hero and meta description ("files the month", lines 7 and 99) and Monthly close ("files the books for you", line 114) never say what is produced or where it goes.
- **Why it matters**: an owner or accountant may read "file" as a tax or regulatory filing. That is a larger promise, with liability implications, than the product may actually deliver.
- **Fix**: say exactly what happens, for example "At month end it reconciles every transaction and produces a closed-month report", and name the output format.
- **Suggested command**: `clarify`

> The suggested commands are Impeccable command names. This pack currently ships only the `critique` formula (`gc sling experiment/impeccable.conductor critique --formula --var target=onepage/index.html`), so these commands cannot yet be started through `gc sling … --formula`.

## Persona Red Flags

**Jordan (first-time small-business owner)**
- "Which spreadsheet?" Excel, Google Sheets and CSV are never mentioned, and neither is whether the file is uploaded or connected. The hero says it "reads the spreadsheet you already keep", while Privacy says "the spreadsheet the customer uploads". Those describe two different setups.
- Jordan reads literally and will stop at "Billed after the 14-day trial" (line 129) before ever reaching the FAQ that contradicts it.
- The plan heading "Harbor" means nothing on its own. Is it a tier? Are there others?
- Nothing says what happens after the CTA hands Jordan off to `app.harborledger.example`.

**Riley (stress tester)**
- "Books that close themselves" invites the question "and when they can't?" The page never says what happens when a bank transaction matches no spreadsheet row, or when the spreadsheet has an unusual layout.
- The three-way billing inconsistency is exactly the kind of gap between promise and reality that Riley writes up first.
- The FAQ promises a free accountant invite, but the features list never mentions inviting anyone.

**Casey (distracted mobile user)**
- The hero CTA is above the fold at 375px, which is good. After the FAQ, though, the nearest CTA is back up in Pricing, and there is no closing or sticky action.
- Footer links (Privacy, Terms, email) have no padding. Their tap height is about 26px, well under 44px, and they sit only 1.5rem apart.
- At 375px the headline wraps to three lines and leaves "close" alone on the middle line.

No project Design Context exists, so no project-specific personas were derived.

## Minor Observations

- The brand name is a `<span>`. It should link to the top of the page.
- There is no "Sign in" link. Returning customers will look for it in the header.
- The second CTA repeats the first word for word. Placed after the price, it could say "Start free, no card".
- The price (`2rem` bold) has no tabular figures and no scope: per business or per user? What's included? The free accountant seat, which is a pricing benefit, appears only in the FAQ.
- The feature copy repeats itself. "A report your accountant can read" is followed by "…a plain report that your accountant can read". "Files the books for you, so the close is done without you doing it by hand" says the same thing twice.
- The divider color `#d9d2bc` on cream has 1.4:1 contrast. On low-quality screens the bands blur into one another.
- There is no favicon, Open Graph image or social preview, so shared links will look bare.
- The meta description repeats the ambiguous "files the month", so the wording problem also shows up in search results.

## Questions to Consider

- If the month-end report is what the product actually produces, why isn't it the hero image? What would this page look like built around one real closed month?
- Is the trial opt-in or auto-converting? If a customer's inbox proves one of the three billing sentences wrong, which one will it be?
- "Harbor" and "Ledger" both suggest strong visuals (ruled columns, a safe mooring). What would make this page recognizable with the name covered up?
- Who is the page for: the owner who keeps the spreadsheet, or the accountant who reads the report? Could "send this to your accountant" turn the free accountant seat into a growth loop?
- Would one plain-language "Your data" section build more trust than two one-sentence legal stubs?

---

> **Trend for `onepage-index-html`:** First run for this target, no trend yet (20/32, heuristics 7 and 10 n/a).
> Wrote `.impeccable/critique/2026-09-28T09-13-24Z__onepage-index-html.md`.

## Questions for the user

1. **Priority direction.** The report lists five issues in three areas. Which should be fixed first?
   - **A. Trust and billing copy.** Make the three billing statements agree (lines 129, 147, 162), add the bank-connection FAQ, and replace "files the books".
   - **B. Product evidence and identity.** Add a sample month-end report, and rebuild type, rules and palette around it, replacing the detector-flagged cream.
   - **C. Page structure.** Add a closing CTA after the FAQ, move the Privacy and Terms stubs out of `main`, and add a header sign-in link.

2. **Billing truth.** Which of the three billing statements is correct? The fix depends on your answer.
   - **A. Opt-in.** Nothing is billed unless the customer chooses the paid plan. The FAQ and Terms are right, and line 129 should change.
   - **B. Auto-convert.** Billing starts automatically after 14 days. Line 129 is right, the FAQ and Terms must change, and the page must say how to cancel.
   - **C. Not decided yet.** Hold billing copy changes until the policy is settled.

3. **Visual intent.** The system-ui on cream, single-column look scores as category-interchangeable, and the detector flags the cream as a reflexive default. Was that intended?
   - **A. Keep it quiet and plain,** but make it Harbor Ledger's own: ledger rules, tabular figures, and a background that isn't the default cream.
   - **B. Lean into the ledger/harbor world,** with a stronger identity built around the sample report (ruled columns, a mark, a distinct palette).
   - **C. The cream and green are deliberate brand colors.** Keep them, record them in a DESIGN.md, and fix only hierarchy and evidence.

4. **Scope.** How much should the next pass cover?
   - **A. The three P1s only** (billing, bank trust, product evidence).
   - **B. All five priority issues.**
   - **C. All five, plus the minor observations** (sign-in link, footer tap targets, favicon/OG image, repeated feature copy).
