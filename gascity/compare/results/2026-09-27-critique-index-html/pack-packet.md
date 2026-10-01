# Critique packet
- target: index.html
- slug: index-html
- live_url: none
- mode: Persuade
- design_context: none
- ignore_list: none
- notes: Single static HTML file (/opt/gascity/projects/impeccable-pack/index.html, ~5 KB) with inline <style> and CSS custom properties on :root; no framework, no external scripts or stylesheets. View it by opening the file directly or serving the repo root with any static server (e.g. `python3 -m http.server` in the repo root). The surface is a single-page product marketing page for "Northwind Analytics" (header nav, hero with CTA, features section, footer). A server on 127.0.0.1:8080 also returns a page titled "Northwind Analytics", but its bytes differ from this file (first difference at line 150), so it is not the target; assess the source file. Project context: `impeccable context` ran successfully and reported no PRODUCT.md and no DESIGN.md; the incumbent code is the only design authority, and missing DESIGN.md is a documentation gap. `.impeccable/critique/ignore.md` does not exist. No automatic detector hook is active; run `$IMPECCABLE_PACK/skill/scripts/impeccable detect --json index.html` for the deterministic scan.
