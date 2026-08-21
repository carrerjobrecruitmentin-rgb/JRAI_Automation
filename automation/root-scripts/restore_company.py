import os
import subprocess
import re

def run_git_restore():
    try:
        # Find the commit before the theme changes
        # We look for the commit that added "THEME OVERRIDES FROM CANDIDATE PANEL"
        log_output = subprocess.check_output("git log -p public_html/employer-company.html", shell=True, text=True)
        
        commits = log_output.split('commit ')
        target_commit = None
        
        for commit in commits:
            if not commit.strip():
                continue
            if 'THEME OVERRIDES FROM CANDIDATE PANEL' not in commit:
                # This commit did not add the theme overrides, meaning it is the ORIGINAL version
                target_commit = commit.split('\n')[0].strip()
                break
                
        if target_commit:
            print(f"Restoring public_html/employer-company.html from commit {target_commit}")
            subprocess.check_call(f"git checkout {target_commit} public_html/employer-company.html", shell=True)
            
            # Now we inject the CSS only
            with open('public_html/employer-company.html', 'r', encoding='utf-8') as f:
                content = f.read()
                
            css_injection = """
    <link href="css/public-output.css" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/styles.css">
    <style>
        /* THEME OVERRIDES FROM CANDIDATE PANEL */
        .glass-card { background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 1rem !important; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important; }
        .form-input { background-color: #f8fafc !important; border: 1px solid #e2e8f0 !important; border-radius: 0.75rem !important; padding: 0.75rem 1rem !important; color: #0f172a !important; }
        .form-input:focus { border-color: #8b5cf6 !important; box-shadow: 0 0 0 1px #8b5cf6 !important; background-color: #ffffff !important; }
        .label { font-size: 0.75rem !important; font-weight: 700 !important; color: #64748b !important; text-transform: uppercase !important; margin-bottom: 0.5rem !important; }
        .btn-primary { background: linear-gradient(135deg, #7c3aed, #0997fc) !important; color: #fff !important; }
    </style>
"""
            content = content.replace('</head>', css_injection + '\n</head>')
            
            with open('public_html/employer-company.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Successfully restored original layout and injected new theme colors!")
        else:
            print("Could not find the original commit.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_git_restore()
