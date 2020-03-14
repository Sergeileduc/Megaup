#!/usr/bin/python3
# -*-coding:utf-8 -*-

import json
import os

import sys
sys.path.append('../')

from utils.mega_accounts_choice import AccountChoice

dir_path = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(dir_path, "conf.json")

with open("conf.json", encoding='utf-8') as json_file:
    data = json.load(json_file, encoding="utf-8")

app = AccountChoice(config=data)
app.protocol("WM_DELETE_WINDOW", app._quit)
app.mainloop()

account = app.selected_account
print(f"User chose account : {account}")
