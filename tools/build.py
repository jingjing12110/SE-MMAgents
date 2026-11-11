#!/usr/bin/env python3
"""Generate index.html for the SE-MMAgents survey page from data/papers.json."""
import json, html, re, sys, os, urllib.parse, collections

OUT = sys.argv[1] if len(sys.argv) > 1 else 'site'
P = json.load(open(os.path.join(OUT, 'data', 'papers.json')))
_lp = os.path.join(OUT, 'data', 'links.json')
LINKS = json.load(open(_lp)) if os.path.exists(_lp) else {}   # {cite_key: {"url": ..., "code": ...}}
for _o in P:
    _o.update({k: v for k, v in LINKS.get(_o['key'], {}).items() if v})
_ap = os.path.join(OUT, 'data', 'all_papers.json')
ALL = json.load(open(_ap)) if os.path.exists(_ap) else []
E = html.escape

REPO = 'jingjing12110/SE-MMAgents'
REPO_URL = f'https://github.com/{REPO}'
PAGE_URL = 'https://jingjing12110.github.io/SE-MMAgents/'
ARXIV_URL = 'https://arxiv.org/abs/2611.14256'
PDF_URL = 'static/pdfs/SE-MMAgents.pdf'
TITLE = 'A Cross-Scenario Survey and Analysis of Self-Evolving Multimodal Agents'

SC = collections.OrderedDict([
    ('mr', dict(name='Multimodal Reasoning', short='MR', id='lib-mr',
        quad='High rollout and fidelity ceilings',
        desc='Rollouts are single decoding passes and short answers admit exact match against a pre-collected or computed reference. Weight-updating loops mostly pose their own questions or train on unlabeled ones, which ties the evaluator to the model it trains, while training-free loops keep a frozen VLM and let the agent write the skills or tools it reuses.')),
    ('mg', dict(name='Multimodal Generation', short='MG', id='lib-mg',
        quad='Low fidelity ceiling',
        desc='An open-ended image or video has no reference output outside sub-families such as object counts, rendered text, or program-drawn charts. Weight-updating loops mostly derive the verifier from the agent, letting its bias move with the policy, and training-free loops let a frozen backbone judge its own outputs and write its memory or skills.')),
    ('gw', dict(name='GUI and Web Navigation', short='GW', id='lib-gw',
        quad='Low rollout ceiling',
        desc='Each rollout is a multi-step episode that pays environment latency at every step, whereas the inspectable end state of an application or a web page keeps the attainable fidelity high in sandboxed environments. Weight-updating loops allocate scarce rollouts by proposing or reweighting goals, and training-free loops reuse each episode through memory or skills.')),
    ('em', dict(name='Embodied Manipulation', short='EM', id='lib-em',
        quad='Both ceilings low on hardware',
        desc='Each rollout costs robot time, a reset, and wear, and each outcome is checkable only by a per-task classifier or a learned judge. Simulation relaxes both ceilings, and the methods differ chiefly in feedback source, namely simulator predicates, agent-derived verifiers, or external judges.')),
    ('bench', dict(name='Self-Evolution Benchmarks', short='Bench', id='lib-bench',
        quad='Measuring self-evolving capability',
        desc='Benchmarks that let an agent write to persistent components across rounds or tasks and report how its score changes, grouped by scenario. They are the measurement side of the survey and record which of the loop-level quantities each benchmark reports.')),
])

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def link_of(o):
    if o.get('url'):
        return o['url']
    if o.get('arxiv'):
        return f"https://arxiv.org/abs/{o['arxiv']}"
    if o.get('doi'):
        return f"https://doi.org/{o['doi']}"
    return ''

def scholar(o):
    return 'https://scholar.google.com/scholar?q=' + urllib.parse.quote('"' + o['title'] + '"')

def sup(s):
    return re.sub(r'\^(\w+|†|‡)', r'<sup>\1</sup>', E(s))

def role_html(s):
    # 'A', 'B', 'E', 'E+A', 'B+A' ...
    parts = [x.strip() for x in s.split('+')]
    if all(x in ('A', 'B', 'E') for x in parts):
        return ''.join(f'<span class="role {x}" title="{dict(A="agent",B="bootstrap",E="environment or task generation")[x]}">{x}</span>' for x in parts)
    return E(s)

def links_html(o):
    out = []
    u = link_of(o)
    if u:
        out.append(f'<a href="{E(u)}" rel="noopener" target="_blank">Paper</a>')
    else:
        out.append(f'<a href="{E(scholar(o))}" rel="noopener" target="_blank" title="Search the title on Google Scholar">Paper</a>')
    code = o.get('code')
    if code:
        out.append(f'<a href="{E(code)}" rel="noopener" target="_blank">Code</a>')
    else:
        out.append('<span class="muted-link" title="No public code found as of November 2026">Code</span>')
    return ' · '.join(out)

