import os
from git import Repo


def repo_clone(repo_name: str, branch: str = "") -> Repo:
    """
    Clones repo into cache folder if it doesn't exist and pulls branch if it does
    """
    path = f"./cache/{repo_name}"
    if os.path.exists(path):
        repo = Repo(path)
        if branch:
            repo.git.checkout(branch)
        repo.remotes.origin.pull(branch if branch else "main")
        repo.remotes.origin.fetch()

        return repo
    else:
        repo_url = f"git@localhost:{repo_name}"
        path_of_clone = f"./cache/{repo_name}"
        return Repo.clone_from(
            repo_url,
            path_of_clone,
            branch=branch if branch else None,
        )
