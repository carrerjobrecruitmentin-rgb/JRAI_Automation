import os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

bad_chars = ['\u00e2\u20ac', '\u00e2\u201a\u00b9', '\u00c3\u00a9', '\u00c2\u00a9', '\u00e2\u02dc', '\u00e2\u2020']
folder = r'd:\Aamir\JRAI\public_html'
found = False
for root, dirs, files in os.walk(folder):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    for fname in files:
        if fname.endswith(('.html', '.php', '.js', '.css')):
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            hits = [b for b in bad_chars if b in content]
            if hits:
                found = True
                safe_hits = [h.encode('ascii', errors='backslashreplace').decode() for h in hits]
                print('STILL DIRTY:', fname, '->', safe_hits)
if not found:
    print('ALL CLEAN - No more mojibake found in any file!')
