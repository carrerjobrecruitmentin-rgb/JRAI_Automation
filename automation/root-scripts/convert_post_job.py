import re
import os

file_path = r"d:\Aamir\JRAI\public_html\employer-post-job.html"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Wizard CSS
css = """
        /* THEME OVERRIDES FROM CANDIDATE PANEL */
        .glass-card { 
            background: #ffffff !important; 
            border: 1px solid #e2e8f0 !important; 
            border-radius: 1rem !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .text-slate-100 { color: #1e293b !important; }
        .text-slate-200 { color: #334155 !important; }
        .text-slate-300 { color: #475569 !important; }
        .text-slate-400 { color: #64748b !important; }
        .bg-[#030712], .bg-black/40, .bg-black/60 { background: #f8fafc !important; }
        
        .btn-primary { background: linear-gradient(135deg, var(--brand-purple), var(--brand-blue)) !important; color: #fff !important; box-shadow: 0 4px 15px rgba(79, 21, 123, 0.3) !important; transition: all 0.3s ease !important; border: none; padding: 0.6rem 1.2rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(9, 151, 252, 0.4) !important; }
        
        .btn-secondary { background: #f1f5f9 !important; color: var(--brand-purple) !important; border: 1.5px dashed #94a3b8 !important; transition: all 0.2s; padding: 0.6rem 1.2rem; border-radius: 0.5rem; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; }
        .btn-secondary:hover { background: #e2e8f0 !important; border-style: solid !important; border-color: var(--brand-purple) !important; transform: translateY(-1px); }
        
        /* Wizard CSS */
        .tab-btn { position: relative; display: flex; align-items: center; gap: 8px; border: 1px solid transparent; }
        .tab-btn.locked { opacity: 0.6; cursor: not-allowed; background: transparent !important; color: #94a3b8 !important; }
        .tab-btn.completed { background: #ecfdf5 !important; color: #059669 !important; font-weight: 600 !important; }
        .tab-btn.current { background: #e0e7ff !important; color: #4338ca !important; font-weight: 700 !important; border: 1px solid #c7d2fe !important; }
        
        .wizard-step { display: none; opacity: 0; transform: translateY(10px); transition: all 0.4s ease; }
        .wizard-step.active { display: block; opacity: 1; transform: translateY(0); }
        
        .step-footer { 
            display: flex; align-items: center; justify-content: flex-end; gap: 12px;
            padding-top: 16px; margin-top: 24px; border-top: 1px solid #e2e8f0;
        }
"""
content = re.sub(r'(\s*\/\* THEME OVERRIDES FROM CANDIDATE PANEL \*\/.*?)(\s*<\/style>)', css + r'\2', content, flags=re.DOTALL)

# 2. Inject Nav Bar and replace top action buttons
top_btn_pattern = r'<div class="flex gap-3 flex-shrink-0">.*?</div>\s*</div>\s*<form id="job-form".*?>'
nav_html = """
                <div class="flex gap-3 flex-shrink-0">
                    <a href="employer.html" class="btn-secondary flex items-center gap-2 px-4 py-2 text-sm">
                        <i data-lucide="x" class="w-4 h-4"></i> Cancel
                    </a>
                </div>
            </div>

            <!-- Wizard Navigation -->
            <div class="flex items-center gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide border-b border-slate-200">
                <button type="button" id="tab-btn-basic" onclick="wizardNav(0)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap current">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="edit-3" class="w-4 h-4"></i></span>
                    Basic Information
                </button>
                <button type="button" id="tab-btn-loc" onclick="wizardNav(1)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap locked">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="lock" class="w-4 h-4"></i></span>
                    Location
                </button>
                <button type="button" id="tab-btn-sal" onclick="wizardNav(2)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap locked">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="lock" class="w-4 h-4"></i></span>
                    Salary
                </button>
                <button type="button" id="tab-btn-exp" onclick="wizardNav(3)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap locked">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="lock" class="w-4 h-4"></i></span>
                    Experience & Education
                </button>
                <button type="button" id="tab-btn-desc" onclick="wizardNav(4)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap locked">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="lock" class="w-4 h-4"></i></span>
                    Description & Skills
                </button>
                <button type="button" id="tab-btn-hire" onclick="wizardNav(5)" class="tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap locked">
                    <span class="tab-icon mr-1 flex items-center justify-center"><i data-lucide="lock" class="w-4 h-4"></i></span>
                    Hiring Details
                </button>
            </div>
            
            <form id="job-form" class="space-y-6" onsubmit="return false;">
"""
content = re.sub(top_btn_pattern, nav_html, content, flags=re.DOTALL)

