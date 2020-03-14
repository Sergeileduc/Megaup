#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Doc."""

import pprint
from mega import Mega

import logging
from logging.handlers import RotatingFileHandler

# from mega_obj import MegaJson


# def select_folders(files_dict):
#     """Return only "folders" items in files/folders dict."""
#     folders = {key: value for (key, value) in files_dict.items()
#                if value['t'] == 1}
#     return folders


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

email = "sergei.leduc@gmail.com"
password = "4:VnjC7:RZF!zzs"

logger.info('Hello')
logger.warning('Testing')

mega = Mega()
m = mega.login(email, password)

logger.warning('Login complete')

pp = pprint.PrettyPrinter(indent=4)

files = m.get_files()

pp.pprint(files)
