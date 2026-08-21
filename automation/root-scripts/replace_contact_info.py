import os
import re

folder = r'd:\Aamir\JRAI\public_html'
extensions = ['.html', '.php', '.js']

old_phone = '+1 (555) 123-4567'
new_phone = '+91 90998 76985'

old_email = 'support@JobRecruitmentAI.com'
new_email = 'Hire@Jobrecruitment.in'

# Addresses
old_address_1 = '123 AI Boulevard, Tech Park, Silicon Valley, CA 94043'
old_address_2 = '123 AI Boulevard, Tech Park<br>Silicon Valley, CA 94043'
old_address_3 = '123 AI Boulevard, Tech\n                                    Park, Silicon Valley, CA 94043'
new_address = 'Fairdeal house, B-910, Chimanlal Girdharlal Rd, nr. Swastik Cross Road, Shital Kunj Society, Vasant Vihar, Navrangpura, Ahmedabad, Gujarat 380009'

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # Pre-compile the regex for single-pass replacement
    if not hasattr(replace_in_file, 'pattern'):
        replacements = {
            old_phone: new_phone,
            old_email: new_email,
            'support@jobrecruitmentai.com': new_email.lower(),
            old_address_1: new_address,
            old_address_2: new_address,
            old_address_3: new_address,
        }
        replace_in_file.rep_dict = replacements
        replace_in_file.pattern = re.compile('|'.join(map(re.escape, replacements.keys())))
        replace_in_file.regex_pattern = re.compile(r'123 AI Boulevard, Tech\s*Park, Silicon Valley, CA 94043')
        
    content = replace_in_file.pattern.sub(lambda match: replace_in_file.rep_dict[match.group(0)], content)
    content = replace_in_file.regex_pattern.sub(new_address, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(folder):
    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
    for f in files:
        if any(f.endswith(e) for e in extensions):
            replace_in_file(os.path.join(root, f))

print("Done replacing contact info.")
