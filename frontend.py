"""
RepoSathi - AI-Powered GitHub Repository Understanding & Open-Source Companion
Enhanced Frontend with Deep Orbit Dark Theme, Repository Deep-Dive,
Skill-Based Discovery, and Local Gemma AI Integration.
"""

import base64
import os
import re
from urllib.parse import urlparse

import requests
import streamlit as st

# ==============================================================================
# 1. APPLICATION CONFIGURATION & CONSTANTS
# ==============================================================================

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

# Local Gemma via Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_TAGS_URL = os.getenv("OLLAMA_TAGS_URL", "http://localhost:11434/api/tags")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")

# Optional External Backend Service (if running alongside)
BACKEND_URL = os.getenv("REPOSATHI_BACKEND_URL", "").rstrip("/")

# Common beginner labels for issue discovery
BEGINNER_LABELS = {
    "good first issue",
    "good-first-issue",
    "beginner",
    "beginner-friendly",
    "easy",
    "first-timers-only",
    "help wanted",
    "help-wanted",
    "low hanging fruit",
    "documentation",
}

# Key setup configuration files to detect
SETUP_SIGNATURES = {
    "Python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "environment.yml"],
    "Node / JavaScript": ["package.json", "pnpm-lock.yaml", "yarn.lock"],
    "Rust": ["Cargo.toml"],
    "Go": ["go.mod"],
    "Java / Kotlin": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "Containers": ["Dockerfile", "docker-compose.yml", "compose.yaml"],
    "Documentation": ["README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"],
}

st.set_page_config(
    page_title="RepoSathi | AI Open-Source Companion",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 2. DESIGN SYSTEM & MODERN DARK THEME CSS
# ==============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-main: #0B0F19;
    --bg-card: rgba(22, 31, 54, 0.75);
    --bg-card-hover: rgba(30, 42, 74, 0.85);
    --border-subtle: rgba(99, 102, 241, 0.22);
    --border-accent: rgba(139, 92, 246, 0.45);
    --primary-indigo: #6366F1;
    --primary-violet: #8B5CF6;
    --accent-glow: rgba(99, 102, 241, 0.15);
    --text-primary: #F9FAFB;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --badge-beginner: #10B981;
}

/* Global Font & App Canvas */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg-main) !important;
    color: var(--text-primary);
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

.block-container {
    max-width: 1280px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0E1424 !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

/* Hero Banner */
.hero-container {
    position: relative;
    padding: 36px 32px;
    border-radius: 20px;
    background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.18), transparent 45%),
                radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.15), transparent 50%),
                linear-gradient(135deg, #131A2E 0%, #0E1526 100%);
    border: 1px solid var(--border-subtle);
    box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px var(--accent-glow);
    margin-bottom: 24px;
    overflow: hidden;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #A5B4FC;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    font-size: clamp(28px, 3.5vw, 44px);
    font-weight: 800;
    line-height: 1.15;
    color: #FFFFFF;
    margin: 8px 0 14px 0;
}

.hero-gradient-text {
    background: linear-gradient(135deg, #818CF8 0%, #C084FC 50%, #60A5FA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-desc {
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.7;
    max-width: 720px;
}

/* Feature Cards Grid */
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    transition: all 0.25s ease;
}

.feature-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
}

.feature-icon {
    font-size: 26px;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
}

.feature-desc {
    color: var(--text-secondary);
    font-size: 13px;
    line-height: 1.6;
}

/* Metric Display Overrides */
div[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    transition: border-color 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: var(--border-accent) !important;
}

div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 24px !important;
    font-weight: 800 !important;
}

/* Modern Streamlit Buttons */
div.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    border: 1px solid var(--border-subtle) !important;
    background-color: #19233D !important;
    color: #E2E8F0 !important;
}

div.stButton > button:hover {
    border-color: var(--border-accent) !important;
    background-color: #243054 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.2) !important;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
}

/* Link Button */
div.stLinkButton > a {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background-color: #1A243F !important;
    border: 1px solid var(--border-subtle) !important;
    color: #C7D2FE !important;
    transition: all 0.2s ease !important;
}

div.stLinkButton > a:hover {
    border-color: var(--border-accent) !important;
    color: #FFFFFF !important;
    background-color: #233054 !important;
}

/* Badges & Tags */
.badge-pill {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}

