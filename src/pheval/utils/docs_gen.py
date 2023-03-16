"""docs generate utils"""
import ast
import os
import shutil
from pathlib import Path


def find_methods_in_python_file(file_path):
    """Return method names from a python file

    Args:
        file_path ([type]): [description]
    """
    methods = []
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
        parsed = ast.parse(text)
        for node in ast.walk(parsed):
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)

    return methods


def list_valid_files():
    """list_valid_files"""
    ignored_files = ["docs_gen", "__init__"]
    source_folder = f"{os.path.dirname(os.path.realpath(__file__))}/../../../src"
    files = Path(source_folder).rglob("*.py")
    filtered_files = []
    for file in files:
        if os.stat(file).st_size == 0 or not os.path.isfile(file):
            continue

        folder_parts = Path(file).parts
        idx = folder_parts.index("..") + 2
        folder = "/".join(folder_parts[idx:-1])
        basename = os.path.basename(file).split(".")[0]

        docs_path = f"../../../docs/api/pheval/{folder.replace('src/', '')}/{basename}.md"
        if basename in ignored_files:
            continue

        filtered_files.append(
            {
                "path": file,
                "docs_path": docs_path,
                "basename": basename,
                "folder": folder,
            }
        )

    return filtered_files


def print_api_doc(file_item):
    "print_api_doc"
    clean_path = str(file_item["folder"]).replace("./", '').replace("/", ".")[1:]
    write_doc(file_item, f"::: {clean_path}.{file_item['basename']}")


def write_doc(file_item, content):
    """write_doc"""
    os.makedirs(os.path.dirname(file_item["docs_path"]), exist_ok=True)
    with open(file_item["docs_path"], "a", encoding="utf-8") as file:
        file.write(content)


def print_cli_doc(file_item):
    """print_cli_doc"""
    methods = find_methods_in_python_file(file_item["path"])
    for method in methods:
        content = f"""
::: mkdocs-click
    :package: {file_item['folder'].replace("./", '').replace('/', '.')}.{file_item['basename']}
    :module: {file_item['folder'].replace("./", '').replace('/', '.')[1:].replace('src.', '')}.{file_item['basename']}
    :command: {method}
    :depth: 4
    :style: table
    :list_subcommands: true
        """
        write_doc(file_item, content)


def gen_docs():
    """gen_docs"""
    api_folder = f"{os.path.dirname(os.path.realpath(__file__))}/../../../docs/api"
    shutil.rmtree(api_folder, ignore_errors=True)
    valid_files = list_valid_files()
    for file_item in valid_files:
        bname = file_item["basename"]
        if bname == "cli":  # or bname.startswith("cli_"):
            print(bname)
            print_cli_doc(file_item)
        elif bname.startswith("cli_"):
            continue
        else:
            print_api_doc(file_item)


if __name__ == "__main__":
    gen_docs()
