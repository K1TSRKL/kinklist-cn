#!/usr/bin/env python3
import re
import os
import json

ROOT = os.path.join(os.path.dirname(__file__), '..', 'kinklist')
PLACEHOLDER_DIR = os.path.join(ROOT, 'placeholder')

# 词表：key 为占位符标签，value 为原始词或词列表
SENSITIVE = {
    'TERM_COCK': ['cock', 'cocks'],
    'TERM_PENIS': ['penis'],
    'TERM_PUSSY': ['pussy', 'pussies'],
    'TERM_CUM': ['cum', 'ejaculat', 'semen'],
    'TERM_DILDO': ['dildo', 'dildos'],
    'TERM_ASS': ['ass', 'asses', 'butt', 'butts'],
    'TERM_SHIT': ['shit', 'scat'],
    'TERM_VAGINA': ['vagina'],
    'TERM_FUCK': ['fuck', 'fucking', 'fucked'],
    'TERM_BREAST': ['breast', 'breasts', 'tit', 'tits'],
}

# Build regex list (word boundaries, case-insensitive)
regex_map = []
for key, words in SENSITIVE.items():
    pattern = r"\\b(?:" + '|'.join(re.escape(w) for w in words) + r")\\b"
    regex_map.append((re.compile(pattern, re.IGNORECASE), '{{' + key + '}}', words))

os.makedirs(PLACEHOLDER_DIR, exist_ok=True)

mapping = {}

def replace_text(text, filename):
    # apply all replacements, recording first-seen original for mapping
    for regex, placeholder, originals in regex_map:
        def repl(m):
            orig = m.group(0)
            mapping.setdefault(placeholder, orig)
            return placeholder
        text = regex.sub(repl, text)
    return text

# Walk target files: top-level txt files and language subfolders
for root, dirs, files in os.walk(ROOT):
    # skip placeholder folder
    if 'placeholder' in root.split(os.sep):
        continue
    rel_root = os.path.relpath(root, ROOT)
    target_root = os.path.join(PLACEHOLDER_DIR, rel_root) if rel_root != '.' else PLACEHOLDER_DIR
    os.makedirs(target_root, exist_ok=True)
    for fname in files:
        if not fname.lower().endswith('.txt'):
            continue
        src_path = os.path.join(root, fname)
        dst_path = os.path.join(target_root, fname)
        with open(src_path, 'r', encoding='utf-8') as f:
            txt = f.read()
        new_txt = replace_text(txt, src_path)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(new_txt)
        print('Wrote', dst_path)

# Write mapping
mapping_path = os.path.join(PLACEHOLDER_DIR, 'mapping.json')
with open(mapping_path, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)
print('Wrote mapping:', mapping_path)
print('Done.')
