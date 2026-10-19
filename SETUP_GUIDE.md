# 🚀 Quick Setup Guide (3 Minutes)

Follow these simple steps to activate your new modern GitHub Profile README:

---

### Step 1: Create your Special Profile Repository on GitHub

1. Go to [github.com/new](https://github.com/new).
2. Set the **Repository name** to exactly:
   ```text
   swastiksahu
   ```
   *(GitHub will show a banner saying: ✨ "You found a secret! swastiksahu/swastiksahu is a special repository that you can use to add a README.md to your GitHub profile."✨)*
3. Ensure the repository is set to **Public**.
4. Check **Add a README file** (or leave it unchecked if pushing from git).
5. Click **Create repository**.

---

### Step 2: Upload / Push the Files

#### Option A: Using Git in Terminal (Fastest)

Run these commands inside this directory (`/Users/swastiksahu/.gemini/antigravity/scratch/github-profile-readme`):

```bash
cd /Users/swastiksahu/.gemini/antigravity/scratch/github-profile-readme
git init
git branch -M main
git add .
git commit -m "feat: modern dark neon profile README and snake animation"
git remote add origin https://github.com/swastiksahu/swastiksahu.git
git push -u origin main
```

*(Note: If you already initialized it with a README on GitHub, you can do `git pull origin main --rebase` before pushing, or force-push `git push -u origin main --force`).*

#### Option B: Via GitHub Web Interface

1. Open your repository `https://github.com/swastiksahu/swastiksahu`.
2. Click **Add file** -> **Upload files** or edit `README.md` directly and paste the contents of `README.md`.
3. To enable the snake animation, ensure `.github/workflows/snake.yml` is also added.

---

### Step 3: Enable Permissions for the Snake Contribution Animation

To allow GitHub Actions to generate and save your contribution snake SVGs:

1. In your `swastiksahu/swastiksahu` repository, click **Settings** (top tab).
2. In the left sidebar, click **Actions** ➔ **General**.
3. Scroll down to **Workflow permissions**.
4. Select **Read and write permissions**.
5. Click **Save**.

---

### Step 4: Run the Snake Action for the First Time

1. Click on the **Actions** tab in your repository.
2. In the left list, click **Generate Snake Contribution Animation**.
3. Click the **Run workflow** dropdown button on the right ➔ click the green **Run workflow** button.
4. Once completed (takes ~20 seconds), your snake animation will automatically display on your profile!

---

### 🎨 Personalizing Links
You can freely customize any links in `README.md`:
- LinkedIn: Replace `https://linkedin.com/in/swastiksahu` with your custom handle if needed.
- Twitter/X: Update `https://twitter.com/` with your handle.
- Featured Projects: Add more repos or highlight ongoing projects anytime.
