# Assessment B: Detector + Browser Evidence

## Detector command and exit code

```
/opt/gascity/packs/impeccable/skill/scripts/impeccable detect --json index.html
```
Run from the repo root `/opt/gascity/projects/impeccable-pack`. **Exit code: 2** (findings present). Target is a single markup file (index.html, 234 lines, inline `<style>`), so no need to narrow scope.

## Findings

4 findings across 2 rules. All are severity `warning`, category `slop`. The detector reported `"line": 0` for every finding, so it gave no line numbers. The source lines below come from matching each snippet against `index.html`.

| rule | count | locations (detector snippet → source line) |
|---|---|---|
| `icon-tile-stack` (Icon tile stacked above heading) | 3 | "40x40px icon tile above h3 "Live dashboards"" → index.html:205–206; "…"Ad-hoc queries"" → index.html:210–211; "…"Alerts that matter"" → index.html:215–216. The tile is styled by `.card .icon` at index.html:128–138 (40×40, border-radius 10px, `--accent-soft` background, emoji glyphs 📊 🔍 🔔). |
| `kicker-above-heading` (Kicker / eyebrow label above heading) | 1 | "kicker "Features" above h2 "Built for teams that ship"" → index.html:201–202. Styled by `.section-title` at index.html:99–107 (13px, 700, uppercase, letter-spacing 0.08em, accent color). |

Raw JSON (the `description` fields are shortened here; the full text is in the detector output):

```json
[
  {"antipattern":"icon-tile-stack","name":"Icon tile stacked above heading","severity":"warning","category":"slop","file":"/opt/gascity/projects/impeccable-pack/index.html","line":0,"snippet":"40x40px icon tile above h3 \"Live dashboards\""},
  {"antipattern":"icon-tile-stack","name":"Icon tile stacked above heading","severity":"warning","category":"slop","file":"/opt/gascity/projects/impeccable-pack/index.html","line":0,"snippet":"40x40px icon tile above h3 \"Ad-hoc queries\""},
  {"antipattern":"icon-tile-stack","name":"Icon tile stacked above heading","severity":"warning","category":"slop","file":"/opt/gascity/projects/impeccable-pack/index.html","line":0,"snippet":"40x40px icon tile above h3 \"Alerts that matter\""},
  {"antipattern":"kicker-above-heading","name":"Kicker / eyebrow label above heading","severity":"warning","category":"slop","file":"/opt/gascity/projects/impeccable-pack/index.html","line":0,"snippet":"kicker \"Features\" above h2 \"Built for teams that ship\""}
]
```

Rule descriptions, as the detector gave them:
- icon-tile-stack: "A small rounded-square icon container above a heading is the universal AI feature-card template … Try a side-by-side icon and heading, or let the icon sit in flow without its own container."
- kicker-above-heading: "A tiny tracked uppercase or small-caps label sitting as its own block directly above a heading is banned outright, repeated or not. … Delete the label and let the heading speak; if the words matter, work them into the heading or the body."

## Likely false positives

None identified. I checked each finding against the source, and each one matches its rule's stated trigger:
- icon-tile-stack ×3: each card has a real 40×40 rounded container (`.card .icon`) placed directly above an `<h3>`. This is a true match.
- kicker-above-heading ×1: `<p class="section-title">Features</p>` is a block-level, 13px, uppercase, tracked label directly above the `<h2>`. This is a true match.

The three icon-tile-stack findings come from one repeated component (a single CSS rule used three times), so fixing it is one change, not three.

The reporting has one gap, and it is not a false positive: every finding has `line: 0`. The source line numbers above were added by hand.

The detector did not flag these, and I did not audit them (this is evidence only, not design judgement): the emoji used as icons, the `href="#"` placeholder links, and the hard-coded `#fff` and `#4338ca` that sit outside the tokens.

## Browser evidence

**Skipped.** This session has no browser automation:
- No native browser or canvas tool is exposed. The connected MCP servers are Figma, Canva, Docs, Gmail and similar; none of them drives a browser.
- No fallback was available for a custom script: `chromium`, `chromium-browser`, `google-chrome`, `google-chrome-stable` and `firefox` are not on PATH; `~/.cache/ms-playwright` does not exist; Node cannot resolve `playwright` or `puppeteer`; and Python has no `playwright` module.
- Per the harness notes, I did not install one.

As a result, the mutation preflight (setting `document.title` and appending a `<script>`) could not run, and the fallback signal applies: there is no runtime or computed-style evidence. That means no rendered contrast, layout or overflow checks and no console overlay findings. The packet also says the server on 127.0.0.1:8080 serves different bytes from index.html, so it would not have been a valid browser target anyway.

## Skipped or failed steps

- Browser tab creation or navigation: skipped because no browser tool or binary exists (see above).
- Mutable-injection preflight: skipped for the same reason.
- `impeccable live-server --background`: not started, because the flow says to skip the live server when mutation is unavailable. I also noticed that this launcher's `--help` does not list a `live-server` command (it lists detect, ignores, help, install, link, update, check). No server was started, so none needed stopping.
- `detect.js` overlay injection and `impeccable` console capture: skipped because there was no browser.
- Multi-view sampling: not applicable, since this is a single-page target.
- CLI scan: **completed**, with exit code 2 and 4 findings. The parent can reuse these results; the counts, rule names and file are all present. The one gap is that the detector's line numbers are 0; source lines are given above.
