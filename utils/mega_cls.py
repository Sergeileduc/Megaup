"""Doc."""
import logging


class MegaDict():

    def __init__(self, dict_: dict):
        self.input_dict = dict_
        # user dict is like {"documents": megaelement}
        self.user_dict = {v['a']['n']: MegaElement(name=v['a']['n'],
                                                   descr=v['h'],
                                                   type_=v['t'])
                          for v in self.input_dict.values()}

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
    """A simple representation of a Mega Element, sith name, ID, and type.

    Args:
        name (str): name of the element.
        descr (str): unique ID of element.
        type (int): type of the element.

    Attributes:
        name (str): name of the element.
        descr (str): unique ID of element.
        type (int): type of the element.
        isfile (bool): if element is a file.
        isfolder (bool): if element is a folder.

    """

    def __init__(self, name: str, descr: str, type_: int):
        self.name = name
        self.descr = descr
        self.type = type_
        self.isfolder = True if type_== 1 else False
        self.isfile = True if type == 0 else False
            

    def __str__(self):
        return f"{self.name:20} | {self.descr:10} | {self.type}"
