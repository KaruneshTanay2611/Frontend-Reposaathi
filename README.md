# 🤝 RepoSathi

> **AI-Powered GitHub Repository Understanding & Open-Source Contribution Assistant**  
> Demystifying complex codebases, finding approachable first issues, and empowering developers to make their first open-source contributions with confidence.

---

## 🌟 Key Features

- **🔐 Secure Contributor Authentication:**
  Real authentication with input validation, duplicate rejection, and `bcrypt` password hashing. Stores accounts and user-scoped saved repositories in local SQLite (`reposathi.db`).
- **⚡ Instant Repository Analyzer:**
  Paste any public GitHub repository URL or `owner/repo` slug to instantly inspect repository metadata, tech stack, root files, and license.
- **🏗️ Project Structure & Setup Detection:**
  Automatically identifies build tools, container configs, and dependency files (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Dockerfile`) and renders local setup instructions.
- **🎯 First-Contribution Opportunity Finder:**
  Surfaces live open issues filtered by newcomer labels (`good first issue`, `beginner-friendly`, `help wanted`, `documentation`), complete with search and quick-launch links.
- **🤖 Gemma AI Mentorship:**
  Powered by Google's Gemma model running locally via Ollama (`gemma4:e2b`) or an external backend service. Get contextual architecture breakdowns, setup guides, and first-PR checklists grounded strictly in verified repository facts.
- **👨‍💻 Contributor Skill Matcher:**
  Customize your developer profile (languages, experience level, domain interests, time commitment) to discover tailored open-source projects.
- **🔖 User-Scoped Saved Repositories:**
  Bookmark repositories to track contribution goals; bookmarks persist across sessions in the SQLite database tied to your account.
- **🎨 Deep Orbit Dark Theme:**
  Modern developer aesthetic featuring glassmorphic cards, indigo and violet accents, responsive layouts, and accessible contrast.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Ollama** installed with the Gemma model:
  ```bash
  ollama run gemma4:e2b
  ```

### 2. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/KaruneshTanay2611/Reposathi.git
cd Reposathi
pip install -r requirements.txt
```

### 3. Launch the Application
Start the Streamlit application using either entrypoint:
```bash
# Recommended:
streamlit run frontend.py

# Alternatively:
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💾 Database & Storage

* **Database Engine:** SQLite 3
* **File Location:** `c:\Users\karun\OneDrive\Desktop\Reposathi\reposathi.db` (automatically generated on first run and ignored by `.gitignore`).
* **Tables:**
  * `users`: Stores contributor profiles with `id`, `full_name`, `email` (case-insensitive unique index), and `password_hash` (bcrypt salted).
  * `user_saved_repos`: Stores bookmarked repositories scoped to `user_id` with foreign key cascade deletion.

---

## ⚙️ Environment Variables (Optional)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `OLLAMA_URL` | `http://localhost:11434/api/chat` | Ollama chat API endpoint |
| `OLLAMA_MODEL` | `gemma4:e2b` | Local Gemma model tag |
| `REPOSATHI_BACKEND_URL` | `""` | Optional external backend URL (e.g., `http://localhost:8000`) |
| `GITHUB_TOKEN` | `""` | Personal GitHub token to increase API rate limits |

---

## 📐 Architecture

```
┌────────────────────────────────────────────────────────┐
│               RepoSathi Frontend (Streamlit)           │
│  [Auth Portal: Sign In / Sign Up -> Dashboard Access]  │
└───────────────┬───────────────────┬────────────────────┘
                │                   │
       GitHub REST API      SQLite Database (reposathi.db)
                │                   │
  ┌─────────────┴────────────┐  ┌───┴───────────────────┐
  │ - Repo Metadata & Stats  │  │ - Users Table (bcrypt)│
  │ - File Tree & Setup      │  │ - User-Scoped Bookmarks│
  │ - README & Open Issues   │  └───────────────────────┘
  └──────────────────────────┘
                │
         Gemma AI Model (Ollama / Backend)
```

---

## 📄 License
MIT License. Built for the Open Source Community.
