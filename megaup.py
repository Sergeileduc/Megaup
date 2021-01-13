"""Doc."""

from dotenv import load_dotenv
import os
import pprint
from mega import Mega

import logging
from logging.handlers import RotatingFileHandler

from utils.mega_cls import MegaDict  # noqa: F401


def select_folders(files_dict):
    """Return only "folders" items in files/folders dict."""
    folders = {key: value for (key, value) in files_dict.items()
               if value['t'] == 1}
    return folders


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.DEBUG)
# logger.addHandler(stream_handler)

load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWD")

logger.info('Hello')
logger.warning('Testing')

mega = Mega()
m = mega.login(email, password)

logger.warning('Login complete')

pp = pprint.PrettyPrinter(indent=4)

files = m.get_files()
# pp.pprint(files)

print(files)

# nodes are :
'''
    0: file
    1: dir
    2: special: root cloud drive
    3: special: inbox
    4: special trash bin
'''

# print("Root dir")
# root_dict = mega.get_files_in_node(2)
# all_dict = mega.get_files()


# pp.pprint(root_dict)

# logger.warning('Files in root dir fetched')

# print("Select folders")
# folders_dict = select_folders(root_dict)
# pp.pprint(folders_dict)

# root_desc = mega.find_path_descriptor("/", all_dict)
# print(root_desc)

# doc_desc = mega.find_path_descriptor("/Documents/", all_dict)
# print("doc desc")
# print(doc_desc)

# nested_desc = mega.find_path_descriptor("/DCtrad/Nested Folder/More test (2020)", all_dict)  # noqa: E501
# print("nested desc")
# print(nested_desc)

# print("Dirs")
# doc_files = mega.get_files_in_node("xRxzXIAT")
# doc_files = mega.get_files_in_node(2)
# pp.pprint(doc_files)

# files1 = {key: value for (key, value)
#           in doc_files.items() if value['t'] == 0}


# print("Files")
# pp.pprint(files1)
# print("Folders")
# pp.pprint(folders1)

# List Documents/Test_Folder files
# descr = m.find_path_descriptor("Documents")
# doc_files = m.get_files_in_node(descr)
# pp.pprint(doc_files)


# /
# descr = mega.find_path_descriptor("")
# raw_dict = mega.get_files_in_node(descr)
# pp.pprint(raw_dict)

# mega_json = MegaJson(raw_dict)

# # pp.pprint(mega_json.json)

# # files1 = {key: value for (key, value) in raw_dict.items()
# #           if value['t'] == 0}
# print("raw folders")
# # raw_folders = {key: value for (key, value) in mega_json.json.items()
#             #    if value['t'] == 1}
# raw_folders = [value for value in mega_json.json.values()
#                if value['t'] == 1]
# raw_files = {key: value for (key, value) in raw_dict.items()
#              if value['t'] == 0}

# print(raw_folders)
# pp.pprint(raw_folders)
# list_folders = [fold['a']['n'] for fold in raw_folders.values()]
# list_files = [f['a']['n'] for f in raw_files.values()]
# print(list_folders)
# print(list_files)

# depth 1
# descr = mega.find_path_descriptor(list_folders[1])
# raw_dict = mega.get_files_in_node(descr)
# raw_folders = {key: value for (key, value) in raw_dict.items() if value['t'] == 1}  # noqa: E501
# list_folders = [fold['a']['n'] for fold in raw_folders.values()]
# print(list_folders)

# Upload a file in folder
# folder_id = m.find_path_descriptor('Documents/Test_Folder')
# print(folder_id)
# m.upload('Captain America 17.odt', folder_id)
