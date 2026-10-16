"""
RepoSathi - Main Application Entrypoint
Preserves legacy helper functions and API contracts for backward compatibility
while executing the modern, enhanced Deep Orbit frontend interface.
"""

import os
from urllib.parse import urlparse
import requests

# Import and execute the enhanced frontend
import frontend

# Preserve existing API constants & contract signatures
GITHUB_API = frontend.GITHUB_API
BACKEND_URL = frontend.BACKEND_URL


def parse_github_url(url):
    """Validate a public GitHub repository URL."""
    return frontend.parse_github_url(url)


def get_github_data(owner, repo):
    """Fetch public repository details and open issues."""
    repo_data = frontend.fetch_github_repository(owner, repo)
    issues = frontend.fetch_github_issues(owner, repo)
    return repo_data, issues


def ask_backend(question, repository, history):
    """
    Query the team backend service at REPOSATHI_BACKEND_URL/api/ask.
    Preserves exact existing payload contract.
    """
    return frontend.query_team_backend(question, repository, history)


def get_demo_answer(question, repository):
    """AI guidance using local Gemma / fallback assistant."""
    answer, _ = frontend.ask_ai_assistant(question, repo_data=repository)
    return answer