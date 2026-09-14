# -*- coding: utf-8 -*-
import re, io, glob, os
folder = r'C:\Users\USER\Downloads\excel compaire'
f = glob.glob(os.path.join(folder, r'stock-compare*.html'))[0]
s = io.open(f, encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', s, re.S)
script = m.group(1)
LANGS = ['fr', 'en', 'ar']

def find_block(lang):
    i = script.find(lang + ':')
    if i < 0: return None
    ob = script.find('{', i)
    depth = 0
    inq = None
    esc = False
    for j in range(ob, len(script)):
        c = script[j]
        if esc: esc = False; continue
        if c == '\\': esc = True; continue
        if inq:
            if c == inq: inq = None
            continue
        if c in ('"', "'"): inq = c; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return script[ob:j+1]
    return None

dicts = {}
for lang in LANGS:
    block = find_block(lang)
    keys = set()
    for mm in re.finditer(r"""(['"])([A-Za-z0-9_]+)\1\s*:""", block or ''):
        keys.add(mm.group(2))
    dicts[lang] = keys
    print('dict %s : %d keys' % (lang, len(keys)))

used = set()
for mm in re.finditer(r"""\bt(?:F)?\s*\(\s*['"]([A-Za-z0-9_]+)['"]\s*\)""", script):
    used.add(mm.group(1))
for pat in ('data-i18n', 'data-i18n-html', 'data-i18n-ph', 'data-i18n-title', 'data-i18n-aria'):
    for mm in re.finditer(pat + r"""=['"]([A-Za-z0-9_]+)['"]""", script):
        used.add(mm.group(1))
print('\nused keys: %d' % len(used))

print('\n== USED KEYS ABSENT IN >=1 DICT ==')
missing = []
for k in sorted(used):
    absent = [l for l in LANGS if k not in dicts.get(l, set())]
    if absent:
        missing.append('%s  missing in: %s' % (k, ','.join(absent)))
print('\n'.join(missing) if missing else '  (none)')

allk = set()
for v in dicts.values(): allk |= v
print('\n== DICT PARITY GAPS (key in <3 dicts) ==')
gaps = []
for k in sorted(allk):
    have = [l for l in LANGS if k in dicts.get(l, set())]
    if len(have) < 3:
        gaps.append('%s  only in: %s' % (k, ','.join(have)))
print('\n'.join(gaps) if gaps else '  (none)')
