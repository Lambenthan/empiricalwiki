# View the wiki as a local website (Quartz)

Render the `wiki/` markdown into a local website with **graph view, search, and clickable links**. It reads the same `wiki/` files — read-only, never modifies your content. Better than asking others to install Obsidian, ideal for sharing and recording demos.

Built on [Quartz](https://quartz.jzhao.xyz/) (an open-source static-site generator), pinned to the stable `v4.5.2`.

## Three steps

**Step 1: Install Node.js (once)**
Download the LTS from [nodejs.org](https://nodejs.org) and install. Verify with `node --version`.

**Step 2: Run one command from the project root**

```bash
tools/view.sh
```

- **First run** clones Quartz and installs deps (a few minutes, only the first time), then builds.
- Subsequent runs are fast.

**Step 3: Open the browser**
Go to `http://localhost:8080`. Press `Ctrl-C` to stop the preview.

## What you get

- **Home** = `wiki/index.md`, the full catalog.
- **Left** file tree by type (papers / assumptions / propositions / mechanisms …).
- **Right** backlinks per page (who references it).
- **Graph view**: the whole knowledge network; the theory↔empirics bridge is visible at a glance.
- **Top search**: full-text.

## Other modes

```bash
tools/view.sh           # build + local preview (default)
tools/view.sh --build   # build only; output in site/.quartz/public/ (upload to any static host)
tools/view.sh --update  # force-update the Quartz version, then build + preview
```

To publish online: upload `site/.quartz/public/` to GitHub Pages / Vercel / Netlify (all free).

## One authoring gotcha: the dollar sign `$`

Quartz treats `$...$` as math (KaTeX). So **dollar amounts** in body text must be escaped: write `\$1`, `\$(1+r)`, not `$1`. Otherwise CJK between the `$` gets rendered as a garbled formula.

- Real equations: use `$$...$$` (display) or inline `$...$` — fine.
- Stata macros like `$controls`: keep them inside ``` code blocks ``` and they are unaffected.

## Notes

- The whole `site/` directory is generated locally (Quartz clone + deps + build output) and is `.gitignore`d. Each person runs `tools/view.sh` on their own machine.
- `wiki/graph/`, `wiki/outputs/`, and `wiki/.obsidian/` are not rendered into the site.
- The site is read-only; to change content, edit the markdown under `wiki/` or use skills like `/ingest`, `/theory-ingest`, then re-run `tools/view.sh` to refresh.
