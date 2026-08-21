#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

# Force UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FOLDER = r'd:\Aamir\JRAI\public_html'
EXTENSIONS = ['.html', '.php', '.js', '.css']

# Mojibake -> correct Unicode
# These happen when UTF-8 files are mis-read as Windows-1252/Latin-1
REPLACEMENTS = [
    # ---- Deeply-nested / compound sequences first ----
    # triple-encoded rupee (worst case)
    ('\u00c3\u0192\u00c2\u00a2\u00c3\u201a\u00c2\u00ac\u00c3\u0192\u00e2\u20ac\u0161\u00c3\u201a\u00c2\u00b9', '\u20b9'),

    # ---- Smart quotes ----
    ('\u00e2\u20ac\u009c', '\u201c'),   # left double quote "
    ('\u00e2\u20ac\u009d', '\u201d'),   # right double quote "
    ('\u00e2\u20ac\u0098', '\u2018'),   # left single quote '
    ('\u00e2\u20ac\u2122', '\u2019'),   # right single quote / apostrophe '

    # ---- Dashes & Ellipsis ----
    ('\u00e2\u20ac\u00a6', '\u2026'),   # ellipsis ...
    ('\u00e2\u20ac\u201c', '\u2013'),   # en dash -
    ('\u00e2\u20ac\u201d', '\u2014'),   # em dash --

    # ---- Bullet ----
    ('\u00e2\u20ac\u00a2', '\u2022'),   # bullet point

    # ---- Euro (catch-all after specific sequences above) ----
    ('\u00e2\u20ac', '\u20ac'),         # euro sign

    # ---- Indian Rupee ----
    ('\u00e2\u201a\u00b9', '\u20b9'),   # rupee sign

    # ---- Arrows ----
    ('\u00e2\u2020\u2019', '\u2192'),   # right arrow ->
    ('\u00e2\u2020\u2018', '\u2190'),   # left arrow <-
    ('\u00e2\u2020\u201c', '\u2193'),   # down arrow
    ('\u00e2\u2020\u201d', '\u2194'),   # left-right arrow

    # ---- Stars ----
    ('\u00e2\u02dc\u2026', '\u2605'),   # filled star
    ('\u00e2\u02dc\u2020', '\u2606'),   # empty star

    # ---- Copyright / misc symbols ----
    ('\u00c2\u00a9', '\u00a9'),         # copyright (c)
    ('\u00c2\u00ae', '\u00ae'),         # registered (r)
    ('\u00c2\u00b7', '\u00b7'),         # middle dot
    ('\u00c2\u00bb', '\u00bb'),         # >>
    ('\u00c2\u00ab', '\u00ab'),         # <<
    ('\u00c2\u00a0', '\u00a0'),         # non-breaking space
    ('\u00c2\u00b0', '\u00b0'),         # degree
    ('\u00c2\u00bd', '\u00bd'),         # 1/2
    ('\u00c2\u00bc', '\u00bc'),         # 1/4
    ('\u00c2\u00be', '\u00be'),         # 3/4

    # ---- Accented Latin characters ----
    ('\u00c3\u00a9', '\u00e9'),         # e acute
    ('\u00c3\u00a8', '\u00e8'),         # e grave
    ('\u00c3\u00aa', '\u00ea'),         # e circumflex
    ('\u00c3\u00ab', '\u00eb'),         # e umlaut
    ('\u00c3\u00a0', '\u00e0'),         # a grave
    ('\u00c3\u00a2', '\u00e2'),         # a circumflex
    ('\u00c3\u00a4', '\u00e4'),         # a umlaut
    ('\u00c3\u00bc', '\u00fc'),         # u umlaut
    ('\u00c3\u00b6', '\u00f6'),         # o umlaut
    ('\u00c3\u00bf', '\u00ff'),         # y umlaut
    ('\u00c3\u00ad', '\u00ed'),         # i acute
    ('\u00c3\u00b3', '\u00f3'),         # o acute
    ('\u00c3\u00ba', '\u00fa'),         # u acute
    ('\u00c3\u00b1', '\u00f1'),         # n tilde
]


def collect_files(folder, extensions):
    result = []
    skip_dirs = {'node_modules', '.git', '__pycache__', 'venv'}
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                result.append(os.path.join(root, f))
    return result


def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            original = f.read()
    except Exception as e:
        return 'ERROR_READ', str(e)

    content = original
    changes = []
    
    import re
    if not hasattr(fix_file, 'pattern'):
        fix_file.rep_dict = {bad: good for bad, good in REPLACEMENTS}
        fix_file.pattern = re.compile('|'.join(map(re.escape, fix_file.rep_dict.keys())))
        
    counts = {}
    def replacer(match):
        bad = match.group(0)
        counts[bad] = counts.get(bad, 0) + 1
        return fix_file.rep_dict[bad]
        
    content = fix_file.pattern.sub(replacer, content)
    
    for bad, n in counts.items():
        changes.append((bad, fix_file.rep_dict[bad], n))

    if changes:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return 'FIXED', changes
        except Exception as e:
            return 'ERROR_WRITE', str(e)
    return 'CLEAN', []


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'))


def main():
    safe_print('=' * 65)
    safe_print('MOJIBAKE FIXER - Scanning all project files')
    safe_print('=' * 65)

    files = collect_files(FOLDER, EXTENSIONS)
    safe_print(f'Found {len(files)} files to scan...\n')

    fixed_count = 0
    error_count = 0

    for filepath in sorted(files):
        status, data = fix_file(filepath)
        rel = filepath.replace(FOLDER, '').lstrip('\\/') 

        if status == 'FIXED':
            fixed_count += 1
            safe_print(f'[FIXED]  {rel}')
            for bad, good, n in data:
                # Print ASCII-safe summary
                bad_safe = bad.encode('ascii', errors='backslashreplace').decode('ascii')
                good_safe = good.encode('ascii', errors='backslashreplace').decode('ascii')
                safe_print(f'         {bad_safe!r} -> {good_safe!r} ({n}x)')
        elif status.startswith('ERROR'):
            error_count += 1
            safe_print(f'[ERROR]  {rel}: {data}')
        # CLEAN files: silent

    safe_print('')
    safe_print('=' * 65)
    safe_print(f'DONE: Fixed {fixed_count} file(s). Errors: {error_count}. Clean: {len(files) - fixed_count - error_count}.')
    safe_print('=' * 65)


if __name__ == '__main__':
    main()
