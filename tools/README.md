# SE-MMAgents project page: developer notes

The repository root serves two things: `README.md`, the paper list rendered by GitHub, and `index.html`, the
project page at <https://jingjing12110.github.io/SE-MMAgents/>. This file covers the page only.

Source of the project page for **A Cross-Scenario Survey and Analysis of Self-Evolving Multimodal Agents**
(Jingjing Jiang, 2026), served at <https://jingjing12110.github.io/SE-MMAgents/>.

The layout follows the survey page of *Self-Improvements in Modern Agentic Systems*
(<https://selfimproving-agent.github.io/>), itself based on the Academic Project Page Template.

## Layout

```
index.html                 generated page (do not edit by hand, see below)
static/css/main.css        styles (template styles + additions for this survey)
static/js/main.js          library search/filters, figure zoom, BibTeX copy, GitHub stats
static/images/             figures cropped from the paper PDF (Fig. 1-4) and the favicon
static/pdfs/SE-MMAgents.pdf  paper PDF linked by the "Paper" buttons
data/papers.json           paper library, parsed from tables/4_mr ... 7_em_taxonomy.tex and 9_eval_benchmarks.tex
tools/template.html        page text and structure with {{PLACEHOLDERS}}
tools/build.py             fills the template from data/papers.json
.nojekyll                  lets GitHub Pages serve the files as-is
```

## Editing

1. Change text in `tools/template.html`, or library entries in `data/papers.json`
   (each entry accepts optional `url` and `code` fields, which override the arXiv/Scholar link and add a Code link).
2. Regenerate: `python3 tools/build.py .`
3. Preview locally: `python3 -m http.server` and open <http://localhost:8000>.

Settings at the top of `tools/build.py`:

- `ARXIV_URL`: `https://arxiv.org/abs/2611.14256`, used by the Paper button and the BibTeX entry.
- `REPO`: `jingjing12110/SE-MMAgents`, used for the GitHub buttons, issue templates, and live star/fork counts.

## Paper list

`README.md` tables are generated from the same `data/papers.json` and `data/links.json`.
Edit the data, then run `python3 tools/build_readme.py .`, which rewrites the block between the
`GENERATED` markers and leaves the surrounding prose alone.

## Deploying

Push the contents of this folder to the default branch of `github.com/jingjing12110/SE-MMAgents` and enable
GitHub Pages (Settings → Pages → Deploy from branch, root). The page is then served at
`https://jingjing12110.github.io/SE-MMAgents/`.