def search_text(o):
    return ' '.join([o['year'], o['name'], o['title'], o.get('venue_name', ''), o.get('group', ''),
                     o.get('signal', ''), o.get('update', ''), o.get('backbone', ''), o.get('tasks', '')]).lower()

def method_row(o):
    tf = o.get('training_free')
    branch = o['scenario']
    tfb = '<span class="tf-badge" title="frozen backbone, the loop writes memory, tools, skills, or instructions">training-free</span>' if tf else ''
    return (f'<tr class="paper-row" data-branch="{branch}" data-tf="{"1" if tf else "0"}" data-year="{o["year"]}" data-search="{E(search_text(o))}">'
            f'<td class="year">{o["year"]}</td>'
            f'<td class="title-cell"><span class="mname">{E(o["name"])}{tfb}</span><span class="ptitle" title="{E(o["title"])}">{E(o["title"])}</span></td>'
            f'<td>{E(o["venue_name"])}</td>'
            f'<td class="small">{role_html(o["V"])} {sup(o["signal"])}</td>'
            f'<td class="small">{role_html(o["f"])} {sup(o["update"])}</td>'
            f'<td class="links">{links_html(o)}</td></tr>')

def bench_row(o):
    return (f'<tr class="paper-row benchmark-row" data-branch="bench" data-tf="0" data-year="{o["year"]}" data-search="{E(search_text(o))}">'
            f'<td class="year">{o["year"]}</td>'
            f'<td class="title-cell"><span class="mname">{E(o["name"])}</span><span class="ptitle">{E(o["title"])}</span></td>'
            f'<td class="small">{E(o["tasks"])}</td>'
            f'<td class="small">{sup(o["feedback"])}</td>'
            f'<td class="small">{E(o["writes"])}</td>'
            f'<td class="links">{links_html(o)}</td></tr>')

def groups(sc):
    g = collections.OrderedDict()
    for o in P:
        if o['scenario'] == sc:
            g.setdefault(o['group'], []).append(o)
    return g

counts = {sc: sum(1 for o in P if o['scenario'] == sc) for sc in SC}
n_methods = sum(counts[s] for s in ('mr', 'mg', 'gw', 'em'))
n_tf = sum(1 for o in P if o['scenario'] != 'bench' and o['training_free'])

# ---------------------------------------------------------------- library
lib = []
for sc, meta in SC.items():
    g = groups(sc)
    lib.append(f'<div class="library-block" id="{meta["id"]}" data-block="{sc}"><div class="block-head"><div>'
               f'<h3>{list(SC).index(sc)+1}. {E(meta["name"])}</h3><p>{E(meta["desc"])}</p></div>'
               f'<div class="count-badge">{counts[sc]} {"benchmarks" if sc=="bench" else "methods"}</div></div>')
    for gi, (gname, rows) in enumerate(g.items()):
        gid = f'{sc}-{slug(gname)}'
        lib.append(f'<details class="subgroup" id="{gid}" open><summary><span>{list(SC).index(sc)+1}.{gi+1} {E(gname)}</span>'
                   f'<span class="count-badge small">{len(rows)} {"entries" if sc=="bench" else "methods"}</span></summary>'
                   '<div class="table-wrap"><table class="paper-table"><thead><tr>')
        if sc == 'bench':
            lib.append('<th>Year</th><th>Benchmark</th><th>Tasks</th><th>Feedback</th><th>Writes</th><th>Links</th></tr></thead><tbody>')
            lib.extend(bench_row(o) for o in rows)
        else:
            lib.append('<th>Year</th><th>Method</th><th>Venue</th><th>Feedback (<span class="math">V</span>)</th><th>Update (<span class="math">f</span>)</th><th>Links</th></tr></thead><tbody>')
            lib.extend(method_row(o) for o in rows)
        lib.append('</tbody></table></div></details>')
    lib.append('</div>')
LIB = '\n'.join(lib)

# ---------------------------------------------------------------- all papers by chapter
CODE = {o['key']: o.get('code', '') for o in P}
def ref_row(r):
    r = dict(r); r.update({k: v for k, v in LINKS.get(r['key'], {}).items() if v})
    r.setdefault('code', CODE.get(r['key'], ''))
    if not r.get('code'): r['code'] = CODE.get(r['key'], '')
    st = ' '.join([r['year'], r['title'], r['venue'], r['key']]).lower()
    return (f'<tr class="paper-row" data-branch="ref" data-tf="0" data-year="{E(r["year"])}" data-search="{E(st)}">'
            f'<td class="year">{E(r["year"])}</td><td class="title-cell">{E(r["title"])}</td>'
            f'<td>{E(r["venue"])}</td><td class="links">{links_html(r)}</td></tr>')
