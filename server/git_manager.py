import typing
import git

conf_file_path = "conf/gitolite.conf"


class GitManager:
    def __init__(self, path: str) -> None:
        self.repo = git.Repo(path)
        self.path = path

    def _commit_files(self, commit_message: str, files_to_commit: typing.List[str]):
        self.repo.index.add(files_to_commit)
        self.repo.git.commit(
            "-m",
            commit_message,
        )

        origin = self.repo.remote(name="origin")
        origin.push()

    def add_ssh_key(self, user_name: str, ssh_key: str):
        """
        Adds an SSH key to gitolite for a specific user.

        Parameters:
            user_name (str): The name of the user.
            ssh_key (str): The SSH key to be added.

        Returns:
            None
        """
        file_name = f"keydir/{user_name}.pub"
        with open(f"{self.path}/{file_name}", "w+") as ssh_key_file:
            ssh_key_file.write(ssh_key)
        self._commit_files(f"Add {user_name} ssh key", [file_name])

    def create_repo(self, repo_name: str, user: str, public: bool):
        """
        Create a new repository in gitolite with the specified name for a given user.

        Parameters:
            repo_name (str): The name of the repository to be created.
            user (str): The user for whom the repository is being created.
            public (bool): A boolean indicating if the repository is public or not.

        Returns:
            None
        """
        with open(f"{self.path}/{conf_file_path}", "a") as conf_file:
            conf_file.write(
                f"""
repo {user}/{repo_name}
    RW+     =   {user}
"""
            )
            if public:
                conf_file.write("""    - main  =   @all\n""")
                conf_file.write("""    RW+     =   @all\n""")
        self._commit_files(
            f"Add new {'public' if public else 'private'} repo {repo_name} for user {user}",
            [conf_file_path],
        )


if __name__ == "__main__":
    gm = GitManager("../gitolite-admin")
    # gm.change_visibility("TestRepo", False)
    gm.create_repo("itamarsch/GitGud", "itamarsch", True)
