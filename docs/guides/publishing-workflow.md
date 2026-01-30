# GitHub Publishing & Security Workflow

This guide outlines the process for safely publishing your project to GitHub while protecting your personal information (PII) and private notes.

---

## 🛡️ The "Safe-to-Publish" Philosophy

We use a **"Deny by Default"** strategy.

1. **Ignore Everything Personal**: The `.gitignore` file is configured to exclude your `journals/`, `whiteboards/`, and `assets/` by default.
2. **Scan Before Commit**: We run a custom security scanner to check for accidental leaks (emails, phone numbers, passwords).
3. **Manual Whitelist**: You explicitly choose which files to share.

---

## 🛠️ Setup (Do This Once)

### 1. Initialize Git

If you haven't already initialized the repository:

```bash
git init
```

### 2. Review `.gitignore`

Check the `.gitignore` file in the root directory. It is pre-configured to block:

* `journals/` (Personal daily logs)
* `whiteboards/` (Brainstorming)
* `assets/` (Images that might be personal)
* `secrets.json` / `.env` (Credentials)

---

## 🔄 The Publishing Workflow

### Step 1: Run the Security Scanner

Before adding any new files, run the scanner script to check for PII.

```bash
# Run from the root directory
python3 scripts/security_scan.py --dir .
```

**Review the Output:**

* **✅ No PII detected**: You are generally safe to proceed (still do a quick visual check).
* **⚠️ Issues Found**: Open the flagged files. If they contain real PII, remove it or add the file to `.gitignore`.

### Step 2: Stage Your Files

Add the project code and documentation.

```bash
# Add code and docs
git add scripts/
git add *.md
git add .gitignore
git add requirements.txt

# OPTIONAL: Add specific "safe" notes from pages/
# Only add notes you have reviewed!
git add pages/My_Public_Project_Note.md
```

### Step 3: Check Status

See what is about to be committed.

```bash
git status
```

*Make sure no `journals/` or unexpected files are listed in green.*

### Step 4: Commit and Push

```bash
git commit -m "feat: Update project documentation and scripts"
git branch -M main
# git remote add origin <your-github-repo-url>
# git push -u origin main
```

---

## 🚨 Emergency: "I committed something private!"

If you accidentally commit a file with PII:

1. **Remove it from git (but keep local file):**

    ```bash
    git rm --cached path/to/private_file.md
    ```

2. **Add to .gitignore:**
    Add the filename to `.gitignore`.
3. **Commit the removal:**

    ```bash
    git commit -m "fix: remove accidental private file"
    ```

4. **If you already pushed to GitHub:**
    You will need to rewrite history (BFG Repo-Cleaner) or delete the repo and start over if it's a new project. **Changing the latest commit is not enough if the file is in the history.**

---

## 📝 Checklist for New Files

* [ ] Does this file contain my phone number or address?
* [ ] Does this file contain names of family/friends?
* [ ] Does this file contain passwords or API keys?
* [ ] Have I run `python3 scripts/security_scan.py`?
