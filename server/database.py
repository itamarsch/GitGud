import os
import psycopg2
from dotenv import load_dotenv
from typing import List, Tuple, Optional, cast


class DB:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            dbname="gitgud",
            user="postgres",
            host=os.getenv("DB_IP"),
            port=5432,
            password=os.getenv("DB_PASSWORD"),
        )
        self.cursor = self.conn.cursor()

    def repo_by_name(self, repo: str) -> Optional[Tuple[int, str, bool]]:
        """
        Returns the repo id according to username and reponame in format "user/repo"
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
        :returns: ID of new user
        """

        self.cursor.execute(
            'INSERT INTO "User" (username, password) VALUES (%s, %s) RETURNING id',
            (username, password_hash),
        )

        id = cast(Tuple[int], self.cursor.fetchone())[0]

        self.conn.commit()
        return id

    def username_to_id(self, username: str) -> Optional[int]:

        self.cursor.execute('SELECT id FROM "User" where username = %s', (username,))
        id = self.cursor.fetchone()
        if id is None:
            return None
        return id[0]

    def add_repo(self, user_id: int, repo_name: str, public: bool) -> bool:

        self.cursor.execute(
            'INSERT INTO "Repository" (user_id, name, public) VALUES (%s, %s, %s)',
            (user_id, repo_name, public),
        )

        self.conn.commit()
        return True

    def create_issue(self, user_id: int, repo_id: int, title: str, content: str):

        self.cursor.execute(
            'INSERT INTO "Issue" (user_id, repo_id, title, content) VALUES (%s ,%s, %s, %s)',
            (user_id, repo_id, title, content),
        )

        self.conn.commit()

    def issues(self, repo_id: int) -> List[Tuple[int, str, str, str]]:
        """
        Returns all issues for repo in the format id, username, title, content
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

        self.cursor.execute('DELETE FROM "Issue" where id = %s', (issue_id,))

        self.conn.commit()

    def update_issue(
        self,
        issue_id: int,
        title: str,
        content: str,
    ):

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
        self.cursor.execute(
            'INSERT INTO "PullRequest" (title, from_branch, into_branch, repo_id, user_id) VALUES (%s, %s, %s, %s, %s)',
            (title, from_branch, into_branch, repo_id, user_id),
        )
        self.conn.commit()

    def delete_pr(self, pr_id: int):
        self.cursor.execute('DELETE FROM "PullRequest" where id = %s', (pr_id,))
        self.conn.commit()

    def update_pr(self, id: int, title: str, from_branch: str, into_branch: str):
        self.cursor.execute(
            'UPDATE "PullRequest" set title = %s, from_branch = %s, into_branch = %s where id = %s',
            (title, from_branch, into_branch, id),
        )
        self.conn.commit()

    def pull_requests(self, repo_id: int) -> List[Tuple[int, str, str, str, str]]:
        """
        Returns all pull request for repository in the format: id, username, title, from_branch, into_branch
        """
        self.cursor.execute(
            """
SELECT "PullRequest".id, "User".username, "PullRequest".title, "PullRequest".from_branch, "PullRequest".into_branch 
from "PullRequest" 
INNER JOIN "User" on "User".id="PullRequest".user_id
where repo_id = %s
""",
            (repo_id,),
        )
        return cast(List[Tuple[int, str, str, str, str]], self.cursor.fetchall())

    def change_repo_visibility(self, repo_id: int, public: bool):
        self.cursor.execute(
            'UPDATE "Repository" set public = %s where id = %s', (public, repo_id)
        )
        self.conn.commit()

    def user_exists(self, username: str) -> bool:
        self.cursor.execute('SELECT id from "User" where username = %s', (username,))
        user = self.cursor.fetchone()
        return user is not None

    def validate_user(self, username: str, password_hash: str) -> bool:

        self.cursor.execute(
            'SELECT password from "User" where username = %s', (username,)
        )

        password_res = self.cursor.fetchone()
        if password_res is None:
            return False
        password_hash_db: str = cast(str, password_res[0])
        return password_hash == password_hash_db

    def search_repos(self, search_query: str) -> List[Tuple[int, str, str]]:
        """
        Returns all repositorys that fit search query in format: id, creator_name, repository_name
        """

        self.cursor.execute(
            """
SELECT "Repository".id, "User".username, "Repository".name
from "Repository" 
INNER JOIN "User" on "Repository".user_id="User".id
where "Repository".name LIKE %s and "Repository".public
""",
            (search_query,),
        )

        return cast(
            List[Tuple[int, str, str]],
            self.cursor.fetchall(),
        )

    def repo_and_owner_of_issue(self, issue_id: int) -> Optional[Tuple[str, str]]:
        """
        Returns the the owner and reponame of issue
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

    def repo_and_owner_of_pr(self, pr_id: int) -> Optional[Tuple[str, str]]:
        """
        Returns the the owner and reponame of pr
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
        Returns: into_branch, from_branch of pr
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
    print(db.search_repos("Git___"))
