import os
import shutil
from git import Repo


class RepoClone:
    """
    Class for entering a context where repo is cloned and deleteing it when leaving the context.
    """

    def __init__(self, repo_name: str, branch: str = ""):
        """
        Initialize the class with the given repo_name.

        Parameters:
            repo_name (str): The name of the repository.

        Returns:
            None
        """
        self.branch = branch
        self.repo_name = repo_name
        self.path_of_clone: str

    def __enter__(
        self,
    ) -> Repo:
        path = f"./cache/{self.repo_name}"
        if os.path.exists(path):
            repo = Repo(path)
            if self.branch:
                repo.git.checkout(self.branch)
            repo.remotes.origin.pull(self.branch if self.branch else "main")

            return repo
        else:
            repo_url = f"git@localhost:{self.repo_name}"
            self.path_of_clone = f"./cache/{self.repo_name}"
            return Repo.clone_from(
                repo_url,
                self.path_of_clone,
                branch=self.branch if self.branch else None,
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
