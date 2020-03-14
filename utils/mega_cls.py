#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Doc."""
import logging


class MegaJson():

    def __init__(self, json_):
        self.json = json_
        # self.list = [{"name": v['a']['n'],
        #               "descr": v['h'],
        #               "type": v['t']}
        #              for v in self.json.values()]
        # self.list = [MegaElement(name=v['a']['n'],
        #                          descr=v['h'],
        #                          type_=v['t'])
        #              for v in self.json.values()]
        # user dict is like {"documents": megaelement}
        self.user_dict = {v['a']['n']: MegaElement(name=v['a']['n'],
                                                   descr=v['h'],
                                                   type_=v['t'])
                          for v in self.json.values()}

    def get_folders_list(self):
        """Return list of folders names.

        Example : ["Documents", "Important stuff", "Misc"]
        """
        return [e.name for e in self.user_dict.values()
                if e.isfolder]

    def get_files_list(self):
        """Return list of files names.

        Example : ["doc.odt", "other_doc.xls", "photo.jpeg"]
        """
        return [e.name for e in self.user_dict.values()
                if e.isfile]

    def get_item_descr(self, name):
        """Return descr of given item."""
        return self.user_dict[name].descr


class MegaElement():

    def __init__(self, name, descr, type_):
        self.name = name
        self.descr = descr
        self.type = type_
        if type_ == 0:
            self.isfolder = False
            self.isfile = True
        elif type_ == 1:
            self.isfolder = True
            self.isfile = False
        else:
            logging.warning("Incorrect value for t")
            self.isfolder = False
            self.isfile = False

    def __str__(self):
        return f"{self.name:20} | {self.descr:10} | {self.type}"
