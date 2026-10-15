
import os
from urllib.parse import urlparse

import requests
import streamlit as st


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="RepoSathi | Open Source Companion",
    page_icon="🤝",
    layout="wide",
)

GITHUB_API = "https://api.github.com"
BACKEND_URL = os.getenv("REPOSATHI_BACKEND_URL", "").rstrip("/")

# ---------------- SESSION STATE ----------------

defaults = {
    "repo_data": None,
    "repo_issues": [],
    "ai_messages": [],
    "ai_error": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- CUSTOM STYLING ----------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #312e81);
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero p {
        color: #dbeafe;
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        padding: 16px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- HEADER ----------------

st.markdown(
    """
    <div class="hero">
        <h1>🤝 RepoSathi</h1>
        <p>Your friendly companion for open-source contributions.</p>
        <p>
            Explore repositories, discover contribution opportunities,
            and get guidance on your open-source journey.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("EXPLORE  ·  CONTRIBUTE  ·  LEARN")


# ---------------- GITHUB HELPERS ----------------

def parse_github_url(url):
    """Validate a public GitHub repository URL."""
    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Enter a URL starting with https://")

    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise ValueError("Please enter a github.com repository URL.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(parts) != 2:
        raise ValueError(
            "Use a URL like https://github.com/streamlit/streamlit"
        )

    owner, repo = parts
    repo = repo.removesuffix(".git")

    if not owner or not repo:
        raise ValueError("Repository owner or name is missing.")

    return owner, repo


def get_github_data(owner, repo):
    """Fetch public repository details and open issues."""
    headers = {"Accept": "application/vnd.github+json"}

    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}",
        headers=headers,
        timeout=15,
    )

    if response.status_code == 404:
        raise ValueError("Repository not found or not publicly accessible.")

    if response.status_code == 403:
        raise ValueError("GitHub API rate limit reached. Try again later.")

    response.raise_for_status()
    repo_data = response.json()

    issues_response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/issues",
        params={"state": "open", "per_page": 30},
        headers=headers,
        timeout=15,
    )
    issues_response.raise_for_status()

    # Exclude pull requests returned by GitHub's issues endpoint.
    issues = [
        issue
        for issue in issues_response.json()
        if "pull_request" not in issue
    ]

    return repo_data, issues


# ---------------- REPOSITORY EXPLORER ----------------

st.subheader("🔎 Explore a Repository")
st.write(
    "Enter a public GitHub repository to explore its details "
    "and contribution opportunities."
)

with st.form("repository_form"):
    repo_url = st.text_input(
        "GitHub repository URL",
        placeholder="https://github.com/streamlit/streamlit",
    )

    explore_clicked = st.form_submit_button(
        "Explore Repository",
        type="primary",
        use_container_width=True,
    )

if explore_clicked:
    st.session_state.repo_data = None
    st.session_state.repo_issues = []
    st.session_state.ai_messages = []
    st.session_state.ai_error = ""

    try:
        owner, repo = parse_github_url(repo_url)

        with st.spinner("Fetching repository details..."):
            data, issues = get_github_data(owner, repo)

        st.session_state.repo_data = data
        st.session_state.repo_issues = issues
        st.success("Repository loaded successfully!")

    except ValueError as error:
        st.error(str(error))

    except requests.exceptions.Timeout:
        st.error("GitHub took too long to respond. Please try again.")

    except requests.exceptions.RequestException:
        st.error(
            "Unable to connect to GitHub. Check your internet "
            "connection and try again."
        )


# ---------------- REPOSITORY DASHBOARD ----------------

repo_data = st.session_state.repo_data
issues = st.session_state.repo_issues

if repo_data:
    st.divider()
    st.title(f"📦 {repo_data['full_name']}")

    st.write(
        repo_data.get("description")
        or "No repository description is available."
    )

    st.link_button(
        "View Repository on GitHub ↗",
        repo_data["html_url"],
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "⭐ Stars",
        f"{repo_data.get('stargazers_count', 0):,}",
    )
    c2.metric(
        "🍴 Forks",
        f"{repo_data.get('forks_count', 0):,}",
    )
    c3.metric(
        "🐛 Open Issues",
        f"{repo_data.get('open_issues_count', 0):,}",
    )
    c4.metric(
        "💻 Language",
        repo_data.get("language") or "Not specified",
    )

    st.caption(
        "Repository owner: "
        + repo_data.get("owner", {}).get("login", "Unknown")
    )

    # ---------------- ISSUE FINDER ----------------

    st.divider()
    st.header("🎯 Contribution Opportunities")

    st.write(
        "Search open issues and filter for issues labelled "
        "as beginner-friendly."
    )

    beginner_labels = {
        "good first issue",
        "beginner",
        "easy",
        "help wanted",
    }

    search_text = st.text_input(
        "🔎 Search issues by title",
        placeholder="e.g. documentation, bug, Python",
        key="issue_search",
    )

    issue_filter = st.selectbox(
        "Filter contribution opportunities",
        [
            "All open issues",
            "Beginner-friendly issues",
        ],
        key="issue_filter",
    )

    filtered_issues = []

    for issue in issues:
        labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
        ]

        is_beginner = any(
            label.lower() in beginner_labels
            for label in labels
        )

        matches_search = (
            search_text.strip().lower()
            in issue.get("title", "").lower()
        )

        matches_filter = (
            issue_filter == "All open issues" or is_beginner
        )

        if matches_search and matches_filter:
            filtered_issues.append(issue)

    st.caption(
        f"Showing {len(filtered_issues)} of {len(issues)} open issues"
    )

    if not filtered_issues:
        st.info(
            "No issues match your search. Try another keyword "
            "or select All open issues."
        )

    for issue in filtered_issues:
        labels = [
            label.get("name", "")
            for label in issue.get("labels", [])
        ]

        is_beginner = any(
            label.lower() in beginner_labels
            for label in labels
        )

        with st.container(border=True):
            st.markdown(
                f"**#{issue['number']} — {issue['title']}**"
            )

            if is_beginner:
                st.success("Potential beginner-friendly issue")

            body = issue.get("body") or "No description provided."

            st.write(
                body[:700] + ("..." if len(body) > 700 else "")
            )

            if labels:
                st.caption("Labels: " + " · ".join(labels))
            else:
                st.caption("Labels: None")

            st.link_button(
                "View Issue ↗",
                issue["html_url"],
                key=f"issue_{issue['number']}",
            )

    st.caption(
        "Label matching is only a hint. Read the discussion, "
        "contribution guidelines, and project requirements first."
    )


# ---------------- AI BACKEND ADAPTER ----------------

def ask_backend(question, repository, history):
    """
    Example API contract. Confirm the endpoint and JSON fields
    with your teammate before enabling backend integration.
    """
    response = requests.post(
        f"{BACKEND_URL}/api/ask",
        json={
            "question": question,
            "repository": (
                {
                    "full_name": repository.get("full_name"),
                    "description": repository.get("description"),
                    "url": repository.get("html_url"),
                }
                if repository
                else None
            ),
            "history": history,
        },
        timeout=90,
    )

    response.raise_for_status()
    result = response.json()

    if not isinstance(result.get("answer"), str):
        raise ValueError(
            "Backend response must contain an 'answer' string. "
            "Confirm the API contract with your teammate."
        )

    return result["answer"]


def get_demo_answer(question, repository):
    """Sample guidance only; this is not a real AI response."""
    if repository:
        return (
            f"You're exploring **{repository['full_name']}**.\n\n"
            "1. Read the README and contribution guidelines.\n"
            "2. Search for a suitable open issue.\n"
            "3. Read the issue discussion and understand the expected change.\n"
            "4. Fork the repository, create a branch, and test your change.\n"
            "5. Open a pull request using the project's instructions.\n\n"
            "**Demo mode:** This is sample guidance, not an AI-generated "
            "analysis of the repository."
        )

    return (
        "Here are some starting steps:\n\n"
        "1. Choose a project that interests you.\n"
        "2. Read its README and contribution guidelines.\n"
        "3. Search for issues labelled `good first issue`.\n"
        "4. Understand the problem before editing code.\n\n"
        "**Demo mode:** Connect the backend to enable real AI answers."
    )


# ---------------- AI ASSISTANT ----------------

st.divider()
st.header("🤖 Ask RepoSathi")

st.write(
    "Ask questions about open source, contribution steps, "
    "or the repository you're exploring."
)

if not repo_data:
    st.info(
        "You can ask general questions now. Explore a repository "
        "first to include its details in your question."
    )

# Display previous conversation messages.
for message in st.session_state.ai_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("demo"):
            st.caption("DEMO MODE · Sample guidance, not a real AI answer.")

# A chat input allows follow-up questions.
question = st.chat_input(
    "Ask RepoSathi a question...",
    key="chat_question",
)

if question:
    question = question.strip()

    if question:
        st.session_state.ai_messages.append(
            {"role": "user", "content": question}
        )

        # Pass earlier conversation to the backend if supported.
        history = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in st.session_state.ai_messages[:-1]
        ]

        try:
            with st.spinner("🤖 RepoSathi is thinking..."):
                if BACKEND_URL:
                    answer = ask_backend(
                        question,
                        repo_data,
                        history,
                    )
                    is_demo = False
                else:
                    answer = get_demo_answer(question, repo_data)
                    is_demo = True

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "demo": is_demo,
                }
            )

            st.rerun()

        except requests.exceptions.Timeout:
            st.session_state.ai_error = (
                "The backend took too long to respond. Please try again."
            )

        except requests.exceptions.ConnectionError:
            st.session_state.ai_error = (
                "Could not connect to the backend. Check its URL "
                "and make sure the backend server is running."
            )

        except requests.exceptions.RequestException as error:
            st.session_state.ai_error = f"Backend request failed: {error}"

        except ValueError as error:
            st.session_state.ai_error = str(error)

if st.session_state.ai_error:
    st.error(st.session_state.ai_error)
    st.session_state.ai_error = ""

if st.session_state.ai_messages:
    if st.button("Clear conversation"):
        st.session_state.ai_messages = []
        st.rerun()


# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "🤝 RepoSathi · Making open source easier to approach, "
    "one contribution at a time."
)