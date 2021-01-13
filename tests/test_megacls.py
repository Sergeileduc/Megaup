#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Unit tests meg_cls."""

from dotenv import load_dotenv
import os
import pytest

from mega import Mega
from utils.mega_cls import MegaDict
from tests.megafiles import r


import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def test_megadict():
    """Test MegaDict."""
    m = MegaDict(r)
    # print(m)
    print()
    folders = m.get_folders_list()
    files = m.get_files_list()
    print(folders)
    print(files)
    assert m is not None


def test_mega():
    load_dotenv()
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWD")

    mega = Mega()
    m = mega.login(email, password)
    all_dict = m.get_files()
    print(all_dict)
    # root_desc = mega.find_path_descriptor("/", all_dict)
    # print()
    # print(root_desc)

    # m_dict = MegaDict(all_dict)
    # folders = m_dict.get_folders_list()
    # print(folders)
    # doc_desc = mega.find_path_descriptor("/Documents/", all_dict)
    # print("doc desc")
    # print(doc_desc)

    # nested_desc = mega.find_path_descriptor("/DCtrad/Nested Folder/More test (2020)", all_dict)
    # # print("nested desc")
    # print(nested_desc)

    # # print("Dirs")
    # # doc_files = mega.get_files_in_node("xRxzXIAT")
    # # doc_files = mega.get_files_in_node(2)
    # # pp.pprint(doc_files)
    # nested_files = mega.get_files_in_node(nested_desc)
    # m_dict = MegaDict(nested_files)
    # file_list = m_dict.get_files_list()
    # print(file_list)

    # remote_file = m.upload("Captain America 17.odt", dest=nested_desc)
    # print(remote_file)
    # link = m.get_upload_link(remote_file)
    # print(link)
