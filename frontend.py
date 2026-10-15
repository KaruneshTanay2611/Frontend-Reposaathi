
import os
import requests
import streamlit as st

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
GITHUB_API = "https://api.github.com"

st.set_page_config(
    page_title="RepoSathi | Open Source Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

.stApp {
    background: #f7f8fc;
    color: #19233c;
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: #19233c;
}
.hero {
    padding: 32px;
    border-radius: 22px;
    background: linear-gradient(120deg,#efedff,#eef4ff);
    border: 1px solid #e2e5fa;
    margin-bottom: 25px;
}
.hero-label {
    color: #6958d8;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 800;
}
.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(32px,4vw,48px);
    font-weight: 800;
    line-height: 1.15;
    margin: 14px 0;
}
.gradient {
    background: linear-gradient(90deg,#7555dc,#477ee8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-desc {
    color: #737f98;
    font-size: 15px;
    line-height: 1.8;
    max-width: 650px;
}
.card {
    background: white;
    border: 1px solid #e6e9f2;
    border-radius: 15px;
    padding: 21px;
    margin-bottom: 15px;
}
.card h3 {
    font-size: 19px;
    margin: 8px 0;
}
.muted {
    color: #7c879e;
    font-size: 13px;
    line-height: 1.7;
}
.tag {
    display: inline-block;
    padding: 5px 9px;
    margin: 3px;
    border-radius: 7px;
    background: #f0eeff;
    color: #6655c9;
    font-size: 11px;
}
div.stButton > button {
    border-radius: 10px;
    border: 1px solid #e1e4ef;
    min-height: 42px;
    font-weight: 700;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg,#7056df,#4e7de8);
    color: white;
    border: none;
}
section[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #e8eaf2;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 17px;
    border: 1px solid #e7eaf3;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
defaults = {
    "page": "Home",
    "skills": ["Python", "Git & GitHub"],
    "experience": "Beginner",
    "interests": ["AI / Machine Learning"],
    "availability": "3–5 hours per week",
    "repos": [],
    "issues": [],
    "saved": [],
    "ai_notes": "",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- GITHUB ----------
def search_repositories(skills, interests):
    languages = [
        x for x in skills
        if x in ["Python", "JavaScript", "TypeScript", "Java",
                 "C++", "C", "Go", "Rust"]
    ]

    language = languages[0] if languages else "Python"
    query = f"language:{language} stars:>20"

    if "Documentation" in interests:
        query += " topic:documentation"

    response = requests.get(
        f"{GITHUB_API}/search/repositories",
        params={
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 8,
        },
        headers={"Accept": "application/vnd.github+json"},
        timeout=12,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def get_open_issues(repo):
    owner = repo["owner"]["login"]
    name = repo["name"]

    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{name}/issues",
        params={"state": "open", "per_page": 20, "sort": "updated"},
        headers={"Accept": "application/vnd.github+json"},
        timeout=12,
    )
    response.raise_for_status()

    issues = response.json()
    beginner_issues = []

    for issue in issues:
        if "pull_request" in issue:
            continue

        labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
        ]
        beginner_labels = [
            label.lower() for label in labels
            if "good first issue" in label.lower()
            or "beginner" in label.lower()
            or "help wanted" in label.lower()
        ]

        if beginner_labels:
            beginner_issues.append({
                "title": issue["title"],
                "url": issue["html_url"],
                "repo": repo["full_name"],
                "labels": beginner_labels,
            })

    return beginner_issues[:5]


# ---------- OLLAMA ----------
def ask_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are RepoSathi, an open-source mentor. "
                        "Give beginner-friendly, practical guidance. "
                        "Use only the repository and issue facts provided. "
                        "Never invent URLs, issues, or repository details."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🌱 RepoSathi")
    st.caption("OPEN SOURCE, MADE SIMPLE")
    st.divider()

    pages = [
        "Home",
        "My Skills",
        "Explore Repositories",
        "Beginner Issues",
        "Saved Repositories",
    ]

    for page in pages:
        if st.button(
            page,
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if st.session_state.page == page else "secondary",
        ):
            st.session_state.page = page
            st.rerun()

    st.divider()
    st.caption("YOUR DEVELOPER PROFILE")
    st.write(f"**{st.session_state.experience}** contributor")
    st.caption(", ".join(st.session_state.skills) or "Choose your skills")


# ---------- HERO ----------
st.markdown("""
<div class="hero">
  <div class="hero-label">YOUR OPEN SOURCE JOURNEY STARTS HERE</div>
  <div class="hero-title">
    Your skills.<br>Your first
    <span class="gradient">contribution.</span>
  </div>
  <div class="hero-desc">
    Discover projects that fit your skills, find approachable issues,
    and make your first open-source contribution with confidence.
  </div>
</div>
""", unsafe_allow_html=True)


# ---------- SKILL PROFILE ----------
def skill_form():
    st.subheader("👨‍💻 Tell us about yourself")
    st.write("Your profile helps RepoSathi personalize its suggestions.")

    with st.form("profile_form"):
        skills = st.multiselect(
            "Technologies you know or are learning",
            [
                "Python", "JavaScript", "TypeScript", "Java",
                "C++", "C", "HTML & CSS", "React", "Node.js",
                "Machine Learning", "SQL", "Git & GitHub",
            ],
            default=st.session_state.skills,
        )

        experience = st.radio(
            "Experience level",
            ["Beginner", "Intermediate", "Advanced"],
            horizontal=True,
            index=["Beginner", "Intermediate", "Advanced"].index(
                st.session_state.experience
            ),
        )

        interests = st.multiselect(
            "What interests you?",
            [
                "Web Development", "AI / Machine Learning",
                "Developer Tools", "Mobile Development",
                "Documentation", "Data Science",
                "Cybersecurity", "Open Source Infrastructure",
            ],
            default=st.session_state.interests,
        )

        availability = st.selectbox(
            "Time available",
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

        submitted = st.form_submit_button(
            "Save my profile", type="primary", use_container_width=True
        )

    if submitted:
        st.session_state.skills = skills
        st.session_state.experience = experience
        st.session_state.interests = interests
        st.session_state.availability = availability
        st.success("Profile saved in this session.")
        st.rerun()


# ---------- RECOMMENDATIONS ----------
def find_recommendations():
    if not st.session_state.skills:
        st.warning("Select at least one technology in My Skills first.")
        return

    with st.spinner("Finding repositories on GitHub..."):
        try:
            repos = search_repositories(
                st.session_state.skills,
                st.session_state.interests,
            )
            st.session_state.repos = repos
            st.session_state.issues = []

            # Limit issue lookups to avoid excessive API requests.
            for repo in repos[:4]:
                try:
                    st.session_state.issues.extend(get_open_issues(repo))
                except requests.RequestException:
                    continue

            st.session_state.ai_notes = ""
            st.success(f"Found {len(repos)} public repositories.")
        except requests.RequestException as error:
            st.error(
                "GitHub could not be reached. Check your internet connection "
                f"and try again. Details: {error}"
            )


def explain_matches():
    repos = st.session_state.repos[:5]
    if not repos:
        st.warning("Find repositories first.")
        return

    facts = [
        {
            "name": r["full_name"],
            "description": r.get("description"),
            "language": r.get("language"),
            "stars": r.get("stargazers_count"),
            "url": r.get("html_url"),
        }
        for r in repos
    ]

    prompt = f"""
User profile:
Skills: {st.session_state.skills}
Experience: {st.session_state.experience}
Interests: {st.session_state.interests}
Time: {st.session_state.availability}

Verified GitHub repository data:
{facts}

For each repository, explain why it might suit the user, what skills
may be useful, and what the user should inspect before contributing.
Do not claim that a repository or issue is beginner-friendly unless
the supplied facts support that conclusion. Be concise.
"""
    with st.spinner(f"Gemma/Ollama is evaluating the matches ({OLLAMA_MODEL})..."):
        try:
            st.session_state.ai_notes = ask_ollama(prompt)
        except requests.RequestException as error:
            st.error(
                f"Could not contact Ollama. Make sure it is running and "
                f"the model '{OLLAMA_MODEL}' is installed. Details: {error}"
            )
        except (KeyError, ValueError) as error:
            st.error(f"Unexpected Ollama response: {error}")


# ---------- REPOSITORY CARDS ----------
def render_repositories(repos):
    if not repos:
        st.info("No repositories loaded yet. Click Find repositories to begin.")
        return

    for repo in repos:
        full_name = repo.get("full_name", "Unknown repository")
        url = repo.get("html_url", "https://github.com")
        description = repo.get("description") or "No description provided."
        language = repo.get("language") or "Multiple / not specified"
        stars = repo.get("stargazers_count", 0)

        with st.container(border=True):
            left, right = st.columns([5, 1])
            with left:
                st.markdown(f"### 🔀 [{full_name}]({url})")
                st.write(description)
                st.caption(f"💻 {language}  ·  ⭐ {stars:,} stars")
            with right:
                if st.button("🔖 Save", key=f"save_{full_name}"):
                    if full_name not in st.session_state.saved:
                        st.session_state.saved.append(full_name)
                    st.toast("Repository saved!")
            st.link_button(
                "View repository on GitHub ↗",
                url,
                use_container_width=False,
            )


# ---------- PAGE CONTENT ----------
page = st.session_state.page

if page == "Home":
    a, b, c = st.columns(3)
    a.metric("Repositories found", len(st.session_state.repos))
    b.metric("Issues discovered", len(st.session_state.issues))
    c.metric("Saved projects", len(st.session_state.saved))

    st.subheader("✨ Your next contribution starts here")
    st.write(
        "Build your profile, discover public repositories, and ask your "
        "local AI model to explain which projects may suit your current skills."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍💻 Set up my skills", type="primary",
                     use_container_width=True):
            st.session_state.page = "My Skills"
            st.rerun()
    with col2:
        if st.button("🔎 Find repositories", use_container_width=True):
            find_recommendations()

    if st.session_state.repos:
        st.subheader("Recommended places to explore")
        render_repositories(st.session_state.repos[:4])

        if st.button("✨ Explain my matches with Ollama", type="primary"):
            explain_matches()

        if st.session_state.ai_notes:
            st.subheader("🤖 RepoSathi AI insights")
            st.markdown(st.session_state.ai_notes)

elif page == "My Skills":
    skill_form()

elif page == "Explore Repositories":
    st.subheader("🔎 Explore public repositories")
    st.write("Search results use your selected programming language.")
    if st.button("Find repositories", type="primary"):
        find_recommendations()
    render_repositories(st.session_state.repos)

    if st.session_state.repos and st.button("✨ Explain matches with Ollama"):
        explain_matches()
    if st.session_state.ai_notes:
        st.subheader("🤖 AI explanations")
        st.markdown(st.session_state.ai_notes)

elif page == "Beginner Issues":
    st.subheader("🪄 Issues worth investigating")
    st.caption(
        "These are open issues with beginner-related labels. "
        "Always verify the issue status and contribution instructions."
    )
    if not st.session_state.repos and st.button(
        "Find repositories and issues", type="primary"
    ):
        find_recommendations()

    if not st.session_state.issues:
        st.info("Find repositories first to look for related open issues.")
    for issue in st.session_state.issues:
        with st.container(border=True):
            st.markdown(f"**[{issue['title']}]({issue['url']})**")
            st.caption(
                f"{issue['repo']} · {', '.join(issue['labels'])}"
            )
            st.link_button("Check issue on GitHub ↗", issue["url"])

elif page == "Saved Repositories":
    st.subheader("🔖 Saved repositories")
    saved_repos = [
        r for r in st.session_state.repos
        if r.get("full_name") in st.session_state.saved
    ]
    if saved_repos:
        render_repositories(saved_repos)
    else:
        st.info("No saved repositories yet. Save one from Explore Repositories.")

st.divider()
st.caption(
    "RepoSathi · AI-assisted open-source discovery · "
    "Verify repository and issue details before contributing."
)