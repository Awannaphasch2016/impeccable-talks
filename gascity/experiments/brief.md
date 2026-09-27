# Brief: Harbor Ledger

Every decision below is final. Do not ask the owner anything. If a checklist
item is answered here, it is settled by the brief. Record factory's usual
TypeScript default as overridden by the constraint in section 7.

## 1. Purpose

Harbor Ledger is a one-page marketing site for a bookkeeping product used by
owners of businesses with 1 to 20 people. After reading the page, a visitor
knows what the product does and can start a 14-day trial.

Success is a click on the trial button. The site is not a web application, a
blog, a help center, or a sign-in screen.

## 2. Audience

Visitors are business owners who already keep books in a spreadsheet. They
arrive from a link. Design for a phone and a desktop equally. Language is
English only. Meet WCAG 2.1 AA.

## 3. Content and pages

One page, `site/index.html`. Sections, in order:

1. Header with the name Harbor Ledger and links that jump to Pricing and FAQ.
2. Hero. Headline: "Books that close themselves." One sentence of support:
   "Harbor Ledger reads the spreadsheet you already keep and files the month
   without a new system to learn." Primary action: "Start the 14-day trial".
3. Three features: bank import, monthly close, and a report the accountant
   can read. One sentence each. No icons that are only decoration.
4. Pricing. One plan, Harbor, 18 dollars a month after the trial. State that
   the trial needs no card.
5. FAQ. Three questions: where the spreadsheet data goes, whether an
   accountant can be invited, and what happens when the trial ends. Answers:
   data stays in the customer's account and is deletable; one accountant can
   be invited at no charge; the trial ends and nothing is billed unless the
   customer starts the paid plan.
6. Footer with links to the privacy policy and the terms, plus a contact
   address.

The copy above is the copy. Do not invent customers, quotes, awards, or
metrics. No photographs and no video. The page does not change after launch;
the owner edits the file.

## 4. Behaviour and data

The only action is the trial link. It goes to
`https://app.harborledger.example/signup`. No form, no account on this page,
no search, no comments, no uploads, nothing stored in a browser, no database.

The privacy link points at `#privacy` and the terms link at `#terms`. Both
sections are on this page, after the FAQ, and each is two sentences: Harbor
Ledger stores the spreadsheet the customer uploads and deletes it when the
customer asks; the trial is 14 days and billing starts only when the customer
chooses the paid plan.

## 5. Look

No existing brand. Use a cream page, near-black text, and one green
(`#1f7a4d`) for the trial button and the links. Type is a single sans-serif
stack. Tone is plain and specific, the way a careful bookkeeper speaks. No
gradients, no emoji, no illustrated backgrounds.

## 6. Running it

The site is one static file. It is not deployed by this task. Domain, when it
has one, will be harborledger.example. No analytics and no cookie banner,
because nothing is measured. The owner maintains the file.

## 7. Constraints

No deadline. The page must be `site/index.html`, valid HTML, with CSS in the
file and no request to another host. This overrides a TypeScript, Node, or
npm default: do not add a server, a package, or a build step. Legal pages are
the two on-page sections named above.
