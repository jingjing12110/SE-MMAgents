#!/usr/bin/env python3
"""Generate the paper-list sections of README.md from data/papers.json and data/links.json.

usage: python3 tools/build_readme.py [repo_root]
Rewrites the block between <!-- BEGIN GENERATED --> and <!-- END GENERATED --> in README.md.
"""
import json, os, sys, urllib.parse

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, 'data', 'papers.json')))
L = json.load(open(os.path.join(ROOT, 'data', 'links.json')))

SC = [
    ('mr', 'Multimodal Reasoning', 'High rollout and fidelity ceilings',
     'Question and visual-input source'),
    ('mg', 'Multimodal Generation', 'Low fidelity ceiling',
     'Verifier dependence on the policy'),
    ('gw', 'GUI and Web Navigation', 'Low rollout ceiling',
     'Allocation and reuse of scarce rollouts'),
    ('em', 'Embodied Manipulation', 'Both ceilings low on hardware',
     'Feedback source'),
    ('bench', 'Self-Evolution Benchmarks', 'Measuring self-evolving capability',
     'Scenario measured'),
]


def paper_url(o):
    if o.get('url'):
        return o['url']
    if o.get('arxiv'):
        return f"https://arxiv.org/abs/{o['arxiv']}"
    if o.get('doi'):
        return f"https://doi.org/{o['doi']}"
    return 'https://scholar.google.com/scholar?q=' + urllib.parse.quote('"' + o['title'] + '"')


def cell(s):
    return s.replace('|', '\\|').strip()


def link_text(s):
    # square brackets and underscores inside link text need escaping in GitHub markdown
    s = s.replace('[', '\\[').replace(']', '\\]')
    return cell(s)


SQUARE = {'A': '🟥', 'B': '🟦', 'E': '🟩'}


def role(s):
    parts = [x.strip() for x in (s or '').split('+') if x.strip()]
    return '/'.join(SQUARE.get(x, x) for x in parts) or '—'


def prov(o):
    return f"{role(o.get('sigma'))} {role(o.get('V'))} {role(o.get('f'))}"


def row(o):
    code = L.get(o['key'], {}).get('code', '')
    code_cell = f"[code]({code})" if code else '—'
    return (f"| {o['year']} | [{link_text(o['title'])}]({paper_url(o)}) | "
            f"{prov(o)} | {code_cell} |")


def bench_row(o):
    code = L.get(o['key'], {}).get('code', '')
    code_cell = f"[code]({code})" if code else '—'
    return (f"| {o['year']} | [{link_text(o['title'])}]({paper_url(o)}) | "
            f"{cell(o['tasks'])} | {cell(o['writes'])} | {code_cell} |")


out = []
for sc, title, quad, var in SC:
    rows = [o for o in P if o['scenario'] == sc]
    if not rows:
        continue
    out.append(f"### {title}\n")
    out.append(f"<sub>{quad}. Rows are grouped by {var.lower()}.</sub>\n")
    groups = []
    for o in rows:
        if o['group'] not in groups:
            groups.append(o['group'])
    for g in groups:
        grp = sorted([o for o in rows if o['group'] == g], key=lambda o: (o['year'], o['name'].lower()))
        out.append(f"<details open>\n<summary><b>{g}</b> ({len(grp)})</summary>\n")
        if sc == 'bench':
            out.append("| 📅 Year | 📝 Title | 🧪 Tasks | ✍️ Writes | 💻 Code |")
            out.append("|------:|--------|--------|--------|--------|")
            out.extend(bench_row(o) for o in grp)
        else:
            out.append("| 📅 Year | 📝 Title | 🔀 Provenance | 💻 Code |")
            out.append("|------:|--------|--------|--------|")
            out.extend(row(o) for o in grp)
        out.append("\n</details>\n")

block = "\n".join(out).rstrip() + "\n"

path = os.path.join(ROOT, 'README.md')
readme = open(path, encoding='utf-8').read()
a = readme.index('<!-- BEGIN GENERATED -->') + len('<!-- BEGIN GENERATED -->')
b = readme.index('<!-- END GENERATED -->')
readme = readme[:a] + "\n\n" + block + "\n" + readme[b:]
open(path, 'w', encoding='utf-8').write(readme)
print(f'wrote {path}: {len(P)} entries, '
      f'{sum(1 for o in P if L.get(o["key"], {}).get("code"))} with code')