.badge-beginner {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-lang {
    background: rgba(99, 102, 241, 0.15);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.badge-topic {
    background: rgba(148, 163, 184, 0.12);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

/* Status Indicator Dot */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
}

.status-online {
    background: rgba(16, 185, 129, 0.12);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-offline {
    background: rgba(239, 68, 68, 0.12);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: currentColor;
}

/* Chat Message Overrides */
div[data-testid="stChatMessage"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}

/* Card Containers */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 18px;
    transition: border-color 0.2s ease;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"]:hover {
    border-color: var(--border-accent);
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 14px;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 2px solid var(--primary-indigo) !important;
    background: rgba(99, 102, 241, 0.08) !important;
}

/* Code Blocks */
pre {
    background-color: #080C15 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    padding: 14px !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 3. SESSION STATE INITIALIZATION
# ==============================================================================

SESSION_DEFAULTS = {
    "page": "Home",
    "repo_input": "",
    "repo_data": None,
    "repo_readme": None,
    "repo_files": [],
    "repo_issues": [],
    "matched_repos": [],
    "matched_issues": [],
    "saved": [],
    "ai_messages": [],
    "ai_error": "",
    "ai_breakdown": "",
    "skills": ["Python", "Git & GitHub"],
    "experience": "Beginner",
    "interests": ["AI / Machine Learning", "Developer Tools"],
    "availability": "3–5 hours per week",
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==============================================================================
# 4. GITHUB API SERVICES (WITH CACHING)
# ==============================================================================

def get_auth_headers():
    """Build standard GitHub API headers with optional token."""
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def parse_github_url(url: str):
    """
    Parse and validate a GitHub repository URL or slug.
    Accepts:
      - https://github.com/owner/repo
      - http://github.com/owner/repo
      - github.com/owner/repo
      - www.github.com/owner/repo
      - owner/repo
    """
    cleaned = url.strip()
    if not cleaned:
        raise ValueError("Please provide a GitHub repository URL or 'owner/repo' slug.")

    # Strip scheme if present
    if cleaned.startswith("https://"):
        cleaned = cleaned[len("https://"):]
    elif cleaned.startswith("http://"):
        cleaned = cleaned[len("http://"):]

    # Strip domain if present
    if cleaned.startswith("www.github.com/"):
        cleaned = cleaned[len("www.github.com/"):]
    elif cleaned.startswith("github.com/"):
        cleaned = cleaned[len("github.com/"):]

    # Now cleaned should be "owner/repo" or "owner/repo/..."
    parts = [p for p in cleaned.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError("Please enter a valid repository format, e.g. https://github.com/streamlit/streamlit or streamlit/streamlit")

    owner, repo = parts[0], parts[1].removesuffix(".git")
    if not owner or not repo:
        raise ValueError("Invalid repository owner or name.")

    return owner, repo


@st.cache_data(ttl=900, show_spinner=False)
def fetch_github_repository(owner: str, repo: str):
    """Fetch core repository metadata."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}"
    resp = requests.get(url, headers=get_auth_headers(), timeout=12)

    if resp.status_code == 404:
        raise ValueError(f"Repository '{owner}/{repo}' was not found or is private.")
    if resp.status_code == 403:
        raise ValueError("GitHub API rate limit exceeded. Please wait a few minutes or provide GITHUB_TOKEN.")

    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=900, show_spinner=False)
def fetch_github_issues(owner: str, repo: str):
    """Fetch open repository issues, excluding pull requests."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": 40, "sort": "updated"}
    resp = requests.get(url, params=params, headers=get_auth_headers(), timeout=12)

    if resp.status_code != 200:
        return []

    raw_items = resp.json()
    # Exclude pull requests (GitHub issues endpoint returns both issues and PRs)
    clean_issues = [item for item in raw_items if "pull_request" not in item]
    return clean_issues


@st.cache_data(ttl=900, show_spinner=False)
def fetch_github_readme(owner: str, repo: str):
    """Fetch and decode the repository README file."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    resp = requests.get(url, headers=get_auth_headers(), timeout=10)

    if resp.status_code == 200:
        try:
            content_b64 = resp.json().get("content", "")
            return base64.b64decode(content_b64).decode("utf-8", errors="replace")
        except Exception:
            return None
    return None


@st.cache_data(ttl=900, show_spinner=False)
def fetch_github_root_files(owner: str, repo: str):
    """Fetch repository top-level directory items to detect project structure."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents"
    resp = requests.get(url, headers=get_auth_headers(), timeout=10)

    if resp.status_code == 200:
        items = resp.json()
        if isinstance(items, list):
            return [item.get("name", "") for item in items]
    return []


@st.cache_data(ttl=600, show_spinner=False)
def search_github_repositories(skills: list, interests: list):
    """Find public repositories tailored to contributor skills and interests."""
    target_languages = [
        s for s in skills
        if s in ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go", "Rust"]
    ]
    lang = target_languages[0] if target_languages else "Python"
    query = f"language:{lang} stars:>50"

    if "Documentation" in interests:
        query += " topic:documentation"
    elif "AI / Machine Learning" in interests:
        query += " topic:machine-learning"

    resp = requests.get(
        f"{GITHUB_API}/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": 8},
        headers=get_auth_headers(),
        timeout=12,
    )
    if resp.status_code == 200:
        return resp.json().get("items", [])
    return []


def detect_setup_guides(files: list, language: str = ""):
    """Analyze detected files and produce verified setup commands and structure insights."""
    detected = {}
    commands = []

    for category, signatures in SETUP_SIGNATURES.items():
        matched = [f for f in signatures if f in files]
        if matched:
            detected[category] = matched

    # Python Setup
    if any(f in files for f in ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"]):
        commands.append({
            "title": "Python Environment Setup",
            "cmd": "python -m venv .venv\n# On Linux/macOS:\nsource .venv/bin/activate\n# On Windows:\n.venv\\Scripts\\activate\npip install -e .  # or pip install -r requirements.txt"
        })

    # Node Setup
    if "package.json" in files:
        commands.append({
            "title": "Node.js Dependencies Setup",
            "cmd": "npm install\n# or if using pnpm/yarn:\npnpm install\nnpm run test"
        })

    # Rust Setup
    if "Cargo.toml" in files:
        commands.append({
            "title": "Rust Cargo Build",
            "cmd": "cargo check\ncargo test"
        })

    # Go Setup
    if "go.mod" in files:
        commands.append({
            "title": "Go Module Setup",
            "cmd": "go mod download\ngo test ./..."
        })

    # Docker Setup
    if any(f in files for f in ["Dockerfile", "docker-compose.yml", "compose.yaml"]):
        commands.append({
            "title": "Containerized Development",
            "cmd": "docker compose up --build"
        })

    return detected, commands


# ==============================================================================
# 5. BACKEND & GEMMA AI ADAPTER
# ==============================================================================

def check_ollama_status():
    """Verify whether local Ollama is active and if Gemma model is ready."""
    try:
        resp = requests.get(OLLAMA_TAGS_URL, timeout=2)
        if resp.status_code == 200:
            models = [m.get("name") for m in resp.json().get("models", [])]
            return True, models
    except Exception:
        pass
    return False, []


def query_ollama_gemma(prompt: str, repo_context: dict = None, history: list = None):
    """
    Direct inference using local Gemma via Ollama chat endpoint.
    Maintains system grounding to avoid hallucination.
    """
    system_prompt = (
        "You are RepoSathi, an expert AI open-source companion and mentor. "
        "Your mission is to help developers understand codebases, navigate project structure, "
        "and make successful open-source contributions. "
        "Guidelines:\n"
        "1. Give concise, well-structured, practical guidance with clear headings and markdown code blocks.\n"
        "2. Ground your explanations strictly in the verified repository details and facts provided.\n"
        "3. Provide realistic local setup instructions and beginner-friendly advice.\n"
        "4. Never invent nonexistent files, issues, or URLs."
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Include repo context if available
    if repo_context:
        context_str = (
            f"Current Repository Context:\n"
            f"- Full Name: {repo_context.get('full_name')}\n"
            f"- Description: {repo_context.get('description')}\n"
            f"- Primary Language: {repo_context.get('language')}\n"
            f"- Stars: {repo_context.get('stargazers_count')}\n"
            f"- Default Branch: {repo_context.get('default_branch')}\n"
            f"- Key Detected Files: {', '.join(repo_context.get('files', []))}\n"
        )
        messages.append({"role": "system", "content": context_str})

    # Include conversation history (last 6 turns for context budget)
    if history:
        for turn in history[-6:]:
            role = "assistant" if turn["role"] == "assistant" else "user"
            messages.append({"role": role, "content": turn["content"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
        }
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {}).get("content", "").strip()


def query_team_backend(question: str, repo_data: dict = None, history: list = None):
    """
    Invoke team backend API contract at REPOSATHI_BACKEND_URL/api/ask.
    Preserves exact existing payload contract.
    """
    repo_payload = None
    if repo_data:
        repo_payload = {
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "url": repo_data.get("html_url"),
        }

    resp = requests.post(
        f"{BACKEND_URL}/api/ask",
        json={
            "question": question,
            "repository": repo_payload,
            "history": history or [],
        },
        timeout=90,
    )
    resp.raise_for_status()
    res = resp.json()
    if not isinstance(res.get("answer"), str):
        raise ValueError("Backend response did not contain an 'answer' string.")
    return res["answer"]


def ask_ai_assistant(question: str, repo_data: dict = None, repo_files: list = None, history: list = None):
    """
    Master AI dispatch: Routes to external backend if configured,
    or falls back to local Gemma via Ollama, or displays actionable instructions.
    """
    # 1. Team external backend takes priority if configured
    if BACKEND_URL:
        return query_team_backend(question, repo_data, history), f"Backend ({BACKEND_URL})"

    # 2. Local Gemma inference via Ollama
    repo_context = None
    if repo_data:
        repo_context = {
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stargazers_count": repo_data.get("stargazers_count"),
            "default_branch": repo_data.get("default_branch"),
            "files": repo_files or [],
        }

    try:
        answer = query_ollama_gemma(question, repo_context, history)
        return answer, f"Gemma ({OLLAMA_MODEL})"
    except requests.exceptions.ConnectionError:
        return (
            f"Could not connect to local Ollama at `{OLLAMA_URL}`.\n\n"
            f"**To activate Gemma inference:**\n"
            f"1. Make sure Ollama is running (`ollama list`)\n"
            f"2. Pull or run the model: `ollama run {OLLAMA_MODEL}`\n"
            f"3. Or define `REPOSATHI_BACKEND_URL` in your environment.",
            "Disconnected"
        )
    except Exception as e:
        return f"AI request error: {str(e)}", "Error"


# ==============================================================================
# 6. SIDEBAR NAVIGATION & DEVELOPER PROFILE
# ==============================================================================

with st.sidebar:
    # Brand Header
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <div style="font-size: 28px;">🤝</div>
            <div>
                <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">RepoSathi</div>
                <div style="font-size: 11px; color: #818CF8; font-weight: 600; letter-spacing: 1px;">OPEN SOURCE COMPANION</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Backend / AI Status Badge
    ollama_ok, models = check_ollama_status()
    if BACKEND_URL:
        st.markdown(
            f'<div class="status-indicator status-online"><span class="status-dot"></span> Backend API Connected</div>',
            unsafe_allow_html=True,
        )
    elif ollama_ok:
        has_gemma = any(OLLAMA_MODEL in m for m in models)
        if has_gemma:
            st.markdown(
                f'<div class="status-indicator status-online"><span class="status-dot"></span> Gemma Active ({OLLAMA_MODEL})</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="status-indicator status-offline"><span class="status-dot"></span> Ollama Online (Model missing)</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="status-indicator status-offline"><span class="status-dot"></span> AI Offline (Ollama not found)</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    # Navigation Menu
    nav_options = [
        ("Home", "🏠 Home & Launchpad"),
        ("Explore & Analyze", "⚡ Repo Analyzer"),
        ("Contribution Opportunities", "🎯 Issue Finder"),
        ("AI Assistant", "🤖 RepoSathi AI"),
        ("Skill Matcher", "👨‍💻 Skill Matcher"),
        ("Saved Repositories", f"🔖 Saved ({len(st.session_state.saved)})"),
    ]

    for key, label in nav_options:
        is_active = st.session_state.page == key
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_btn_{key}", use_container_width=True, type=btn_type):
            st.session_state.page = key
            st.rerun()

    st.divider()

    # Contributor Profile Quickview
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; letter-spacing: 1px;'>CONTRIBUTOR PROFILE</div>", unsafe_allow_html=True)
    st.markdown(f"**Level:** `{st.session_state.experience}` Contributor")
    st.markdown(f"**Skills:** {', '.join(st.session_state.skills[:3])}{'...' if len(st.session_state.skills) > 3 else ''}")
    st.markdown(f"**Availability:** `{st.session_state.availability}`")

    if st.session_state.repo_data:
        st.divider()
        st.markdown("<div style='font-size: 11px; font-weight: 700; color: #94A3B8; letter-spacing: 1px;'>ACTIVE REPOSITORY</div>", unsafe_allow_html=True)
        r_name = st.session_state.repo_data.get("full_name")
        st.caption(f"📦 **{r_name}**")
        st.caption(f"⭐ {st.session_state.repo_data.get('stargazers_count', 0):,} stars · 🐛 {len(st.session_state.repo_issues)} open issues")


# ==============================================================================
# 7. WORKFLOW HANDLERS
# ==============================================================================

def execute_repo_analysis(repo_input_text: str):
    """Core analysis workflow: Fetches metadata, issues, README, and root files."""
    cleaned = repo_input_text.strip()
    if not cleaned:
        st.warning("Please enter a GitHub repository URL or slug.")
        return False

    with st.spinner("🔍 Connecting to GitHub API and inspecting repository..."):
        try:
            owner, repo = parse_github_url(cleaned)
            repo_meta = fetch_github_repository(owner, repo)
            issues = fetch_github_issues(owner, repo)
            readme = fetch_github_readme(owner, repo)
            files = fetch_github_root_files(owner, repo)

            st.session_state.repo_data = repo_meta
            st.session_state.repo_issues = issues
            st.session_state.repo_readme = readme
            st.session_state.repo_files = files
            st.session_state.repo_input = repo_meta.get("html_url", cleaned)
            st.session_state.ai_breakdown = ""  # Reset prior breakdown
            return True

        except ValueError as err:
            st.error(f"Validation Error: {err}")
            return False
        except requests.exceptions.Timeout:
            st.error("GitHub API timed out. Please try again.")
            return False
        except requests.exceptions.RequestException as err:
            st.error(f"GitHub connection failed: {err}")
            return False


# ==============================================================================
# 8. PAGE: HOME & LAUNCHPAD
# ==============================================================================

if st.session_state.page == "Home":
    # Hero Section
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-pill">⚡ POWERED BY GEMMA & GITHUB API</div>
            <div class="hero-title">
                Demystify Open Source.<br>
                Ship Your First <span class="hero-gradient-text">Pull Request.</span>
            </div>
            <div class="hero-desc">
                RepoSathi analyzes any GitHub repository in seconds — decoding project architectures, 
                detecting setup requirements, surfacing beginner-friendly issues, and providing real-time AI mentorship.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Instant Repository Analyzer Input Bar
    st.markdown("### ⚡ Quick Repository Analyzer")
    st.caption("Paste any public GitHub repository to generate an instant architectural breakdown and find starter tickets.")

    col_in, col_btn = st.columns([4, 1])
    with col_in:
        home_url = st.text_input(
            "GitHub Repository URL or Slug",
            value=st.session_state.repo_input,
            placeholder="e.g. streamlit/streamlit or https://github.com/pallets/flask",
            label_visibility="collapsed",
            key="home_url_input",
        )
    with col_btn:
        home_analyze = st.button("🚀 Analyze Repo", type="primary", use_container_width=True)

    # Preset quick-launch chips
    st.markdown("<div style='margin-top: -6px; margin-bottom: 18px;'>", unsafe_allow_html=True)
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns([1, 1, 1, 2])
    with chip_col1:
        if st.button("✨ streamlit/streamlit", use_container_width=True):
            if execute_repo_analysis("streamlit/streamlit"):
                st.session_state.page = "Explore & Analyze"
                st.rerun()
    with chip_col2:
        if st.button("✨ pallets/flask", use_container_width=True):
            if execute_repo_analysis("pallets/flask"):
                st.session_state.page = "Explore & Analyze"
                st.rerun()
    with chip_col3:
        if st.button("✨ psf/requests", use_container_width=True):
            if execute_repo_analysis("psf/requests"):
                st.session_state.page = "Explore & Analyze"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if home_analyze and home_url:
        if execute_repo_analysis(home_url):
            st.session_state.page = "Explore & Analyze"
            st.rerun()

    # Feature Highlights Grid
    st.write("")
    st.markdown("### 🛠️ Built for Confident Open-Source Contributions")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Deep Architecture Breakdown</div>
                <div class="feature-desc">Decode repository structure, key entry points, and dependencies without reading thousands of lines.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Beginner-Friendly Tickets</div>
                <div class="feature-desc">Filter curated good-first-issue and documentation tickets ready for newcomers to tackle.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Gemma AI Mentorship</div>
                <div class="feature-desc">Ask grounded questions about local setup, pull request conventions, and code architecture.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">👨‍💻</div>
                <div class="feature-title">Skill-Matched Projects</div>
                <div class="feature-desc">Match your exact programming languages, tools, and availability with active open-source projects.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Active Project Stats
    st.write("")
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Repository", st.session_state.repo_data.get("name") if st.session_state.repo_data else "None loaded")
    m2.metric("Saved Projects", len(st.session_state.saved))
    m3.metric("Candidate Issues", len(st.session_state.repo_issues) if st.session_state.repo_issues else 0)
    m4.metric("AI Status", "Gemma 4 Ready" if (ollama_ok or BACKEND_URL) else "Offline Mode")


# ==============================================================================
# 9. PAGE: EXPLORE & ANALYZE (REPOSITORY DEEP-DIVE)
# ==============================================================================

elif st.session_state.page == "Explore & Analyze":
    st.markdown("## ⚡ Repository Deep-Dive Analyzer")
    st.caption("Inspect repository architecture, tech stack files, setup procedures, and live contribution tickets.")

    # Top search bar
    with st.container():
        c_in, c_btn = st.columns([4, 1])
        with c_in:
            search_query = st.text_input(
                "GitHub URL or owner/repo slug",
                value=st.session_state.repo_input,
                placeholder="https://github.com/streamlit/streamlit",
                label_visibility="collapsed",
            )
        with c_btn:
            submit_search = st.button("Inspect Repository", type="primary", use_container_width=True)

        if submit_search and search_query:
            if execute_repo_analysis(search_query):
                st.rerun()

    repo = st.session_state.repo_data
    issues = st.session_state.repo_issues
    readme = st.session_state.repo_readme
    files = st.session_state.repo_files

    if not repo:
        st.info("💡 Enter a public GitHub repository above or select a preset from the Home page to start your analysis.")
    else:
        full_name = repo.get("full_name")
        html_url = repo.get("html_url")
        desc = repo.get("description") or "No description provided by the repository maintainers."
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        open_issues_count = repo.get("open_issues_count", 0)
        language = repo.get("language") or "Multi-language"
        license_name = repo.get("license", {}).get("name") if repo.get("license") else "No license specified"
        default_branch = repo.get("default_branch", "main")
        topics = repo.get("topics", [])

        # Repository Header Banner Card
        st.write("")
        with st.container():
            hdr_left, hdr_right = st.columns([4, 1.2])
            with hdr_left:
                st.markdown(f"### 📦 [{full_name}]({html_url})")
                st.write(desc)

                # Badges row
                badges_html = f'<span class="badge-pill badge-lang">💻 {language}</span>'
                badges_html += f'<span class="badge-pill badge-topic">📄 {license_name}</span>'
                badges_html += f'<span class="badge-pill badge-topic">🌿 branch: {default_branch}</span>'
                for t in topics[:5]:
                    badges_html += f'<span class="badge-pill badge-topic">#{t}</span>'
                st.markdown(badges_html, unsafe_allow_html=True)

            with hdr_right:
                is_saved = full_name in st.session_state.saved
                save_text = "★ Saved" if is_saved else "☆ Save Repo"
                if st.button(save_text, key="save_current_repo_btn", use_container_width=True):
                    if is_saved:
                        st.session_state.saved.remove(full_name)
                        st.toast("Removed from saved repositories.")
                    else:
                        st.session_state.saved.append(full_name)
                        st.toast("Saved to your bookmarks!")
                    st.rerun()

                st.link_button("View on GitHub ↗", html_url, use_container_width=True)

        # Metrics Row
        st.write("")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("⭐ Stargazers", f"{stars:,}")
        col_m2.metric("🍴 Forks", f"{forks:,}")
        col_m3.metric("🐛 Open Issues", f"{open_issues_count:,}")
        col_m4.metric("💻 Primary Stack", language)

        # Tabbed Workspace
        st.write("")
        tab_overview, tab_setup, tab_issues, tab_gemma = st.tabs([
            "📋 Overview & README",
            "🏗️ Project Structure & Setup",
            f"🎯 Issues ({len(issues)})",
            "🤖 Gemma AI Breakdown",
        ])

        # TAB 1: OVERVIEW & README
        with tab_overview:
            st.markdown("#### 📖 Project Overview")
            st.write(f"**Full Repository Name:** `{full_name}`")
            st.write(f"**Owner:** `{repo.get('owner', {}).get('login')}`")
            if repo.get("homepage"):
                st.write(f"**Project Website:** [{repo.get('homepage')}]({repo.get('homepage')})")

            st.write("")
            st.markdown("#### 📄 README Content")
            if readme:
                with st.expander("Expand to view full rendered README.md", expanded=True):
                    # Display sanitized markdown
                    st.markdown(readme[:12000] + ("\n\n*...(README preview truncated for readability)*" if len(readme) > 12000 else ""))
            else:
                st.info("No README file was detected for this repository.")

        # TAB 2: PROJECT STRUCTURE & SETUP
        with tab_setup:
            st.markdown("#### 🏗️ Detected Project Structure")
            st.caption("Inspecting repository root files to determine project type, toolchain, and setup commands.")

            detected_categories, setup_cmds = detect_setup_guides(files, language)

            if files:
                st.write("**Root files detected:**")
                file_pills = " ".join([f"`{f}`" for f in files[:25]])
                st.markdown(file_pills)
            else:
                st.info("Root directory contents could not be retrieved.")

            st.write("")
            st.markdown("#### ⚡ Recommended Local Setup")
            if setup_cmds:
                for guide in setup_cmds:
                    st.markdown(f"**{guide['title']}**")
                    st.code(guide["cmd"], language="bash")
            else:
                st.write("Review the project's README or `CONTRIBUTING.md` for bespoke installation scripts.")

            if "CONTRIBUTING.md" in files:
                st.success("✅ This project has a dedicated `CONTRIBUTING.md` guide in the repository root!")
                st.link_button("Read CONTRIBUTING.md on GitHub ↗", f"{html_url}/blob/{default_branch}/CONTRIBUTING.md")

        # TAB 3: CONTRIBUTION OPPORTUNITIES
        with tab_issues:
            st.markdown("#### 🎯 Open Contribution Opportunities")
            st.caption("Find issues tagged as approachable for newcomers or search by topic.")

            filter_col1, filter_col2 = st.columns([3, 2])
            with filter_col1:
                search_issue_text = st.text_input("🔎 Search issues by title keyword", placeholder="e.g. fix, docs, UI, python", key="issue_search_tab")
            with filter_col2:
                issue_category = st.selectbox(
                    "Filter by ticket type",
                    ["All open issues", "Beginner-friendly only (good first issue, beginner, help wanted)"],
                    key="issue_cat_tab",
                )

            # Filter logic
            filtered_list = []
            for issue in issues:
                labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
                is_beginner = any(
                    any(bl in label for bl in BEGINNER_LABELS)
                    for label in labels
                )

                matches_kw = search_issue_text.strip().lower() in issue.get("title", "").lower()
                matches_cat = (issue_category == "All open issues") or is_beginner

                if matches_kw and matches_cat:
                    filtered_list.append((issue, is_beginner))

            st.caption(f"Displaying {len(filtered_list)} of {len(issues)} retrieved open issues")

            if not filtered_list:
                st.info("No open issues matched your search criteria. Try a broader keyword or switch to 'All open issues'.")

            for issue, is_beginner in filtered_list[:15]:
                with st.container():
                    i_num = issue.get("number")
                    i_title = issue.get("title")
                    i_url = issue.get("html_url")
                    i_body = issue.get("body") or "No description provided."
                    i_labels = [l.get("name", "") for l in issue.get("labels", [])]

                    badge_beginner_html = '<span class="badge-pill badge-beginner">🌱 Good First Issue</span>' if is_beginner else ''
                    st.markdown(f"**#{i_num} — [{i_title}]({i_url})** {badge_beginner_html}", unsafe_allow_html=True)
                    st.write(i_body[:350] + ("..." if len(i_body) > 350 else ""))

                    if i_labels:
                        lbl_html = " ".join([f'<span class="badge-pill badge-topic">{lbl}</span>' for lbl in i_labels[:6]])
                        st.markdown(lbl_html, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns([1.5, 4])
                    with btn_c1:
                        st.link_button("Open Issue on GitHub ↗", i_url, key=f"issue_link_{i_num}")
                    with btn_c2:
                        if st.button("🤖 Ask Gemma how to approach this", key=f"ask_issue_{i_num}"):
                            st.session_state.page = "AI Assistant"
                            st.session_state.ai_messages.append({
                                "role": "user",
                                "content": f"How should I investigate and solve issue #{i_num}: '{i_title}' in {full_name}?\n\nContext:\n{i_body[:400]}"
                            })
                            st.rerun()

        # TAB 4: GEMMA AI ARCHITECTURAL BREAKDOWN
        with tab_gemma:
            st.markdown("#### 🤖 Gemma AI Architectural Breakdown")
            st.caption("Generate an automated architectural synthesis based on verified repository metadata, file tree, and open tickets.")

            if st.button("✨ Generate AI Architectural Breakdown", type="primary", key="btn_gen_breakdown"):
                prompt = (
                    f"Perform a comprehensive architectural breakdown of the GitHub repository '{full_name}'.\n"
                    f"Verified facts:\n"
                    f"- Description: {desc}\n"
                    f"- Language: {language}\n"
                    f"- Key files present: {', '.join(files[:20])}\n"
                    f"- Default branch: {default_branch}\n\n"
                    f"Please provide:\n"
                    f"1. **Core Purpose & Architecture**: What does this project do and how is it structured?\n"
                    f"2. **Key Entry Points**: Based on detected files, where does execution or configuration begin?\n"
                    f"3. **Local Setup & Development**: Recommended steps to run and test locally.\n"
                    f"4. **First PR Strategy**: How a newcomer can approach their first contribution here."
                )

                with st.spinner("🤖 Gemma is analyzing repository structure and files..."):
                    answer, provider = ask_ai_assistant(prompt, repo_data=repo, repo_files=files)
                    st.session_state.ai_breakdown = answer

            if st.session_state.ai_breakdown:
                st.markdown(st.session_state.ai_breakdown)
            else:
                st.info("Click 'Generate AI Architectural Breakdown' above to let Gemma synthesize the codebase.")


# ==============================================================================
# 10. PAGE: CONTRIBUTION OPPORTUNITIES (STANDALONE EXPLORER)
# ==============================================================================

elif st.session_state.page == "Contribution Opportunities":
    st.markdown("## 🎯 Contribution Opportunities Explorer")
    st.caption("Discover starter issues across the active repository or popular open-source software.")

    repo = st.session_state.repo_data
    issues = st.session_state.repo_issues

    if not repo:
        st.info("No active repository loaded. You can load a popular repository below to view its beginner issues:")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Load streamlit/streamlit", use_container_width=True):
                execute_repo_analysis("streamlit/streamlit")
                st.rerun()
        with c2:
            if st.button("Load pallets/flask", use_container_width=True):
                execute_repo_analysis("pallets/flask")
                st.rerun()
        with c3:
            if st.button("Load fastapi/fastapi", use_container_width=True):
                execute_repo_analysis("fastapi/fastapi")
                st.rerun()
    else:
        st.markdown(f"**Showing tickets for:** [{repo.get('full_name')}]({repo.get('html_url')})")

        s_col1, s_col2 = st.columns([3, 2])
        with s_col1:
            issue_kw = st.text_input("Filter issues by keyword", placeholder="e.g. bug, docs, typing", key="standalone_issue_search")
        with s_col2:
            issue_filter = st.radio("Ticket Category", ["Beginner-Friendly Only", "All Open Issues"], horizontal=True)

        matched = []
        for issue in issues:
            labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
            is_beginner = any(any(b in lbl for b in BEGINNER_LABELS) for lbl in labels)
            matches_kw = issue_kw.strip().lower() in issue.get("title", "").lower()
            matches_filter = (issue_filter == "All Open Issues") or is_beginner

            if matches_kw and matches_filter:
                matched.append((issue, is_beginner))

        st.caption(f"Found {len(matched)} tickets")

        if not matched:
            st.info("No matching tickets found for this query.")

        for issue, is_beginner in matched:
            with st.container():
                st.markdown(f"**#{issue['number']} — [{issue['title']}]({issue['html_url']})**")
                if is_beginner:
                    st.markdown('<span class="badge-pill badge-beginner">🌱 Starter Issue</span>', unsafe_allow_html=True)
                body = issue.get("body") or "No description provided."
                st.write(body[:300] + ("..." if len(body) > 300 else ""))

                b_col1, b_col2 = st.columns([1.5, 4])
                with b_col1:
                    st.link_button("View on GitHub ↗", issue["html_url"], key=f"sa_issue_{issue['number']}")
                with b_col2:
                    if st.button("🤖 Get guidance on this issue", key=f"sa_ask_{issue['number']}"):
                        st.session_state.page = "AI Assistant"
                        st.session_state.ai_messages.append({
                            "role": "user",
                            "content": f"How do I solve issue #{issue['number']} in {repo.get('full_name')}?\nTitle: {issue['title']}\nDetails: {body[:350]}"
                        })
                        st.rerun()


# ==============================================================================
# 11. PAGE: AI ASSISTANT (REPOSATHI AI CHAT)
# ==============================================================================

elif st.session_state.page == "AI Assistant":
    st.markdown("## 🤖 RepoSathi AI Assistant")
    st.caption("Ask questions about code architectures, debugging, Git workflows, or your target repository.")

    repo = st.session_state.repo_data
    files = st.session_state.repo_files

    if repo:
        st.markdown(
            f"""
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px; padding: 10px 14px; margin-bottom: 16px;">
                <span style="color: #A5B4FC; font-weight: 700;">Active Context:</span>
                <span style="color: #FFFFFF; font-weight: 600;"> {repo.get('full_name')}</span>
                <span style="color: #94A3B8; font-size: 13px;"> ({repo.get('language') or 'General'})</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("💡 Tip: Load a repository in the 'Repo Analyzer' to give RepoSathi specific context about its code and structure.")

    # Quick prompt suggestion chips
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 6px;'>SUGGESTED QUESTIONS:</div>", unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("🛠️ How do I set up locally?", use_container_width=True):
            st.session_state.ai_messages.append({"role": "user", "content": "How do I set up this repository locally and run the tests?"})
            st.rerun()
    with q2:
        if st.button("📁 Explain folder structure", use_container_width=True):
            st.session_state.ai_messages.append({"role": "user", "content": "Explain the typical directory structure and architecture for this project."})
            st.rerun()
    with q3:
        if st.button("🌱 How to pick first issue?", use_container_width=True):
            st.session_state.ai_messages.append({"role": "user", "content": "What is the best strategy to select and solve my first good-first-issue here?"})
            st.rerun()
    with q4:
        if st.button("🚀 PR checklist template", use_container_width=True):
            st.session_state.ai_messages.append({"role": "user", "content": "Give me a checklist and template for creating a high-quality pull request."})
            st.rerun()

    st.write("")

    # Display conversation history
    for msg in st.session_state.ai_messages:
        role = msg["role"]
        provider = msg.get("provider", "")
        with st.chat_message(role):
            st.markdown(msg["content"])
            if provider:
                st.caption(f"Source: {provider}")

    # Process pending response if user just asked a question via chips or input
    if st.session_state.ai_messages and st.session_state.ai_messages[-1]["role"] == "user":
        latest_user_prompt = st.session_state.ai_messages[-1]["content"]
        with st.chat_message("assistant"):
            with st.spinner("🤖 RepoSathi is analyzing..."):
                prior_history = st.session_state.ai_messages[:-1]
                answer, provider = ask_ai_assistant(
                    latest_user_prompt,
                    repo_data=repo,
                    repo_files=files,
                    history=prior_history,
                )
                st.markdown(answer)
                st.caption(f"Source: {provider}")

                st.session_state.ai_messages.append({
                    "role": "assistant",
                    "content": answer,
                    "provider": provider,
                })

    # Chat Input Box
    user_query = st.chat_input("Ask RepoSathi a question about open source or this repository...")
    if user_query and user_query.strip():
        st.session_state.ai_messages.append({
            "role": "user",
            "content": user_query.strip(),
        })
        st.rerun()

    # Clear Chat History Button
    if st.session_state.ai_messages:
        st.write("")
        if st.button("🗑️ Clear Conversation"):
            st.session_state.ai_messages = []
            st.rerun()


# ==============================================================================
# 12. PAGE: SKILL MATCHER & PROFILE
# ==============================================================================

elif st.session_state.page == "Skill Matcher":
    st.markdown("## 👨‍💻 Contributor Skill Matcher")
    st.caption("Customize your developer profile to discover public repositories tailored to your exact skillset.")

    with st.form("skill_profile_form"):
        form_skills = st.multiselect(
            "Technologies & Languages you know or are learning",
            [
                "Python", "JavaScript", "TypeScript", "Java",
                "C++", "C", "Go", "Rust", "React", "Node.js",
                "Machine Learning", "SQL", "Git & GitHub", "Documentation",
            ],
            default=st.session_state.skills,
        )

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            form_exp = st.radio(
                "Experience Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.experience),
                horizontal=True,
            )
        with col_f2:
            form_avail = st.selectbox(
                "Weekly Availability",
                [
                    "1–2 hours per week",
                    "3–5 hours per week",
                    "5–10 hours per week",
                    "10+ hours per week",
                ],
                index=[
                    "1–2 hours per week",
                    "3–5 hours per week",
                    "5–10 hours per week",
                    "10+ hours per week",
                ].index(st.session_state.availability),
            )

        form_interests = st.multiselect(
            "Domains of Interest",
            [
                "AI / Machine Learning", "Web Development", "Developer Tools",
                "Mobile Development", "Documentation", "Data Science",
                "Cybersecurity", "Open Source Infrastructure",
            ],
            default=st.session_state.interests,
        )

        save_profile = st.form_submit_button("💾 Save Profile & Find Matching Repos", type="primary", use_container_width=True)

    if save_profile:
        st.session_state.skills = form_skills
        st.session_state.experience = form_exp
        st.session_state.interests = form_interests
        st.session_state.availability = form_avail

        with st.spinner("Finding matching open-source repositories on GitHub..."):
            matched = search_github_repositories(form_skills, form_interests)
            st.session_state.matched_repos = matched
            st.success(f"Discovered {len(matched)} matching repositories!")

    # Display Matched Repositories
    repos_to_show = st.session_state.matched_repos
    if repos_to_show:
        st.write("")
        st.markdown(f"### 🌟 Matched Repositories ({len(repos_to_show)})")

        for r in repos_to_show:
            r_name = r.get("full_name")
            r_desc = r.get("description") or "No description provided."
            r_lang = r.get("language") or "Various"
            r_stars = r.get("stargazers_count", 0)
            r_url = r.get("html_url")

            with st.container():
                c_left, c_right = st.columns([4, 1.5])
                with c_left:
                    st.markdown(f"**[{r_name}]({r_url})**")
                    st.write(r_desc)
                    st.markdown(f'<span class="badge-pill badge-lang">💻 {r_lang}</span> <span class="badge-pill badge-topic">⭐ {r_stars:,}</span>', unsafe_allow_html=True)
                with c_right:
                    if st.button("⚡ Inspect in Analyzer", key=f"match_inspect_{r_name}", use_container_width=True):
                        execute_repo_analysis(r_name)
                        st.session_state.page = "Explore & Analyze"
                        st.rerun()

                    is_saved = r_name in st.session_state.saved
                    btn_save_text = "★ Saved" if is_saved else "☆ Bookmark"
                    if st.button(btn_save_text, key=f"match_save_{r_name}", use_container_width=True):
                        if is_saved:
                            st.session_state.saved.remove(r_name)
                        else:
                            st.session_state.saved.append(r_name)
                        st.rerun()


# ==============================================================================
# 13. PAGE: SAVED REPOSITORIES
# ==============================================================================

elif st.session_state.page == "Saved Repositories":
    st.markdown("## 🔖 Saved Repositories")
    st.caption("Your bookmarked repositories for contribution tracking and future deep dives.")

    saved_list = st.session_state.saved

    if not saved_list:
        st.info("You haven't bookmarked any repositories yet. Explore repositories and click 'Save Repo' to build your list.")
    else:
        st.caption(f"You have {len(saved_list)} saved projects.")

        for repo_name in saved_list:
            with st.container():
                col_info, col_act = st.columns([3.5, 1.5])
                with col_info:
                    st.markdown(f"### 📦 [{repo_name}](https://github.com/{repo_name})")
                    st.caption(f"https://github.com/{repo_name}")
                with col_act:
                    if st.button("⚡ Analyze Repo", key=f"saved_analyze_{repo_name}", use_container_width=True):
                        execute_repo_analysis(repo_name)
                        st.session_state.page = "Explore & Analyze"
                        st.rerun()

                    if st.button("🗑️ Remove", key=f"saved_remove_{repo_name}", use_container_width=True):
                        st.session_state.saved.remove(repo_name)
                        st.rerun()


# ==============================================================================
# 14. FOOTER
# ==============================================================================

st.write("")
st.divider()
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; color: #64748B; font-size: 13px;">
        <div>🤝 <strong>RepoSathi</strong> · Open-Source Repository Companion</div>
        <div>Grounding verified repository facts with Gemma AI</div>
    </div>
    """,
    unsafe_allow_html=True,
)