# 3. Replace Bottom Action Bar
bottom_btn_pattern = r'<!-- Bottom Action Bar - Always Visible -->.*?</div>\s*</form>'
content = re.sub(bottom_btn_pattern, r'</form>', content, flags=re.DOTALL)

# 4. Modify Sections manually
sections = [
    ('Basic Information', 'basic'),
    ('Location', 'loc'),
    ('Salary & Compensation', 'sal'),
    ('Experience & Education', 'exp'),
    ('Job Description & Skills', 'desc'),
    ('Hiring Details & Application', 'hire')
]

for i, (title, sid) in enumerate(sections):
    is_first = (i == 0)
    is_last = (i == len(sections) - 1)
    
    # 4.1 Update class and add ID
    # Look for: <div class="glass-card p-6"> \n <h2 ...>Title</h2>
    pattern = r'(<div class="glass-card p-6">)(\s*<h2[^>]*>' + re.escape(title) + r'</h2>)'
    active_class = " active" if is_first else ""
    rep = f'<div class="glass-card p-6 wizard-step{active_class}" id="sec-{sid}">\\2'
    content = re.sub(pattern, rep, content)
    
    # 4.2 Append Step Footer
    # Since we can't reliably parse where the div ends, we can replace the START of the NEXT section or </form>
    prev_btn = f'<button type="button" onclick="wizardPrev({i})" class="btn-secondary text-sm"><i data-lucide="arrow-left" class="w-4 h-4"></i> Previous</button>' if i > 0 else ''
    next_btn = f'<button type="button" onclick="wizardFinish({i})" class="btn-primary text-sm shadow-md px-6 bg-emerald-600 hover:bg-emerald-700 text-white"><span id="btn-next-text-{i}">Publish Job</span> <i data-lucide="check-circle" class="w-4 h-4"></i></button>' if is_last else f'<button type="button" onclick="wizardNext({i})" class="btn-primary text-sm shadow-md px-6 bg-violet-600 hover:bg-violet-700 text-white"><span id="btn-next-text-{i}">Save & Continue</span> <i data-lucide="arrow-right" class="w-4 h-4"></i></button>'
    
    footer_html = f"""
                    <div class="step-footer">
                        {prev_btn}
                        {next_btn}
                    </div>
                </div>
"""
    
    if is_last:
        content = content.replace('</form>', footer_html + '\n            </form>')
    else:
        next_title = sections[i+1][0]
        # Find the comment marking the next section
        next_comment_regex = r'(</div>\s*)(<!-- ' + re.escape(next_title.split(' ')[0]) + r'.*?-->)'
        
        # Alternatively, find the next `<div class="glass-card p-6 wizard-step`
        # By doing string split:
        parts = content.split(f'<div class="glass-card p-6 wizard-step')
        # This is getting too complicated with regex.

def process_file_manually():
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    out = []
    in_section = False
    section_index = -1
    
    sections = [
        ('Basic Information', 'basic'),
        ('Location', 'loc'),
        ('Salary & Compensation', 'sal'),
        ('Experience & Education', 'exp'),
        ('Job Description & Skills', 'desc'),
        ('Hiring Details & Application', 'hire')
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if '<div class="glass-card p-6">' in line and i+1 < len(lines) and '<h2' in lines[i+1]:
            # Check which section it is
            matched_sec = None
            for idx, (title, sid) in enumerate(sections):
                if title in lines[i+1]:
                    matched_sec = (idx, title, sid)
                    break
            
            if matched_sec:
                idx, title, sid = matched_sec
                active_class = " active" if idx == 0 else ""
                out.append(line.replace('<div class="glass-card p-6">', f'<div class="glass-card p-6 wizard-step{active_class}" id="sec-{sid}">'))
                section_index = idx
                i += 1
                continue
                
        if '<!-- Bottom Action Bar - Always Visible -->' in line:
            # Skip until </form>
            while i < len(lines) and '</form>' not in lines[i]:
                i += 1
            if i < len(lines) and '</form>' in lines[i]:
                # We need to append the footer for the LAST section before </form>
                # The last section's closing div should be just before this comment
                # Actually, let's inject footer whenever we see the closing </div> of a glass-card
                pass
        
        out.append(line)
        i += 1
        
    return "".join(out)

# We will just write a new python script that handles the DOM perfectly using beautifulsoup
