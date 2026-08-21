import subprocess
with open('git_hist.txt', 'w', encoding='utf-8') as f:
    subprocess.run(['git', 'log', '-p', 'php-backend/api/ai/improve_resume.php'], stdout=f, stderr=subprocess.STDOUT, cwd='d:/Aamir/JRAI')
with open('git_hist2.txt', 'w', encoding='utf-8') as f:
    subprocess.run(['git', 'log', '-p', 'gov-job-automation/automation/llm/extractor.py'], stdout=f, stderr=subprocess.STDOUT, cwd='d:/Aamir/JRAI')
