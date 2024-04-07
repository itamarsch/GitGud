from git import Commit, Diff, DiffIndex, Repo
from git.objects.base import IndexObject
import unidiff
import unidiff.patch


from typing import List, cast
from gitgud_types import Json, commit_page_size


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
    # base_commit = cast(List[Commit], repo.merge_base(into_branch, from_branch))
    #
    # if not base_commit:
    #     return None
    #
    # diff = base_commit[0].diff(from_branch)
    return repo.git.diff(f"{into_branch}...{from_branch}")


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


def get_diff_string(diff: str) -> Json:

    # List of files
    # Each file contains a modification type and a list of hunks
    # Each hunk contains a list of lines
    formatted_diff = []

    patch_set = unidiff.PatchSet(diff.splitlines())

    for file in patch_set:
        file = cast(unidiff.PatchedFile, file)

        file_json = {}
        if file.is_removed_file:
            file_json["type"] = f"Remove"
            file_json["file_removed"] = file.source_file
        elif file.is_added_file:
            file_json["type"] = f"Add"
            file_json["file_added"] = file.target_file
        elif file.is_rename:
            file_json["type"] = f"Rename"
            file_json["from"] = file.source_file
            file_json["to"] = file.target_file
        else:
            file_json["type"] = f"Modified"
            file_json["file_modified"] = file.target_file

        file_json["hunks"] = []
        for hunk in file:
            hunk = cast(unidiff.Hunk, hunk)

            hunk_lines = []

            for line in hunk:
                line = cast(unidiff.patch.Line, line)

                if line.is_added:
                    hunk_lines.append({"type": "Add", "value": line.value})
                elif line.is_removed:
                    hunk_lines.append({"type": "Remove", "value": line.value})
                else:
                    hunk_lines.append({"type": "Context", "value": line.value})
                hunk_lines[-1]["target_line_no"] = line.target_line_no
                hunk_lines[-1]["source_line_no"] = line.source_line_no
            file_json["hunks"].append({"lines": hunk_lines})

        formatted_diff.append(file_json)

    return {"diff": formatted_diff}
