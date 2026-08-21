import re
import os

file_path = r"d:\Aamir\JRAI\public_html\employer-post-job.html"
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. CSS
css = """
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
text = text.replace("</style>", css + "</style>")

# 2. Navigation bar replacing the top buttons
old_top_btns = r'<div class="flex gap-3 flex-shrink-0">[\s\S]*?</div>\s*</div>\s*<form id="job-form".*?>'
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
                    Experience
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
text = re.sub(old_top_btns, nav_html, text)

# 3. Sections replacing
blocks = text.split('<div class="glass-card p-6">')
new_text = blocks[0]

sections = [
    ('Basic Information', 'basic'),
    ('Location', 'loc'),
    ('Salary & Compensation', 'sal'),
    ('Experience & Education', 'exp'),
    ('Job Description & Skills', 'desc'),
    ('Hiring Details & Application', 'hire')
]

for i in range(1, len(blocks)):
    block = blocks[i]
    if i <= 6:
        sec_idx = i - 1
        is_first = (sec_idx == 0)
        is_last = (sec_idx == 5)
        sid = sections[sec_idx][1]
        
        active_cls = " active" if is_first else ""
        header = f'<div class="glass-card p-6 wizard-step{active_cls}" id="sec-{sid}">'
        
        # Determine footer buttons
        prev_btn = f'<button type="button" onclick="wizardPrev({sec_idx})" class="btn-secondary text-sm px-4 py-2"><i data-lucide="arrow-left" class="w-4 h-4"></i> Previous</button>' if sec_idx > 0 else ''
        if is_last:
            next_btn = f'<button type="button" onclick="wizardFinish({sec_idx})" class="btn-primary text-sm shadow-md px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white"><span id="btn-next-text-{sec_idx}">Publish Job</span> <i data-lucide="check-circle" class="w-4 h-4"></i></button>'
        else:
            next_btn = f'<button type="button" onclick="wizardNext({sec_idx})" class="btn-primary text-sm shadow-md px-6 py-2 bg-violet-600 hover:bg-violet-700 text-white"><span id="btn-next-text-{sec_idx}">Save & Continue</span> <i data-lucide="arrow-right" class="w-4 h-4"></i></button>'
        
        footer_html = f'''
                    <div class="step-footer">
                        {prev_btn}
                        {next_btn}
                    </div>
                </div>'''
        
        parts = block.rsplit('</div>', 1)
        # Note: if there is multiple </div>, we just replace the last one before the next section
        block = parts[0] + footer_html + (parts[1] if len(parts) > 1 else "")
        
        new_text += header + block
    else:
        new_text += '<div class="glass-card p-6">' + block

# 4. Remove bottom action bar
bottom_action = r'<!-- Bottom Action Bar - Always Visible -->[\s\S]*?</div>\s*</form>'
new_text = re.sub(bottom_action, '</form>', new_text)

# 5. Inject JS
js_logic = """
    // --- WIZARD LOGIC ---
    const wizardSections = ['basic', 'loc', 'sal', 'exp', 'desc', 'hire'];
    let wizardState = {
        currentStep: 0,
        completed: { 'basic': false, 'loc': false, 'sal': false, 'exp': false, 'desc': false, 'hire': false }
    };

    function renderWizard() {
        wizardSections.forEach((sec, index) => {
            const tab = document.getElementById('tab-btn-' + sec);
            const card = document.getElementById('sec-' + sec);
            if(!tab || !card) return;
            const iconContainer = tab.querySelector('.tab-icon');
            
            tab.className = 'tab-btn px-4 py-2 text-sm font-semibold rounded-xl transition-all whitespace-nowrap';
            card.classList.remove('active');
            
            if (index === wizardState.currentStep) {
                tab.classList.add('current');
                iconContainer.innerHTML = '<i data-lucide="edit-3" class="w-4 h-4"></i>';
                card.classList.add('active');
                
                setTimeout(() => {
                    const firstInput = card.querySelector('input, select, textarea');
                    if(firstInput) firstInput.focus();
                }, 400);

            } else if (wizardState.completed[sec]) {
                tab.classList.add('completed');
                iconContainer.innerHTML = '<i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-500"></i>';
            } else {
                tab.classList.add('locked');
                iconContainer.innerHTML = '<i data-lucide="lock" class="w-4 h-4"></i>';
            }
        });

        const activeTab = document.querySelector('.tab-btn.current');
        if (activeTab) {
            activeTab.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
        lucide.createIcons();
    }

    function wizardNav(index) {
        const targetSec = wizardSections[index];
        if (index === wizardState.currentStep) return;
        if (!wizardState.completed[targetSec] && index > wizardState.currentStep) {
            if(typeof showToast === 'function') showToast('Complete previous section first.', 'error');
            else alert('Complete previous section first.');
            return;
        }
        wizardState.currentStep = index;
        renderWizard();
        window.scrollTo({top: 0, behavior: 'smooth'});
    }

    function wizardPrev(index) {
        if (wizardState.currentStep > 0) {
            wizardState.currentStep--;
            renderWizard();
            window.scrollTo({top: 0, behavior: 'smooth'});
        }
    }

    async function wizardNext(index) {
        const sec = wizardSections[index];
        const card = document.getElementById('sec-' + sec);
        
        const firstInput = card.querySelector('input[required]');
        if(firstInput && firstInput.value.trim() === '') {
            firstInput.classList.add('border-red-500', 'bg-red-50');
            firstInput.focus();
            if(typeof showToast === 'function') showToast('Please fill out the required fields.', 'error');
            setTimeout(() => firstInput.classList.remove('border-red-500', 'bg-red-50'), 3000);
            return;
        }

        wizardState.completed[sec] = true;
        wizardState.currentStep = index + 1;
        
        renderWizard();
        window.scrollTo({top: 0, behavior: 'smooth'});
    }

    async function wizardFinish(index) {
        const sec = wizardSections[index];
        const btnText = document.getElementById('btn-next-text-' + index);
        const origText = btnText.textContent;
        btnText.textContent = "Publishing...";
        const btn = btnText.parentElement;
        btn.disabled = true;
        
        await submitJob();
        
        wizardState.completed[sec] = true;
        renderWizard();
        
        btnText.textContent = origText;
        btn.disabled = false;
    }
    
    // Initialize
    setTimeout(() => {
        renderWizard();
    }, 100);
"""

new_text = new_text.replace("async function submitJob() {", js_logic + "\n    async function submitJob() {")

# Also fix the button query inside submitJob
new_text = new_text.replace("const btn = document.getElementById('save-btn');", "const btn = document.getElementById('btn-next-text-5')?.parentElement || document.createElement('button');")
new_text = new_text.replace("const lbl = document.getElementById('save-lbl');", "const lbl = document.getElementById('btn-next-text-5') || document.createElement('span');")


with open(r"d:\Aamir\JRAI\public_html\employer-post-job.html", "w", encoding="utf-8") as f:
    f.write(new_text)

