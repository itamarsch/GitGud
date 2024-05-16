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


def get_diff_json(git_diff_output: str) -> Json:
    """
    Creates a json object from the output of git diff,
    List of files, each file has a type and according to the type has the fields:
    Add: file_added
    Remove: file_removed
    Rename: file_added
    Modified: file_modified

    Each file contains a list of hunks
    Each hunk contains a list of lines
    Each line contains: value, type: (Add, Remove, Context), target_line_no, source_line_no


    Parameters:
        git_diff_output (str) The output of a git diff command

    Returns:
        Json: a json representing a diff
    """

    formatted_diff = []

    patch_set = unidiff.PatchSet(git_diff_output.splitlines())

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
                json_line: Json = {}

                if line.is_added:
                    json_line = {"type": "Add", "value": line.value}
                elif line.is_removed:
                    json_line = {"type": "Remove", "value": line.value}
                else:
                    json_line = {"type": "Context", "value": line.value}

                json_line["target_line_no"] = line.target_line_no
                json_line["source_line_no"] = line.source_line_no

                hunk_lines.append(json_line)

            file_json["hunks"].append({"lines": hunk_lines})

        formatted_diff.append(file_json)

    return {"diff": formatted_diff}
