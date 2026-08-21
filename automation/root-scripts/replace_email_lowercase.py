import os

folder = r'd:\Aamir\JRAI\public_html'
extensions = ['.html', '.php', '.js']

old_email = 'Hire@Jobrecruitment.in'
new_email = 'hire@jobrecruitment.in'

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    content = content.replace(old_email, new_email)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(folder):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    for f in files:
        if any(f.endswith(e) for e in extensions):
            replace_in_file(os.path.join(root, f))

print("Done making email lowercase.")
