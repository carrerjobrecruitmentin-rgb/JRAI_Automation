import re

with open(r'c:\xampp\htdocs\JRAI\public_html\employer-nvite.html', encoding='utf8') as f:
    html = f.read()

s1 = html.find('<div id="step-1"')
s2 = html.find('<div id="step-2"')

s1_content = html[s1:s2]

open_divs = len(re.findall(r'<div', s1_content, re.IGNORECASE))
close_divs = len(re.findall(r'</div', s1_content, re.IGNORECASE))

print(f"Step 1 Open Divs: {open_divs}")
print(f"Step 1 Close Divs: {close_divs}")
