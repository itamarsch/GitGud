from git import Commit, Diff, DiffIndex, Repo
from git.objects.base import IndexObject
import unidiff
import unidiff.patch


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


def get_diff_string(diff: str) -> str:
    """Captures git diff output, parses it using unidiff, formats it, and stores in a string.

    Returns:
        str: The formatted git diff output with renames addressed.
    """

    formatted_diff = ""  # Initialize empty string to store output

    patch_set = unidiff.PatchSet(diff.splitlines())

    for file in patch_set:
        file = cast(unidiff.PatchedFile, file)
        if file.is_removed_file:
            formatted_diff += f"Removed: {file.source_file} \n"
        elif file.is_added_file:
            formatted_diff += f"New file: {file.target_file}\n"
        elif file.is_rename:
            formatted_diff += f"Renamed: {file.source_file} -> {file.target_file}\n"

        for i, hunk in enumerate(file):
            if i == 0:
                formatted_diff += (
                    f"Modified: ---{file.source_file}  +++{file.target_file}\n"
                )
            hunk = cast(unidiff.Hunk, hunk)

            for line in hunk:
                line = cast(unidiff.patch.Line, line)

                if line.is_added:
                    formatted_diff += "+" + line.value + "\n"
                elif line.is_removed:
                    formatted_diff += "-" + line.value + "\n"
                else:
                    formatted_diff += line.value + "\n"
            formatted_diff += "\n"  # Print newline after each hunk

    return formatted_diff
