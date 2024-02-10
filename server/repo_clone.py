import shutil
from git import Repo


class RepoClone:
    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.path_of_clone: str

    def __enter__(self) -> Repo:
        repo_url = f"git@localhost:{self.repo_name}"
        self.path_of_clone = f"./cache/{self.repo_name}"
        return Repo.clone_from(repo_url, self.path_of_clone)

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path_of_clone)
        pass
