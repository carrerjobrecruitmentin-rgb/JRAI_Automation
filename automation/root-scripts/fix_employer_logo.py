import os
import re

files = [
    'employer.html',
    'employer-applications.html',
    'employer-company.html',
    'employer-nvite.html',
    'employer-post-job.html'
]

html_target = r'''<div class="sidebar-logo">
        <img src="assets/images/logo_icon.png" alt="Logo" style="width:32px;height:32px;object-fit:contain;flex-shrink:0;">
        <img src="assets/images/logo_wordmark_light.png" alt="JobRecruitmentAI" style="height:22px;max-width:140px;object-fit:contain;">
    </div>'''

html_repl = r'''<div class="sidebar-logo">
        <img class="icon" src="assets/images/logo_icon.png" alt="Logo">
        <img class="wordmark" src="assets/images/logo_wordmark_light.png" alt="JobRecruitmentAI">
    </div>'''

css_target = r'''#sidebar .sidebar-logo img { height: 32px; width: auto; object-fit: contain; }'''

css_repl = r'''#sidebar .sidebar-logo img.icon { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }
        #sidebar .sidebar-logo img.wordmark { height: 22px; width: auto; object-fit: contain; max-width: 140px; }'''

for filename in files:
    filepath = os.path.join('D:\\Aamir\\JRAI\\public_html', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace(html_target, html_repl)
        content = content.replace(css_target, css_repl)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
    else:
        print(f"Missing {filename}")
