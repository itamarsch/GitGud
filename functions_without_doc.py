import os
import ast


def extract_functions_without_docstrings(file_path):
    functions_without_docstrings = []

    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if (
                not node.body
                or not isinstance(node.body[0], ast.Expr)
                or not isinstance(node.body[0].value, ast.Constant)
            ):
                if node.name == "add_children" or node.name == "on_finished":
                    continue
                functions_without_docstrings.append(node.name)

    return functions_without_docstrings


def check_functions_without_docstrings(directory):
    functions_without_docstrings = {}

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                functions_without_docstrings[file_path] = (
                    extract_functions_without_docstrings(file_path)
                )

    return functions_without_docstrings


if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    results = check_functions_without_docstrings(directory)
    for file_path, functions in results.items():
        if functions:
            print(f"File: {file_path}")
            for function_name in functions:
                print(f"\tFunction '{function_name}' is missing a docstring.")
