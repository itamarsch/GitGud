import git


class GitManager:
    def __init__(self, path: str) -> None:
        self.repo = git.Repo(path)
        self.path = path

    def add_ssh_key(self, user_name: str, ssh_key: str):
        file_name = f"keydir/{user_name}.pub"
        with open(f"{self.path}/{file_name}", "w+") as ssh_key_file:
            ssh_key_file.write(ssh_key)

        add_file = [file_name]
        self.repo.index.add(add_file)
        self.repo.git.commit(
            "-m",
            f"Add {user_name} ssh key",
        )

        origin = self.repo.remote(name="origin")
        origin.push()

    def create_repo(self,repo_name:str, user: str, publc: bool):



if __name__ == "__main__":
    gm = GitManager("../gitolite-admin")
    gm.add_ssh_key("Reef", "fddshkdjshgklh")
