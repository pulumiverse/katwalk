import os
from git import Repo
from git.cmd import Git
from pathlib import Path
from urllib.parse import urlparse, urlunparse

def print_safe_url(url):

    parsed_url = urlparse(url)
    safe_netloc = parsed_url.netloc.split("@")[-1] if "@" in parsed_url.netloc else parsed_url.netloc
    safe_url = urlunparse(parsed_url._replace(netloc=safe_netloc))

    return safe_url

def clone_or_update_repo(git_url, destination, username=None, token=None, branch="main", refresh=False):

    # If authentication is provided, set up the URL with credentials
    if username and token:
        git_url = git_url.replace('https://', f'https://{username}:{token}@')

    # Cleanse repo url secrets for logging
    sanitized_git_url = print_safe_url(git_url)

    # Check if the directory already exists and is not empty
    if Path(destination).is_dir() and any(Path(destination).iterdir()):
        print(f"Model directory {destination} already exists.")
        if refresh:
            print(f"Refreshing model repository {sanitized_git_url} in {destination}...")
            repo = Repo(destination)
            repo.git.pull('origin', branch)

            # Run the git-lfs fetch command
            git_cmd = Git(working_dir=destination)
            git_cmd.execute(['git', 'lfs', 'fetch'])
        else:
            print("Skipping refresh as REFRESH_REPOSITORIES is not set to True.")
        return

    # Clone the repository
    print(f"Cloning model repository {sanitized_git_url} into {destination}...")
    repo = Repo.clone_from(git_url, destination, branch=branch)

    # Run the git-lfs fetch command
    git_cmd = Git(working_dir=destination)
    git_cmd.execute(['git', 'lfs', 'fetch'])

    print(f"Repository {sanitized_git_url} cloned successfully to {destination}")

def main():
    # Read environment variables
    repos = os.getenv("HF_REPOS") or "meta-llama/Llama-2-7b-chat-hf"
    branch = os.getenv("HF_BRANCH", "main")
    username = os.getenv("HF_USER")
    token = os.getenv("HF_TOKEN")
    refresh_repositories = os.getenv("REFRESH_REPOSITORIES", "False").lower() == "true"

    # Check for required environment variables
    if not username or not repos or not token:
        print("Error: Missing required environment variables (HF_USER, HF_REPOS, HF_TOKEN).")
        exit(1)

    # Split the repositories into a list
    repo_list = repos.split(",")

    # Iterate over the repositories and clone or update each one
    for repo in repo_list:
        git_url = f"https://huggingface.co/{repo}"
        destination = f"/models/{repo}/{branch}"
        clone_or_update_repo(git_url, destination, username, token, branch, refresh_repositories)

if __name__ == "__main__":
    main()