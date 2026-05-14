import subprocess
import os

# --- SETTINGS ---
# Apni GitHub Repository ka URL yahan paste karein
REPO_URL = "https://github.com/MuhammadRazaAli1/MedicareAI" 
COMMIT_MESSAGE = "Update: Final project with datasets and models"

def run_git_commands():
    try:
        # 1. Git initialize (agar pehle se nahi hai)
        if not os.path.exists(".git"):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", REPO_URL], check=True)
            print("Git initialized and remote added.")

        # 2. Files add karein
        subprocess.run(["git", "add", "."], check=True)
        
        # 3. Commit karein
        subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], check=True)
        
        # 4. Push karein
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
        
        print("\n🚀 Success! Aapka project GitHub par upload ho gaya hai.")
        
    except Exception as e:
        print(f"\n❌ Error aya hai: {e}")

if __name__ == "__main__":
    run_git_commands()