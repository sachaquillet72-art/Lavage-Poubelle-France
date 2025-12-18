# How to push this project to GitHub (Quick guide)

If you don't know Git, follow these steps in PowerShell. Install Git first if needed: https://git-scm.com/download/win and restart your terminal.

Option A — Run the helper script (recommended):
1. Open PowerShell in this folder.
2. Run: ```./prepare_and_push.ps1```  (you may need to run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once to allow the script)
3. Enter your GitHub repo URL when prompted (HTTPS), and credentials when asked.

Option B — Manual commands (copy-paste):
```powershell
cd "C:\Users\sacha\Downloads\Python Poubelle\analyse-villes"
# configure once
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
# initialize and push
git init
git branch -M main
git remote add origin https://github.com/your-username/your-repo.git
git add fetch_insee.py cities_insee.csv app.py requirements.txt README.md
git commit -m "Add INSEE dataset and cloud-ready updates"
git push -u origin main
```

Notes:
- GitHub may require a Personal Access Token (PAT) instead of password for HTTPS pushes. Create one here: https://github.com/settings/tokens (give `repo` scope). Use your username and the token when prompted.
- Alternatively, set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

After pushing, return here and say "c'est poussé" so I can verify the build on Streamlit Cloud and help with any fixes.