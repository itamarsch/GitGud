from git import Diff, DiffIndex
from git.objects.base import IndexObject

from typing import List, cast


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
    return "\n****************\n".join(diff_result)