ar, toc_all = [], []
for i, g in enumerate(ALL, 1):
    gid = f'ref-{i}'
    rows = sorted(g['papers'], key=lambda r: (r['year'] or '9999'))
    toc_all.append(f'<a class="sub2" href="#{gid}">{i}. {E(g["chapter"])}</a>')
    ar.append(f'<div class="library-block" data-block="ref"><details class="subgroup" id="{gid}" open><summary><span>{i}. {E(g["chapter"])}</span>'
              f'<span class="count-badge small">{len(rows)} papers</span></summary>'
              '<div class="table-wrap"><table class="paper-table"><thead><tr><th>Year</th><th>Title</th><th>Venue</th><th>Links</th></tr></thead><tbody>'
              + ''.join(ref_row(r) for r in rows) + '</tbody></table></div></details></div>')
ALLREFS = '\n'.join(ar)
N_REFS = sum(len(g['papers']) for g in ALL)

# ---------------------------------------------------------------- taxonomy cards
tax = []
for sc, meta in SC.items():
    g = groups(sc)
    items = ''.join(f'<li><a href="#{sc}-{slug(k)}">{E(k)}</a> <span class="mini-count">{len(v)}</span></li>' for k, v in g.items())
    tax.append(f'<div class="tax-card {sc}"><h4><a href="#{meta["id"]}" style="color:inherit">{E(meta["name"])}</a> <span class="mini-count">{counts[sc]} {"benchmarks" if sc=="bench" else "methods"}</span></h4>'
               f'<div class="quad-note">{E(meta["quad"])}</div><ul>{items}</ul></div>')
TAX = '\n'.join(tax)

# ---------------------------------------------------------------- verdict matrix (Table 12 of the paper)
V = {'P': ('port', 'portable'), 'C': ('cond', 'conditional'), 'B': ('block', 'blocked'), 'R': ('red', 'redundant')}
def cell(spec):
    out = []
    for tok in spec.split():
        k, _, sup = tok.partition('^')
        cls, lab = V[k]
        sup_html = f'<sup>{E(sup)}</sup>' if sup else ''
        out.append(f'<span class="v {cls}" title="{lab}{(" ("+sup+")") if sup else ""}">{lab[:4] if False else lab}{sup_html}</span>')
    return ''.join(out)
VERDICTS = [
    ('Presupposes a task-structural resource', [
        ('Success-conditioned allocation', 'P^*', 'C^*', 'P^*', 'C^* P^*e'),
        ('Agent-posed goals', 'P^*', 'C^*', 'P^* B^g', 'C B^f P^*e'),
        ('Record-conditioned goal generation', 'P', 'C', 'P^* B^g', 'C B^f'),
        ('Program-checkable goal families', 'P^*', 'C^*', 'P', 'C P^*e'),
        ('Imagined rollouts in a world model', 'R', 'R', 'C', 'C^*'),
        ('Self-consistency vote', 'R^a P^*b', 'C^*', 'R^c C^d B^g', 'C B^f'),
    ]),
    ("Presupposes only the agent's model or a pre-loop artifact", [
        ("Self-judgment by the agent's model", 'R^a P^*b', 'P^*', 'R^c P^*d B^g', 'P^* B^f'),
        ('Generator-confidence reward', 'R^a P^b', 'P^*', 'R^c P', 'P'),
        ('Verifier refit on agent trajectories', 'R^a P^b', 'P^*', 'P^* C^g', 'P C^f P^*e'),
        ('Frozen self-derived estimator', 'R^a P^*b', 'P^*', 'P C^g', 'P^* C^f'),
        ('Episode reuse via memory, skills, or harnesses', 'P^*', 'P^*', 'P^* C^g', 'P^* C^f'),
    ]),
]
vr = []
for gname, rows in VERDICTS:
    vr.append(f'<tr class="group"><td colspan="5">{E(gname)}</td></tr>')
    for r in rows:
        vr.append('<tr><td class="mech">' + E(r[0]) + '</td>' + ''.join(f'<td>{cell(c)}</td>' for c in r[1:]) + '</tr>')
VERDICT_ROWS = '\n'.join(vr)

