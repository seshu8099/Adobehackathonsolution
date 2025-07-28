
import os
import json
import fitz  # PyMuPDF
from collections import Counter, defaultdict
import numpy as np
import re

HEADING_KEYWORDS = re.compile(r'^(Appendix|Chapter|Section|Summary|Background)\b', re.IGNORECASE)
LIST_ITEM     = re.compile(r'^((\d+\.)|(\w\.)|([IVXLCDM]+\.))\s')
URL_RSVP      = re.compile(r'^(www\.|http|RSVP)', re.IGNORECASE)
HYPHEN_LINE   = re.compile(r'^[-_\s]{3,}$')
MAX_TEXT_LEN  = 100
DELTA_SIZE    = 1.5 


def get_toc_outline(doc):
    toc = doc.get_toc(simple=False)
    if not toc:
        return None
    outline = []
    for entry in toc:
        level = entry[0]
        title = entry[1].strip() if len(entry) > 1 else ''
        page = (entry[2] - 1) if len(entry) > 2 else 0
        outline.append({'level': f'H{level}', 'text': title, 'page': page})
    return outline


def extract_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    spans = []
    for pno, page in enumerate(doc, start=0):
        for b in page.get_text('dict')['blocks']:
            text = ' '.join(s['text'] for ln in b.get('lines', []) for s in ln['spans']).strip()
            if not text or HYPHEN_LINE.match(text) or URL_RSVP.match(text):
                continue
            sizes = [round(s['size'],2) for ln in b.get('lines', []) for s in ln['spans']]
            flags = [s['flags'] for ln in b.get('lines', []) for s in ln['spans']]
            if not sizes:
                continue
            spans.append({
                'text': text,
                'page': pno,
                'y': b['bbox'][1],
                'x': b['bbox'][0],
                'size': float(np.median(sizes)),
                'is_bold': any(f & 16 for f in flags),
                'is_italic': any(f & 2 for f in flags)
            })
    doc.close()
    return spans


def cluster_sizes(spans, k=3):
    uniq = sorted({s['size'] for s in spans})
    if len(uniq) <= k:
        return {sz: idx for idx, sz in enumerate(sorted(uniq, reverse=True))}
    diffs = [(uniq[i+1]-uniq[i], i) for i in range(len(uniq)-1)]
    splits = sorted(diffs, reverse=True)[:k-1]
    idxs = sorted([i for _, i in splits])
    clusters = {}
    start = 0; label = 0
    for split in idxs + [len(uniq)-1]:
        for sz in uniq[start:split+1]:
            clusters[sz] = label
        label += 1; start = split+1
    return clusters


def score_blocks(spans):
    sizes = [s['size'] for s in spans]
    body = Counter(sizes).most_common(1)[0][0] if sizes else 0
    candidates = []
    for s in spans:
        if len(s['text']) > MAX_TEXT_LEN:
            continue
        score = 0
        score += max(0, s['size'] - body) * 1.2
        score += 1.5 if s['is_bold'] else 0
        score += 1.0 if s['is_italic'] else 0
        if HEADING_KEYWORDS.match(s['text']): score += 3
        if LIST_ITEM.match(s['text']): score += 2
        if s['y'] < 100: score += 1.5
        if s['x'] < 50: score += 0.5
        s['score'] = score
        if score > 2.5:
            candidates.append(s)
    return candidates


def assign_levels(cands):
    if not cands:
        return []
    # Compute body font to filter borderline clusters
    sizes_all = [c['size'] for c in cands]
    body = Counter(sizes_all).most_common(1)[0][0]
    # Filter out spans whose size is too close to body text
    filtered = [c for c in cands if c['size'] > body + DELTA_SIZE]
    if not filtered:
        filtered = cands  # fallback if no cluster survives
    # Dynamically choose up to 4 clusters for deeper hierarchies
    max_clusters = min(4, len(set(round(c['size'],2) for c in filtered)))
    clusters = cluster_sizes(filtered, k=max_clusters)
    groups = defaultdict(list)
    for c in filtered:
        grp = clusters.get(round(c['size'],2), 0)
        groups[grp].append(c)
    outline = []
    # Map each group to heading levels H1..H4
    for grp in sorted(groups.keys()):
        level = grp + 1
        tag = f'H{level}'
        for b in sorted(groups[grp], key=lambda x: (x['page'], x['y'])):
            outline.append({'level': tag, 'text': b['text'], 'page': b['page']})
    # remove duplicates
    seen = set(); final = []
    for h in outline:
        key = (h['level'], h['text'])
        if key in seen: continue
        seen.add(key); final.append(h)
    return final
    if not cands:
        return []
    # Compute body font to filter borderline clusters
    sizes = [c['size'] for c in cands]
    body = Counter(sizes).most_common(1)[0][0]
    # Filter out spans whose size is too close to body text
    filtered = [c for c in cands if c['size'] > body + DELTA_SIZE]
    if not filtered:
        filtered = cands  # fallback if no cluster survives
    # Cluster remaining sizes
    clusters = cluster_sizes(filtered, k=3)
    groups = defaultdict(list)
    for c in filtered:
        groups[clusters.get(round(c['size'],2),0)].append(c)
    outline = []
    for lvl in sorted(groups.keys()):
        tag = f'H{lvl+1}'
        for b in sorted(groups[lvl], key=lambda x: (x['page'], x['y'])):
            outline.append({'level': tag, 'text': b['text'], 'page': b['page']})
    seen = set(); final = []
    for h in outline:
        key = (h['level'], h['text'])
        if key in seen: continue
        seen.add(key); final.append(h)
    return final


def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    toc = get_toc_outline(doc)
    doc.close()
    if toc:
        return {'title':'','outline':toc}
    spans = extract_blocks(pdf_path)
    cands = score_blocks(spans)
    headings = assign_levels(cands)
    title = ''
    for h in headings:
        if h['level']=='H1' and h['page']==0:
            title = h['text']; break
    headings = [h for h in headings if h['text'] != title]
    return {'title':title,'outline':headings}

if __name__=='__main__':
    inp, outp = 'input','output'
    os.makedirs(outp,exist_ok=True)
    for f in os.listdir(inp):
        if not f.lower().endswith('.pdf'): continue
        res = extract_outline(os.path.join(inp,f))
        with open(os.path.join(outp,f.replace('.pdf','.json')),'w',encoding='utf-8') as o:
            json.dump(res,o,indent=2,ensure_ascii=False)
        print(f'Processed {f}')
