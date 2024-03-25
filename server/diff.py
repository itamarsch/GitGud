from git import Commit, Diff, DiffIndex, Repo
from git.objects.base import IndexObject


from typing import List, cast
from gitgud_types import commit_page_size


def commits_between_branches(
    repo: Repo, from_branch: str, into_branch: str, page: int
) -> List[Commit]:

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
    base_commit = cast(List[Commit], repo.merge_base(into_branch, from_branch))

    if not base_commit:
        return None

    diff = base_commit[0].diff(from_branch)
    return diff


def make_diff_str(add: bool, diff: str) -> str:
    add_remove_str = "++" if add else "--"
    return "\n".join([f"{add_remove_str}{line}" for line in diff.splitlines()])


def get_diff_string(diff: DiffIndex) -> str:

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
