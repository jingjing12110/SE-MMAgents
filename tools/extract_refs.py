#!/usr/bin/env python3
"""Collect every reference cited in the survey and group it by the chapter where it is first cited.

usage: python3 tools/extract_refs.py ../Latex4arXiv   ->  writes data/all_papers.json
Follows main.tex -> chapters -> \\input{tables|figures} in document order.
"""
import re, json, os, sys

LATEX = sys.argv[1] if len(sys.argv) > 1 else '../Latex4arXiv'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VENUE_SHORT = {'PAMI': 'TPAMI', 'PR': 'Pattern Recognition', 'AIJ': 'Artificial Intelligence',
               'FCS': 'Front. Comput. Sci.', 'SCIS': 'Sci. China Inf. Sci.', 'ACMMM': 'ACM MM',
               'NeurIPSW': 'NeurIPS Workshop', 'NeurIPSDB': 'NeurIPS D&B', 'ICLRW': 'ICLR Workshop',
               'ICMLW': 'ICML Workshop', 'CVPRW': 'CVPR Workshop', 'FindingsACL': 'ACL Findings',
               'FindingsEMNLP': 'EMNLP Findings', 'SIGART': 'SIGART Bull.', 'SP': 'IEEE S&P',
               'NATURE': 'Nature', 'SCIENCE': 'Science', 'TECHRXIV': 'TechRxiv', 'PREPRINTS': 'Preprints'}

def strip_comments(t):
    return '\n'.join(re.sub(r'(?<!\\)%.*', '', l) for l in t.splitlines())

def read_tex(rel):
    p = os.path.join(LATEX, rel if rel.endswith('.tex') else rel + '.tex')
    return strip_comments(open(p, encoding='utf-8').read()) if os.path.exists(p) else ''

def expand(t):
    return re.sub(r'\\input\{([^}]*)\}', lambda m: expand(read_tex(m.group(1))), t)

def clean(s):
    s = re.sub(r'\\[`\'^"~=.]\{?(\w)\}?', r'\1', s)
    s = s.replace('\\&', '&').replace('--', '–').replace('~', ' ')
    s = re.sub(r'\$([^$]*)\$', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\*?\s*', '', s)
    s = s.replace('{', '').replace('}', '').replace('^', '')
    return re.sub(r'\s+', ' ', s).strip()

# ---- bib
bib = open(os.path.join(LATEX, 'ref.bib'), encoding='utf-8').read()
entries = {}
for m in re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}', bib, re.S):
    typ, key, body = m.groups()
    if typ.lower() == 'string':
        continue
    f = {}
    for fm in re.finditer(r'(\w+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|"[^"]*"|[A-Za-z0-9_]+)', body):
        k, v = fm.groups()
        f[k.lower()] = v
    entries[key] = f

def field(f, k):
    v = f.get(k, '')
    return v[1:-1] if v[:1] in '{"' else v

def venue_of(f):
    for k in ('booktitle', 'journal', 'howpublished', 'publisher', 'institution', 'school'):
        raw = f.get(k)
        if not raw:
            continue
        if raw[:1] not in '{"':
            return VENUE_SHORT.get(raw, raw)
        v = clean(raw[1:-1])
        if re.match(r'arxiv', v, re.I):
            return 'arXiv'
        return v
    return 'arXiv' if re.search(r'arxiv', ' '.join(f.values()), re.I) else ''

def arxiv_of(f):
    m = re.search(r'arXiv[:\s/]*(?:abs/)?(\d{4}\.\d{4,5})', ' '.join(f.values()), re.I)
    if m:
        return m.group(1)
    if field(f, 'archiveprefix').lower() == 'arxiv' and field(f, 'eprint'):
        return field(f, 'eprint')
    return ''

# ---- chapters in document order
main = strip_comments(open(os.path.join(LATEX, 'main.tex'), encoding='utf-8').read())
chapters = re.findall(r'\\input\{(chapters/[^}]*)\}', main)
seen, groups, missing = set(), [], []
for ch in chapters:
    t = expand(read_tex(ch))
    sec = re.search(r'\\section\*?\{([^}]*)\}', t)
    name = clean(sec.group(1)) if sec else ('Abstract' if 'abstract' in ch else ch)
    keys = []
    for m in re.finditer(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}', t):
        for k in m.group(1).split(','):
            k = k.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    rows = []
    for k in keys:
        f = entries.get(k)
        if f is None:
            missing.append(k); continue
        rows.append(dict(key=k, title=clean(field(f, 'title')), year=field(f, 'year'),
                         venue=venue_of(f), arxiv=arxiv_of(f),
                         doi=field(f, 'doi'), url=field(f, 'url')))
    if rows:
        groups.append(dict(chapter=name, file=ch, papers=rows))

json.dump(groups, open(os.path.join(ROOT, 'data', 'all_papers.json'), 'w'), indent=1, ensure_ascii=False)
print('chapters:', [(g['chapter'], len(g['papers'])) for g in groups])
print('total:', sum(len(g['papers']) for g in groups), '| missing bib:', missing)
