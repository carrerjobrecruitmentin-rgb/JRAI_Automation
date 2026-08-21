import subprocess

def undo_restore():
    try:
        # Restore employer-company.html from HEAD~1, which is what fix_employer.py did
        print("Restoring employer-company.html to its previous state (HEAD~1)...")
        subprocess.check_call("git checkout HEAD~1 public_html/employer-company.html", shell=True)
        print("Done! The file has been restored.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    undo_restore()
