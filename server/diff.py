from git import Commit, Diff, DiffIndex, Repo
from git.objects.base import IndexObject


from typing import List, cast
from gitgud_types import commit_page_size

def commits_between_branches(
    repo: Repo, from_branch: str, into_branch: str, page: int
) -> List[Commit]:
    """
    Returns a list of commits between two branches of a given repository.

    Parameters:
        repo (Repo): The repository object.
        from_branch (str): The name of the source branch.
        into_branch (str): The name of the target branch.
        page (int): The page number for pagination.

    Returns:
        List[Commit]: A list of Commit objects between the specified branches.
    """

    merge_base = cast(List[Commit], repo.merge_base(into_branch, from_branch))
    if not merge_base:
        return []
    merge_base_commit = merge_base[0]

    commits = []
    for i, commit in enumerate(
        repo.iter_commits(from_branch, max_count=commit_page_size)
    ):
        if commit.hexsha == merge_base_commit.hexsha:
            break
        if i < page * commit_page_size:
            continue
        commits.append(commit)

    return commits


def triple_dot_diff(repo: Repo, into_branch: str, from_branch: str):
    """
    Calculate the difference between two branches in the given repository.

    Parameters:
        repo (Repo): The repository object.
        into_branch (str): The name of the branch into which changes are merged.
        from_branch (str): The name of the branch from which changes are merged.

    Returns:
        diff: The difference between the two branches.
    """
    base_commit = cast(List[Commit], repo.merge_base(into_branch, from_branch))

    if not base_commit:
        return None

    diff = base_commit[0].diff(from_branch)
    return diff


def make_diff_str(add: bool, diff: str) -> str:
    """
    A function that generates a diff string with added or removed markers for each line.
    
    Parameters:
    - add (bool): A flag indicating whether to add or remove lines.
    - diff (str): The string containing the lines to be marked.
    
    Returns:
    - str: The formatted string with markers for added or removed lines.
    """
    add_remove_str = "++" if add else "--"
    return "\n".join([f"{add_remove_str}{line}" for line in diff.splitlines()])


def get_diff_string(diff: DiffIndex) -> str:
    """
    Generate a string representation of the differences in the given DiffIndex object.

    Parametes:
        diff (DiffIndex): The DiffIndex object containing the differences.

    Returns:
        str: A string representing the differences in the format: 
        "Rename: {old_name} -> {new_name}" for rename operations,
        "Added: {path}\n{diff}" for added operations,
        "Deleted: {path}\n{diff}" for deleted operations,
        "Modified: {path}\n{old_diff}\n{new_diff}" for modified operations.
    """

    diff_result: List[str] = []
    for diff_item in diff.iter_change_type("R"):
        diff_item: Diff
        diff_result.append(f"Rename: {diff_item.rename_from} -> {diff_item.rename_to}")
    for diff_item in diff.iter_change_type("A"):
        diff_item: Diff
        blob = cast(IndexObject, diff_item.b_blob).data_stream.read().decode("utf-8")

        blob = make_diff_str(True, blob)
        diff_result.append(f"Added: {diff_item.b_path}\n{blob}")

    for diff_item in diff.iter_change_type("D"):
        diff_item: Diff
        blob = cast(IndexObject, diff_item.a_blob).data_stream.read().decode("utf-8")

        blob = make_diff_str(False, blob)
        diff_result.append(f"Deleted: {diff_item.a_path}\n{blob}")

    for diff_item in diff.iter_change_type("M"):
        diff_item: Diff

        b_blob: str = (
            cast(IndexObject, diff_item.b_blob).data_stream.read().decode("utf-8")
        )
        a_blob: str = (
            cast(IndexObject, diff_item.a_blob).data_stream.read().decode("utf-8")
        )
        b_blob = make_diff_str(True, b_blob)
        a_blob = make_diff_str(False, a_blob)
        diff_result.append(f"Modified: {diff_item.b_path}\n" + b_blob + "\n" + a_blob)
    return ("\n" + "───────────────" + "\n").join(diff_result)
