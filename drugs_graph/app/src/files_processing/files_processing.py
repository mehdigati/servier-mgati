import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional


def list_files_in_folder(
    folder_path: str, file_types: Optional[List[str]] = None, recursive: bool = False
) -> List[str]:
    """
    Lists all files in a folder, optionally filtering by file types and recursively"""
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Directory not found: {folder_path}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    pattern = "**/*" if recursive else "*"

    files = []
    for file_path in folder.glob(pattern):
        if file_path.is_dir():
            continue

        if file_types:
            if file_path.suffix.lower()[1:] in [
                ext.lower().strip(".") for ext in file_types
            ]:
                files.append(str(file_path))
        else:
            files.append(str(file_path))

    return sorted(files)


def create_folders_if_not_exist(output_filepath: str) -> None:
    path_split = output_filepath.split("/")
    current_path = ""

    for folder in path_split:
        if "." not in folder and not os.path.exists(folder):
            current_path += folder + "/"
            os.makedirs(current_path)


def write_dict_to_file(output_filepath: str, dictionary: Dict) -> None:
    create_folders_if_not_exist(output_filepath)

    with open(output_filepath, "w", encoding="utf-8") as hd:
        json.dump(dictionary, hd, indent=4, ensure_ascii=False)


def fix_broken_json(filepath: str) -> Dict:
    with open(filepath, "r", encoding="utf-8") as hd:
        json_str = hd.read()

    json_str = (
        json_str.replace("null", "None")
        .replace("true", "True")
        .replace("false", "False")
    )
    cleaned_json = eval(json_str)

    logging.info(f"Successfully fixed and loaded the broken Json file.")
    return cleaned_json


def import_json_file_as_dict(filepath: str) -> Dict:
    try:
        with open(filepath, "r", encoding="utf-8") as hd:
            return json.load(hd)

    except ValueError:
        logging.warning(
            f"Broken json detected in {filepath}. Attempting to clean it and re-load it."
        )
        return fix_broken_json(filepath)