# ---------------------------------------------------------------- trade-off table (Table 11 of the paper)
M = lambda s: f'<span class="math">{s}</span>'
TRADE = [
    ('Experience generation', [
        ('Success-conditioned allocation', M('σ<sub>ω</sub>'), M('𝔼[I<sub>𝒜<sub>k</sub></sub>]'), 'fixed task set with checkable outcomes (T)', 'coverage of tasks dropped by design', 'curriculum collapse'),
        ('Agent-posed goals', M('σ<sub>ω</sub>'), M('𝔼[I<sub>𝒜<sub>k</sub></sub>]'), 'checkable outcomes or output equivalence (T)', 'pooled keys or scripts, label accuracy 72% to 61%', 'curriculum collapse'),
        ('Record-conditioned goal generation', M('σ<sub>ω</sub>'), M('𝔼[I<sub>𝒜<sub>k</sub></sub>]'), 'checkable outcomes or output equivalence (T)', 'pooled keys or scripts', 'curriculum collapse'),
        ('Program-checkable goal families', M('σ<sub>ω</sub>'), M('𝔼[I<sub>𝒜<sub>k</sub></sub>]') + ' at a program-checked ' + M('F<sub>ν</sub>'), 'program, simulator, or scripted scene checks (T)', 'coverage outside the family', 'forgetting'),
        ('Imagined rollouts in a world model', M('V<sub>ν</sub>'), M('K<sub>k</sub>') + ' beyond ' + M('K̄') + ' via imagined rollouts', 'learnable short-horizon dynamics (T)', M('F<sub>ν</sub>') + ' via model error, video degrades past 300 frames', 'distribution shift, model collapse'),
    ]),
    ('Feedback acquisition', [
        ('Self-consistency vote', M('V<sub>ν</sub>'), M('F<sub>ν</sub>') + ' without keys', 'output equivalence (T), prior on the true answer (M)', M('K<sub>k</sub>') + ' rollouts per goal, label errors', 'compounding hacking'),
        ("Self-judgment by the agent's model", M('V<sub>ν</sub>'), M('F<sub>ν</sub>') + ' without checkers', 'generation-verification gap (M)', 'fidelity moving with the policy', 'compounding hacking'),
        ('Generator-confidence reward', M('V<sub>ν</sub>'), M('F<sub>ν</sub>') + ' without checkers', "generator's confidence (M)", 'fidelity tied to updated weights', 'compounding hacking'),
        ('Verifier refit on agent trajectories', M('V<sub>ν</sub>'), M('L<sub>ν</sub>') + ', or ' + M('F<sub>ν</sub>') + ' on free-form goals', 'labeled seed or reference set', 'fidelity moving with the policy', 'compounding hacking'),
        ('Frozen self-derived estimator', M('V<sub>ν</sub>'), M('L<sub>ν</sub>') + ', or ' + M('F<sub>ν</sub>') + ' on free-form goals', 'demonstrations or ' + M('𝒜<sub>0</sub>') + ' calibration', 'fixed bias off the training support', 'distribution shift'),
    ]),
    ('Update consolidation', [
        ('Episode reuse via memory or skills', M('f<sub>ζ</sub>'), M('G<sub>ζ</sub>') + ', ' + M('𝔼[I<sub>𝒜<sub>k</sub></sub>]') + ' on hard goals', "writer's generation-verification gap (M) or an online check (T)", "exposure to the writer's errors", 'erroneous writes'),
    ]),
]
tr = []
for gname, rows in TRADE:
    tr.append(f'<tr class="group"><td colspan="6" style="background:#fbfbfc;font-style:italic;color:var(--muted)">{E(gname)}</td></tr>')
    for r in rows:
        tr.append(f'<tr><td class="mech">{E(r[0])}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{E(r[5])}</td></tr>')
TRADE_ROWS = '\n'.join(tr)

# ---------------------------------------------------------------- quick start
QS_KEYS = [('visplay', 'Poses its own questions over unlabeled images and rewards answers by majority vote, a reference instance of agent-posed goals with consensus feedback.'),
           ('visionzero', 'Turns arbitrary images into competitive games whose computed outcomes supply the reward for self-play training.'),
           ('solace', 'Rewards a text-to-image generator with its own denoising confidence, the reference case of generator-confidence reward and its within-run hacking.'),
           ('asg', 'Scores generated images by answer agreement across framings of self-posed questions, carrying the vote from reasoning into generation.'),
           ('digirl', 'Trains a device-control agent with offline-to-online reinforcement learning, scoring episodes by a VLM evaluator and filtering steps with value functions.'),
           ('seagent', 'Generates new software tasks from its own exploration record and learns from a world-state judge, a reference case of record-conditioned goal generation.'),
           ('evovla', 'Trains a vision-language-action policy with PPO against stage rewards from an external model plus pose curiosity, moving from simulation to hardware.'),
           ('searrobot', 'Lets coding agents design their own robot practice and write code skills and memories, and doubles as a benchmark with a sealed judge and an explicit budget.')]
