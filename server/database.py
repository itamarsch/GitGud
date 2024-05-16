import os
import psycopg2
from dotenv import load_dotenv
from typing import List, Tuple, Optional, cast


class DB:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            host=os.getenv("DB_IP"),
            port=5432,
            password=os.getenv("DB_PASSWORD"),
        )
        self.cursor = self.conn.cursor()

    def repo_by_name(self, repo: str) -> Optional[Tuple[int, str, bool]]:
        """
        A function that retrieves a repository by name from the database.

        Parameters:
            repo (str): The name of the repository in the format 'username/repo_name'.

        Returns:
            Optional[Tuple[int, str, bool]]: A tuple containing the repository's id, name, and public status if found,
                                              or None if the repository is not found.
        """
        [user, repo] = repo.split("/")

        self.cursor.execute('SELECT id from "User" where username = %s', (user,))
        user_id_res = cast(Optional[Tuple[int]], self.cursor.fetchone())
        if user_id_res is None:
            return None
        user_id = user_id_res[0]

        self.cursor.execute(
            'SELECT id, name, public from "Repository" where name = %s and user_id = %s',
            (repo, user_id),
        )
        repo_id_res = cast(Optional[Tuple[int, str, bool]], self.cursor.fetchone())
        if repo_id_res is None:
            return None
        return repo_id_res

    def add_user(self, username: str, password_hash: str) -> int:
        """
        Adds a new user to the database with the provided username and password hash.

        Parameters:
            username (str): The username of the user.
            password_hash (str): The hashed password of the user.

        Returns:
            int: The id of the newly added user.
        """

        self.cursor.execute(
            'INSERT INTO "User" (username, password) VALUES (%s, %s) RETURNING id',
            (username, password_hash),
        )

        id = cast(Tuple[int], self.cursor.fetchone())[0]

        self.conn.commit()
        return id

    def username_to_id(self, username: str) -> Optional[int]:
        """
        Converts a username to an ID using the provided username string.

        Parameters:
            username (str): The username to be converted to an ID.

        Returns:
            Optional[int]: The ID corresponding to the username if found, otherwise None.
        """

        self.cursor.execute('SELECT id FROM "User" where username = %s', (username,))
        id = self.cursor.fetchone()
        if id is None:
            return None
        return id[0]

    def add_repo(self, user_id: int, repo_name: str, public: bool) -> bool:
        """
        A function to add a repository to the database.

        Parameters:
            user_id (int): The ID of the user adding the repository.
            repo_name (str): The name of the repository.
            public (bool): A boolean indicating if the repository is public.

        Returns:
            bool: True if the repository was successfully added.
        """

        self.cursor.execute(
            'INSERT INTO "Repository" (user_id, name, public) VALUES (%s, %s, %s)',
            (user_id, repo_name, public),
        )

        self.conn.commit()
        return True

    def create_issue(self, user_id: int, repo_id: int, title: str, content: str):
        """
        Creates an issue in the database with the provided user ID, repository ID, title, and content.

        Parameters:
            user_id (int): The ID of the user creating the issue.
            repo_id (int): The ID of the repository where the issue is created.
            title (str): The title of the issue.
            content (str): The content of the issue.

        Returns:
            None
        """

        self.cursor.execute(
            'INSERT INTO "Issue" (user_id, repo_id, title, content) VALUES (%s ,%s, %s, %s)',
            (user_id, repo_id, title, content),
        )

        self.conn.commit()

    def issues(self, repo_id: int) -> List[Tuple[int, str, str, str]]:
        """
        Retrieve a list of issues for the given repository ID.

        Parameters:
            repo_id (int): The ID of the repository.

        Returns:
            List[Tuple[int, str, str, str]]: A list of tuples containing the issue ID, username, title, and content.
        """

        self.cursor.execute(
            """
SELECT "Issue".id, "User".username, "Issue".title, "Issue".content 
from "Issue" 
INNER JOIN "User" on "User".id="Issue".user_id
where repo_id = %s""",
            (repo_id,),
        )

        return cast(List[Tuple[int, str, str, str]], self.cursor.fetchall())

    def delete_issue(self, issue_id: int):
        """
        Deletes an issue from the database based on the given issue_id.

        Parameters:
            issue_id (int): The unique identifier of the issue to be deleted.

        Returns:
            None
        """

        self.cursor.execute('DELETE FROM "Issue" where id = %s', (issue_id,))

        self.conn.commit()

    def update_issue(
        self,
        issue_id: int,
        title: str,
        content: str,
    ):
        """
        Update title, and content for the issue with the given issue_id, .

        Parameters:
            issue_id (int): The ID of the issue to be updated.
            title (str): The new title for the issue.
            content (str): The new content for the issue.
        """

        self.cursor.execute(
            'UPDATE "Issue" set content = %s, title = %s where id = %s',
            (content, title, issue_id),
        )

        self.conn.commit()

    def create_pr(
        self,
        title: str,
        from_branch: str,
        into_branch: str,
        repo_id: int,
        user_id: int,
    ):
        """
        Creates a pull request with the specified title, from_branch, into_branch, repo_id, and user_id.

        Parameters:
            title (str): The title of the pull request.
            from_branch (str): The source branch of the pull request.
            into_branch (str): The target branch of the pull request.
            repo_id (int): The ID of the repository.
            user_id (int): The ID of the user creating the pull request.
        """
        self.cursor.execute(
            'INSERT INTO "PullRequest" (title, from_branch, into_branch, repo_id, user_id) VALUES (%s, %s, %s, %s, %s)',
            (title, from_branch, into_branch, repo_id, user_id),
        )
        self.conn.commit()

    def delete_pr(self, pr_id: int):
        """
        Delete a pull request from the database.

        Parameters:
            pr_id (int): The ID of the pull request to be deleted.

        Returns:
            None
        """
        self.cursor.execute('DELETE FROM "PullRequest" where id = %s', (pr_id,))
        self.conn.commit()

    def update_pr(self, id: int, title: str, from_branch: str, into_branch: str):
        """
        Updates a Pull Request record in the database with the provided title, from_branch, and into_branch for a given id.

        Parameters:
            id (int): The unique identifier of the Pull Request record.
            title (str): The new title for the Pull Request.
            from_branch (str): The branch the Pull Request is coming from.
            into_branch (str): The branch the Pull Request is going into.
        """
        self.cursor.execute(
            'UPDATE "PullRequest" set title = %s, from_branch = %s, into_branch = %s where id = %s',
            (title, from_branch, into_branch, id),
        )
        self.conn.commit()

    def pull_requests(self, repo_id: int) -> List[Tuple[int, str, str, str, str, bool]]:
        """
        Retrieves pull requests for a given repo_id.

        Parameters:
            repo_id (int): The ID of the repository.

        Returns:
            List[Tuple[int, str, str, str, str, bool]]: A list of tuples representing pull requests, each containing the ID, username, title, from_branch, into_branch, and approval status.
        """
        self.cursor.execute(
            """
SELECT "PullRequest".id, "User".username, "PullRequest".title, "PullRequest".from_branch, "PullRequest".into_branch, "PullRequest".approved
from "PullRequest" 
INNER JOIN "User" on "User".id="PullRequest".user_id
where repo_id = %s
""",
            (repo_id,),
        )
        return cast(List[Tuple[int, str, str, str, str, bool]], self.cursor.fetchall())

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.

        Parameters:
            username (str): The username to check existence for.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        self.cursor.execute('SELECT id from "User" where username = %s', (username,))
        user = self.cursor.fetchone()
        return user is not None

    def validate_user(self, username: str, password_hash: str) -> bool:
        """
        Validates the user by checking if the provided password hash matches the one stored in the database for the given username.

        Parameters:
            username (str): The username of the user to validate.
            password_hash (str): The hashed password to validate.

        Returns:
            bool: True if the password hash matches the one in the database, False otherwise.
        """

        self.cursor.execute(
            'SELECT password from "User" where username = %s', (username,)
        )

        password_res = self.cursor.fetchone()
        if password_res is None:
            return False
        password_hash_db: str = cast(str, password_res[0])
        return password_hash == password_hash_db

    def all_repos(self) -> List[Tuple[int, str, str]]:
        """
        Retrieve all public repositories from the database, including the repository id, owner's username, and repository name.
        """

        self.cursor.execute(
            """
SELECT "Repository".id, "User".username, "Repository".name
from "Repository" 
INNER JOIN "User" on "Repository".user_id="User".id
where "Repository".public
""",
        )

        return cast(
            List[Tuple[int, str, str]],
            self.cursor.fetchall(),
        )

    def repo_and_repo_owner_of_issue(self, issue_id: int) -> Optional[Tuple[str, str]]:
        """
        A function to retrieve the repository and repository owner of a given issue.

        Parameters:
            issue_id (int): The ID of the issue.

        Returns:
            Optional[Tuple[str, str]]: A tuple containing the repository owner's username and the repository name, or None if no such issue is found.
        """

        self.cursor.execute(
            """
SELECT "User".username, "Repository".name
FROM "Issue"
JOIN "Repository" ON "Issue".repo_id = "Repository".id
JOIN "User" ON "Repository".user_id = "User".id
WHERE "Issue".id = %s
""",
            (issue_id,),
        )
        user_repo = self.cursor.fetchone()

        return cast(Optional[Tuple[str, str]], user_repo)

    def repo_and_repo_owner_of_pr(self, pr_id: int) -> Optional[Tuple[str, str]]:
        """
        Retrieves the repository name and owner username associated with the given pull request ID.

        Parameters:
            pr_id (int): The ID of the pull request.

        Returns:
            Optional[Tuple[str, str]]: A tuple containing the username of the repository owner and the name of the repository, or None if the pull request ID is not found.
        """

        self.cursor.execute(
            """
SELECT "User".username, "Repository".name
FROM "PullRequest"
JOIN "Repository" ON "PullRequest".repo_id = "Repository".id
JOIN "User" ON "Repository".user_id = "User".id
WHERE "PullRequest".id = %s
""",
            (pr_id,),
        )
        user_repo = self.cursor.fetchone()

        return cast(Optional[Tuple[str, str]], user_repo)

    def pr_branches(self, id: int) -> Optional[Tuple[str, str]]:
        """
        Fetches the into_branch and from_branch for the given pull request ID.

        Parameters:
            id (int): The ID of the pull request.

        Returns:
            Optional[Tuple[str, str]]: A tuple containing the into_branch and from_branch, or None if no result is found.
        """

        self.cursor.execute(
            """SELECT into_branch, from_branch FROM "PullRequest" WHERE id = %s""",
            (id,),
        )

        branches = self.cursor.fetchone()
        return cast(Optional[Tuple[str, str]], branches)


if __name__ == "__main__":
    load_dotenv()
    db = DB()
