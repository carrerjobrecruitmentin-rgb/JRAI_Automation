import subprocess
import os

files_to_fix = [
    'public_html/employer-nvite.html',
    'public_html/employer-company.html',
    'public_html/employer-applications.html',
    'public_html/employer-post-job.html',
    'public_html/employer.html'
]

# 1. Restore the files to their original state from Git
subprocess.run(['git', 'checkout'] + files_to_fix, cwd='d:/Aamir/JRAI')

# 2. Apply the CSS overrides safely right before </style>
css_overrides = """
        /* THEME OVERRIDES FROM CANDIDATE PANEL */
        .glass-card { 
            background: #ffffff !important; 
            border: 1px solid #e2e8f0 !important; 
            border-radius: 1rem !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .glass-card:hover {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            border-color: #cbd5e1 !important;
        }
        .text-white { color: #0f172a !important; }
        .text-slate-100 { color: #1e293b !important; }
        .text-slate-200 { color: #334155 !important; }
        .text-slate-300 { color: #475569 !important; }
        .text-slate-400 { color: #64748b !important; }
        .bg-[#030712], .bg-black/40, .bg-black/60 { background: #f8fafc !important; }
        .bg-white/5 { background: #f8fafc !important; }
        .bg-white/10 { background: #f1f5f9 !important; }
        .border-white/10, .border-white/5 { border-color: #e2e8f0 !important; }
        .btn-primary, .btn-primary .text-white, .btn-primary i, .bg-violet-600 { color: #ffffff !important; }
        .bg-emerald-600, .bg-blue-600 { color: #ffffff !important; }
        .bg-blue-600 { background: #2563eb !important; }
        .bg-emerald-600 { background: #059669 !important; }
        .bg-violet-600 { background: #7c3aed !important; }
        .sidebar-logo img { filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
        
        .form-input {
            width: 100% !important;
            background-color: #f8fafc !important; 
            border: 1px solid #e2e8f0 !important; 
            border-radius: 0.75rem !important; 
            padding: 0.75rem 1rem !important; 
            font-size: 0.875rem !important; 
            color: #0f172a !important; 
            outline: none !important;
            transition: all 0.3s !important;
            font-weight: 500 !important;
            backdrop-filter: none !important;
        }
        .form-input::placeholder { color: #94a3b8 !important; }
        .form-input:focus {
            border-color: #8b5cf6 !important; 
            box-shadow: 0 0 0 1px #8b5cf6 !important; 
            background-color: #ffffff !important;
            transform: none !important;
        }
        .label {
            display: block !important;
            font-size: 0.75rem !important; 
            font-weight: 700 !important; 
            color: #64748b !important; 
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important; 
            margin-bottom: 0.5rem !important; 
        }
"""

for file_path in files_to_fix:
    full_path = os.path.join('d:/Aamir/JRAI', file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '/* THEME OVERRIDES FROM CANDIDATE PANEL */' not in content:
            content = content.replace('</style>', css_overrides + '</style>')
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
print("All files restored and safely updated!")
