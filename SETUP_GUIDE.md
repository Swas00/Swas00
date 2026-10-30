# 🚀 Complete Deployment Guide for Swastik's Enhanced Profile (@Swas00)

Your profile is now powered by the full **Kaushik-inspired Data Visualization & Showcase Architecture**, customized for your data and projects.

---

### 🌟 What this brings to your GitHub Profile:

1. **Aurora Header Banner (`assets/header.svg`)**:
   - Drifting live aurora background mesh
   - Real-time weekly contribution totals wave
   - Rotating roles: *"Full-stack software developer"*, *"Exploring GenAI, LLMs & LangChain"*, *"MCA student & passionate builder"*
   - Live glass status chips showing: `STATUS: Online`, `LAST PUSH: <repo>`, `STREAK: <n> days`
2. **Retro 16-Bit RPG Character Sheet (`assets/rpg_sheet.svg`)**:
   - Procedural 16-bit JRPG status screen: animated idle breathing pixel hero, HP (Streak Vitality), MP (Commit Velocity), EXP to next level, Core Attributes (STR, INT, AGI, VIT, CHA, LUK), equipped stack weapons, and live active questline
3. **Operator Dossier (`assets/dossier.svg`)**:
   - Halftone portrait rendered directly from your GitHub profile picture (`Swas00.png`)
   - Real-time statistics: Public Repos, Stars, Followers, Streak, Commit Count, and Language Mix
4. **Live Vitals (`assets/vitals.svg`)**:
   - 3 live gauges: Streak & consistency rings, 24-hour push clock (shows what time of day you ship code), and 26-week momentum comparison
5. **Contribution Skyline (`assets/skyline.svg`)**:
   - 3D procedural isometric city: 1 building per day, height = commits, lit windows for active days, beacon marking your peak commit day
6. **Repo Neural Map (`assets/neural.svg`)**:
   - Every one of your repositories is a neuron clustered by language and wired to repos with shared topics/dependencies, with pulse rings on active repos
7. **Contribution Galaxy (`assets/galaxy.svg`)**:
   - 365 days of contributions mapped as an astronomical spiral galaxy (core is today)
   - Interactive visitor star guestbook (visitors can submit an issue to add their orbiting star!)
8. **Active Ops Flight Recorder (`assets/ops.svg` & Table)**:
   - 2-week push histogram per repository
   - Markdown mission-brief table auto-updated by `explorer.py` with your latest public repos (`portfolio`, `letscollab`, `Spend_Wise`, `LIFE-RPG`, etc.)
9. **Interactive Transmission CTF (`assets/div-ctf.svg`)**:
   - 3-stage CTF challenge hidden in your profile with automated proof verification and Hall of Fame
10. **Arsenal**:
    - Curated skill icons (`skillicons.dev`) and custom badges matching your royal/dark palette
11. **Full Automation (`.github/workflows/showcase.yml`)**:
    - Runs every 6 hours and on **every push to `main`**
    - Uses `GITHUB_TOKEN` to recalculate all stats, re-render all SVGs directly into `assets/`, update the `README.md` table, and commit automatically!

---

### 🚀 How to Push to GitHub in 1 Step

All 16 SVGs are compiled and ready in this repository. Push them to your GitHub profile repository (`Swas00/Swas00`):

```bash
cd /Users/swastiksahu/Downloads/Swas00-main
git init
git branch -M main
git remote add origin https://github.com/Swas00/Swas00.git
git add .
git commit -m "feat: complete showcase profile with 16-bit RPG character sheet"
git push -u origin main --force
```

---

### ⚙️ Ensure GitHub Actions Permissions (One-Time Setup)

To allow GitHub Actions to run the automatic 6-hour and on-push re-renders:

1. Open your repository: 👉 **[https://github.com/Swas00/Swas00](https://github.com/Swas00/Swas00)**
2. Click **Settings** (top tab) ➔ **Actions** (left sidebar) ➔ **General**.
3. Under **Workflow permissions**, select **"Read and write permissions"**.
4. Check the box **"Allow GitHub Actions to create and approve pull requests"**.
5. Click **Save**.

---

### 🔄 How to Force an On-Demand Update Anytime

Whenever you push code to any repo and want your profile to refresh immediately:
1. Go to **[https://github.com/Swas00/Swas00/actions](https://github.com/Swas00/Swas00/actions)**.
2. Click **Update showcase (dossier, galaxy, radar)**.
3. Click **Run workflow** ➔ **Run workflow**.
4. In ~45 seconds, all SVGs and your repository table will update to the latest state.
