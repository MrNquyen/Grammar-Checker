import os
import re
import glob
import json
import pickle
import glob
import yaml
import os
import numpy as np

from PIL import Image 
from tqdm import tqdm
from icecream import ic
from argparse import Namespace

# ==== LOAD FILES ====
def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        json_content = json.load(file)
        return json_content
    
#---- Save json
def save_json(path, content):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=3)


#---- Load numpy
def load_npy(path):
    return np.load(path, allow_pickle=True)


#---- Load yaml file
def load_yml(path):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
        return config
    
# ==== File Processing ====
def read_file_as_bytes(path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return pdf_bytes

def read_plain_text_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        return content

def save_plain_text_file(content, path):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)


# ==== UTILS ====
def update_dict(original: dict, updates: dict) -> dict:
    original.update(updates)
    return original

# ==== FUNCTION ====
def read_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        return html_content


# ==== FILE FUNCTIONS ====
def get_all_file(
        folder_path: str,
        postfix: str ="htm"
    ):
    """
    Get all file in directory that match postfix

    Args:
        folder_path (str): Root folder where you want to get all matching files
        postfix (str, optional): postfix of a file name. Defaults to ".htm".

    Returns:
        List[str]: All file paths that match postfix  
    """
    return glob.glob(os.path.join(folder_path, '**', f'*.{postfix}'), recursive=True)


def get_file_name(file_path: str, get_postfix=True):
    """_summary_

    Args:
        file_path (str): file path
        get_postfix (bool, optional): Get the postfix or not. Defaults to True.
    """
    basename = os.path.basename(file_path)
    if get_postfix:
        return basename
    return basename.split(".")[0]


def load_yml_to_args(yml_path):
    """
    Load yml config file as arg parser object

    Args:
        yml_path (str): path to yml file
    """
    def dict_to_namespace(d):
        """Recursively convert dict to Namespace"""
        if isinstance(d, dict):
            return Namespace(**{k: dict_to_namespace(v) for k, v in d.items()})
        elif isinstance(d, list):
            return [dict_to_namespace(x) for x in d]
        else:
            return d
    yml_file = load_yml(yml_path)
    args = dict_to_namespace(yml_file)
    return args

#-- CLEAN LOCAL_PATH
def clean_local_path(path: str) -> str:
    return path.replace('"', "").strip()