byk = {o['key']: o for o in P}
qs = []
for k, d in QS_KEYS:
    o = byk[k]
    u = link_of(o) or scholar(o)
    qs.append(f'<div class="ref-card"><strong><a href="{E(u)}" rel="noopener" target="_blank">{E(o["name"])}</a></strong>'
              f'<div class="meta">{o["year"]} · {E(SC[o["scenario"]]["name"])}</div><p>{E(d)}</p></div>')
QS = '\n'.join(qs)

# ---------------------------------------------------------------- sidebar toc
toc_sub = ''.join(f'<a class="sub2" href="#{m["id"]}">{list(SC).index(s)+1}. {E(m["name"])}</a>' for s, m in SC.items())

ARXIV_BTN = (f'<a class="btn" href="{ARXIV_URL}" rel="noopener" target="_blank">arXiv</a>' if ARXIV_URL
             else '<span class="btn disabled" title="arXiv link coming soon">arXiv (coming soon)</span>')

BIB = f"""@article{{jiang2026selfevolvingmmagents,
	title   = {{{TITLE}}},
	author  = {{Jiang, Jingjing}},
	journal = {{arXiv preprint arXiv:2611.14256}},
	year    = {{2026}}
}}"""

DESC = ('A survey of self-evolving multimodal agents across multimodal reasoning, multimodal generation, '
        'GUI and Web navigation, and embodied manipulation, analyzing the structural source of the cross-scenario '
        'asymmetry in how their mechanisms transfer.')

# Math: every <span class="math"> carries the HTML of a symbol; render it as TeX for KaTeX in the browser.
TEX = {
    'V': 'V', 'f': 'f', 'k': 'k',
    'σ<sub>ω</sub>': r'\sigma_\omega', 'V<sub>ν</sub>': r'V_\nu', 'F<sub>ν</sub>': r'F_\nu',
    'K̄': r'\bar{K}', 'F̄': r'\bar{F}', 'K<sub>k</sub>': r'K_k', 'L<sub>ν</sub>': r'L_\nu',
    '𝔼[I<sub>𝒜<sub>k</sub></sub>]': r'\mathbb{E}[I_{\mathcal{A}_k}]',
    'I<sub>𝒜<sub>k</sub></sub>': r'I_{\mathcal{A}_k}',
    'f<sub>ζ</sub>': r'f_\zeta', 'G<sub>ζ</sub>': r'G_\zeta', 'S<sub>ζ</sub>': r'S_\zeta',
    '𝒬<sub>k</sub>': r'\mathcal{Q}_k', '𝒜<sub>k</sub>': r'\mathcal{A}_k', '𝒜<sub>0</sub>': r'\mathcal{A}_0',
    '𝒫<sub>g</sub>': r'\mathcal{P}_g', '𝒟<sub>k</sub>': r'\mathcal{D}_k',
}
def _math(m):
    return f'<span class="math" data-tex="{E(TEX[m.group(1)])}"></span>'

page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')).read()
for k, v in dict(TITLE=E(TITLE), DESC=E(DESC), PAGE_URL=PAGE_URL, REPO=REPO, REPO_URL=REPO_URL, PDF_URL=PDF_URL, ARXIV_URL=ARXIV_URL,
                 ARXIV_BTN=ARXIV_BTN, LIB=LIB, TAX=TAX, VERDICT_ROWS=VERDICT_ROWS, TRADE_ROWS=TRADE_ROWS, QS=QS,
                 TOC_SUB=toc_sub, TOC_ALL=''.join(toc_all), ALLREFS=ALLREFS, N_REFS=str(N_REFS), BIB=E(BIB), N_ALL=str(len(P)), N_METHODS=str(n_methods), N_TF=str(n_tf),
                 N_MR=str(counts['mr']), N_MG=str(counts['mg']), N_GW=str(counts['gw']), N_EM=str(counts['em']),
                 N_BENCH=str(counts['bench'])).items():
    page = page.replace('{{' + k + '}}', v)
assert '{{' not in page, re.findall(r'\{\{\w+\}\}', page)
page = re.sub(r'<span class="math">(.*?)</span>', _math, page)
open(os.path.join(OUT, 'index.html'), 'w').write(page)
print('wrote', os.path.join(OUT, 'index.html'), len(page), 'bytes;', len(P), 'entries')
