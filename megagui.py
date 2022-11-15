"""Upload file to Onwcloud, extract cover, and upload to casimages.

Return BBcode.
"""

import logging
import sys
import json
import os
import random
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from tkinter import END, SEL, INSERT
import zipfile

import requests
from Crypto.Cipher import AES
from Crypto.Util import Counter
from mega.crypto import (
    a32_to_base64, encrypt_key, encrypt_attr,
    a32_to_str, get_chunks, str_to_a32, makebyte,
    base64_url_encode
)

# import subprocess
# import sys
# import logging
# import logging.config

# import tkinter  # for pyinstaller
# import bs4  # for pyinstaller

# from pathlib import Path

from mega import Mega
from py_casim import Casim, CasimLogged
from utils.mega_accounts_choice import AccountChoice
from utils.tools import extract_cover, get_base_name, no_ext
from utils.mega_cls import MegaDict

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(dir_path, "conf.json")

redim_val = 640

cloud_dir = "/"
cover_bool = False
variant_bool = False

# Check command line arguments
if len(sys.argv) < 2:
    print("Missing command line argument (cbz file)")
    sys.exit()


class MegaObj():
    """Basic class for mega items.
    """
    def __init__(self, raw=None):
        if raw:
            self.split_info = raw.split(maxsplit=5)
            # self._parse_raw()

    # def _parse_raw(self):
    #     self.columns = self.raw.split()
    #     self.name = self.columns[5]

    def is_dir(self):
        return self.split_info[0] == "d---"

    def get_name(self):
        name = self.split_info[5]
        return name


class MegaException(Exception):
    """Custom Exception for mega, with status code.
    """
    def __init__(self, res, errorType):
        if isinstance(res, int):
            code = res
        else:
            code = res.status_code
            self.res = res
        Exception.__init__(self, errorType + " error: %i" % code)
        self.status_code = code


class MegaClient():
    """Mega client.
    """
    def __init__(self, config_dict):
        self.conf = config_dict
        self.is_logged = False
        self.connected_user = None
        self.mail = self.conf["login"]
        self.passwd = self.conf["passwd"]
        self.mega = Mega()
        self.filelist = None

    def login(self):
        self.mega.login(self.mail, self.passwd)

    def logout(self):
        pass

    def fetch_file_list(self):
        self.filelist = self.mega.get_files()

    def ls_l(self, dir_):
        dir_id = self.mega.find_path_descriptor(dir_, self.filelist)
        files_in_node = self.mega.get_files_in_node(dir_id)
        # doc_files = mega.get_files_in_node(2)
        # pp.pprint(doc_files)
        # nested_files = mega.get_files_in_node(nested_desc)
        m_dict = MegaDict(files_in_node)
        folder_list = m_dict.get_folders_list()
        return sorted(folder_list)

    def put(self, file_, remotedir):
        desc = self.mega.find_path_descriptor(remotedir, self.filelist)
        remote_file = self.mega.upload(file_, dest=desc)
        return remote_file

    def share(self, remote_file):
        return self.mega.get_upload_link(remote_file)


class MegaExplorer(tk.Toplevel):
    """GUI for exploring Mega folders.
    """
    def __init__(self, master=None, mega=None):
        tk.Toplevel.__init__(self, master)
        # self.racine = master
        # self.conf = conf
        self.withdraw()

        self.folder_path = "/"
        self.previous_folder_path = []
        self.folder_name = ""

        self.folder_list = []

        self.mega = mega
        self._login()

        self.title("Dossiers Mega")

        self.frame = tk.Frame(self)
        self.lb = tk.Listbox(self.frame, width=60, height=15,
                             font=("Helvetica", 12))
        self.frame.pack(fill="both", expand=1)

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.lb.config(yscrollcommand=self.scrollbar.set)

        self.lb.pack(side="left", fill="both", expand=1)

        # Buttons
        self.bottom_bar = tk.Frame(self)
        self.bottom_bar.pack(side='bottom')
        self.b1 = tk.Button(self.bottom_bar, text="Précédent",
                            command=self._up,
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2)  # noqa:E501
        self.b2 = tk.Button(self.bottom_bar, text="Ajouter le chemin",
                            command=self._select,
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2)

        self.b1.pack(side="left", padx=30)
        self.b2.pack(side="left", padx=30)

        self._populate_list()
        self.lb.bind('<Double-Button-1>', self.double_click)

        self._alt_center(30)
        self.deiconify()

    def double_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        index = selection[0]
        # value = widget.get(selection[0])
        # print("selection:", selection, ": '%s'" % value)
        self.previous_folder_path.append(self.folder_path)
        # print(self.folder_list)
        self.folder_path = self.folder_list[index]["path"]

        # print(self.folder_path)
        self.folder_list = []
        self.lb.delete(0, tk.END)
        # print('double mouse click event')
        self._populate_list()

    def _login(self):
        self.mega.login()
        self.mega.fetch_file_list()
        self.mega.ls_l("/")

    def _up(self):
        self.folder_list = []
        self.lb.delete(0, tk.END)

        try:
            self.folder_path = self.previous_folder_path.pop()
        except IndexError:
            pass
        self._populate_list()

    def _select(self):
        try:
            sel = self.lb.curselection()[0]
            s = self.folder_list[sel]["path"]
        except IndexError:
            s = self.folder_path

        # print(f"Cloud dir = {self.cloud_dir}")
        self.master.new_dir = s[1:] if s.startswith("/") else s
        # self.master.destroy()
        self.destroy()

    def _populate_list(self):
        list_dir = self.mega.ls_l(self.folder_path)
        for dir_ in list_dir:
            # print(name)
            # full_path = file.get_path() + '/' + newName
            # full_path = dir_.get_path()
            if self.folder_path != '/':
                full_path = self.folder_path + '/' + dir_
            else:
                full_path = '/' + dir_
            self.folder_list.append({'path': full_path, 'name': dir_})

        [self.lb.insert(END, item["name"]) for item in self.folder_list]

    def _alt_center(self, pad):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2) + pad
        y = (self.winfo_screenheight() // 2) - (height // 2) + pad
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class PathChoice(tk.Tk):

    def __init__(self, *args, file_=None, account=None, mega=None, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.withdraw()

        self.title("Choix du chemin Méga")

        # self.conf_file = os.path.join(Path.home(), file_)
        self.conf_file = file_
        self.account = account
        self.paths_list = []
        self.mega = mega

        self.selected_cloud_dir = ""
        self.redim = tk.StringVar()
        self.choices = ["640", "320", "125", "Miniature"]

        self.redim.set(self.choices[0])

        # self._init_file()
        self._read_file()
        self._read_fav()
        # self._print_list()

        # One frame for lisbox and scrollbar
        self.frame = tk.Frame(self)

        self.lb = tk.Listbox(self.frame, width=60, height=12,
                             font=("Helvetica", 12))
        [self.lb.insert(END, item) for item in self.paths_list]

        self.frame.pack(fill="both", expand=1)

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.lb.config(yscrollcommand=self.scrollbar.set)

        self.lb.pack(side="left", fill="both", expand=1)

        # Another Frame for buttons
        self.button_bar = tk.Frame(self)
        self.button_bar.pack(fill='x', padx=10, ipady=10)
        # tk.Button(self.button_bar, text="Sauver et Quitter", command=self._quit).pack(side=LEFT)  # noqa:E501
        self.b1 = tk.Button(self.button_bar, text="Suppimer",
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2,
                            command=self._remove,
                            bg="#ede7f6",
                            activebackground="#fff7ff")
        self.b2 = tk.Button(self.button_bar, text="Nouveau chemin",
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=14, height=2,
                            command=self._add,
                            bg="#ede7f6",
                            activebackground="#fff7ff")
        self.b3 = tk.Button(self.button_bar,
                            text="Sélectionner et uploader",
                            bd=0, font=("Helvetica", 12, "bold"),
                            width=18, height=2,
                            command=self._select,
                            bg="#311b92",
                            activebackground="#000063",
                            activeforeground="#fff",
                            fg="#fff")

        self.b1.pack(side="left")
        self.b2.pack(side="left")
        self.b3.pack(side="right")

        # Another Frame for checkbox
        self.bottom_bar = tk.Frame(self)
        self.bottom_left = tk.Frame(self)
        self.bottom_right = tk.Frame(self)
        self.check_casi = tk.IntVar()
        self.check_variant = tk.IntVar()

        self.c = tk.Checkbutton(self.bottom_left,
                                justify="left",
                                text=("Et uploader la cover sur Casimages\n"
                                      "Donne un lien de partage avec balise [img]"),  # noqa:E501
                                variable=self.check_casi)

        self.c2 = tk.Checkbutton(self.bottom_left,
                                 justify="left",
                                 text=("avec variante"),
                                 variable=self.check_variant)

        self.choice = tk.OptionMenu(self.bottom_right, self.redim, *self.choices)  # noqa:E501

        self.bottom_bar.pack(side='bottom', fill='x', padx=10, ipady=10)
        self.bottom_left.pack(side='left')
        self.bottom_right.pack(side='left')
        self.c.pack(side='left', padx=(0, 10))
        self.c2.pack(side='left', padx=(0, 10))
        # self.choice.configure(width=5)
        self.choice.pack(side='left')

        self._center()
        self.deiconify()

    def _init_file(self):
        # Create file if not exists
        pass

    def _read_file(self):
        with open(self.conf_file, encoding='utf-8') as json_file:
            self.data = json.load(json_file)

    def _read_fav(self):
        self.paths_list = self.data[self.account]["fav"]

    def _print_list(self):
        for p in self.paths_list:
            print(p)

    def _remove(self):
        sel = self.lb.curselection()
        if len(sel) > 0:
            index = self.paths_list.index(self.lb.get(sel[0]))
            self.lb.delete(sel)
            self.paths_list.pop(index)
            self.data[account]["fav"] = self.paths_list

    def _add(self):
        self.new_dir = ""
        self.wait_window(self._add_path())
        if self.new_dir:
            print(f"Adding : {self.new_dir}")
            self.paths_list.append(self.new_dir)
            self.lb.insert(END, self.new_dir)
            self.data[account]["fav"] = self.paths_list
        # self.lb.insert(END, self.paths_list[-1])

    def _select(self):
        self._save_file()

        try:
            self.selected_cloud_dir = self.lb.get(self.lb.curselection())
            self.destroy()
        except tk.TclError:
            pass

    def _quit(self):
        print("Quitting")
        self._save_file()
        self.destroy()
        sys.exit()

    def _add_path(self):
        """Create tkinter 'add path' window."""
        # top = tk.Toplevel()
        top = MegaExplorer(self, mega=self.mega)
        return top

    def _save_file(self):
        self.paths_list.sort()

        if "Edit" in self.paths_list:
            self.paths_list.insert(0, self.paths_list.pop(self.paths_list.index("Edit")))  # noqa:E501
        with open(self.conf_file, 'w', encoding='utf-8') as outfile:
            json.dump(self.data, outfile, ensure_ascii=False, indent=4)

    def _center(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class OutputShare(tk.Tk):

    def __init__(self, *args,
                 with_cover=False,
                 with_variant=False,
                 name=None,
                 share=None,
                 cover=None,
                 variant=None,
                 **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.withdraw()

        self.with_cover = with_cover
        self.with_variant = with_variant
        self.name = name
        self.share = share
        self.cover = cover
        self.variant = variant

        self.bbcode = ""
        self._make_share_bbcode()

        self.title("Liens de partage")

        # First line
        self.w1 = tk.Text(self, width=120, height=1, font=("Helvetica", 11),
                          exportselection=1)
        self.w1.insert(1.0, self.share)
        self.w1.pack(pady=10, fill=tk.BOTH, expand=1)

        # Second line
        self.w2 = tk.Text(self, width=120, height=1, font=("Helvetica", 11),
                          exportselection=1)
        self.w2.insert(1.0, self.bbcode1)
        self.w2.tag_add(SEL, "1.0", END)
        self.w2.mark_set(INSERT, "1.0")
        self.w2.see(INSERT)
        self.w2.pack(pady=10, fill="both", expand=1)

        # Third line (optional)
        if self.with_cover:
            self.w3 = tk.Text(self, width=120, height=1, font=("Helvetica", 11),  # noqa:E501
                              exportselection=1)
            self.w3.insert(1.0, self.bbcode2)
            self.w3.tag_add(SEL, "1.0", END)
            self.w3.mark_set(INSERT, "1.0")
            self.w3.see(INSERT)
            self.w3.pack(pady=10, fill="both", expand=1)

        if self.with_cover and self.with_variant:
            self.w4 = tk.Text(self, width=120, height=2, font=("Helvetica", 11),  # noqa:E501
                              exportselection=1)
            self.w4.insert(1.0, self.bbcode3)
            self.w4.tag_add(SEL, "1.0", END)
            self.w4.mark_set(INSERT, "1.0")
            self.w4.see(INSERT)
            self.w4.pack(pady=10, fill="both", expand=1)

        # 4th line :
        newbbcode = ("[rl]\n"
                     "    [case]\n"
                     "        [rlimg={},{}]\n"
                     "    [/case]\n"
                     "[/rl]")
        if self.with_cover and not self.with_variant:
            self.w5 = tk.Text(self, width=120, height=6, font=("Helvetica", 11),  # noqa:E501
                              exportselection=1)
            self.w5.insert(1.0, newbbcode.format(self.cover, self.share))
            self.w5.tag_add(SEL, "1.0", END)
            self.w5.mark_set(INSERT, "1.0")
            self.w5.see(INSERT)
            self.w5.pack(pady=10, fill="both", expand=1)

        newbbcode2 = ("[rl2]\n"
                      "    [case]\n"
                      "        [rlimg={},{}]\n"
                      "    [/case]\n"
                      "    [case]\n"
                      "        [rlimg={},{}]\n"
                      "    [/case]\n"
                      "[/rl2]")
        if self.with_cover and self.with_variant:
            self.w6 = tk.Text(self, width=120, height=10, font=("Helvetica", 11),  # noqa:E501
                              exportselection=1)
            self.w6.insert(1.0, newbbcode2.format(self.cover, self.share, self.variant, self.share))
            self.w6.tag_add(SEL, "1.0", END)
            self.w6.mark_set(INSERT, "1.0")
            self.w6.see(INSERT)
            self.w6.pack(pady=10, fill="both", expand=1)

        self._center()
        self.deiconify()

    def _make_share_bbcode(self):
        new_name = no_ext(self.name)
        self.bbcode1 = f"[url={self.share}]{new_name}[/url]"
        if self.with_cover:
            self.bbcode2 = f"[url={self.share}][img]{self.cover}[/img][/url]"  # noqa:E501
            if self.with_variant:
                self.bbcode3 = f"[url={self.share}][img]{self.cover}[/img] [img]{self.variant}[/img][/url]"  # noqa:E501

    def _center(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))


class UploadApp(tk.Tk):

    def __init__(self, *args,
                 megaclient=None, local_file=None, remote_path=None,
                 **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # self.overrideredirect(1)
        # self.wm_attributes('-type', 'splash')

        self.withdraw()

        self.local_file = sys.argv[1]

        self.megaclient = megaclient
        self.local_file = local_file
        self.basename = get_base_name(self.local_file)
        self.remote_path = remote_path

        self.mega_file = None

        # self.wm_attributes('-type', 'splash')

        self.title("Progression")

        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=400, mode="determinate")
        self.progress.pack()

        self.bytes = 0
        self.maxbytes = 0
        self._center()
        self.deiconify()
        self.upload()

    def _center(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def upload(self):
        desc = self.megaclient.mega.find_path_descriptor(self.remote_path, self.megaclient.filelist)  # noqa: E501
        self.mega_file = self._put_file_chunked(self.local_file, dest=desc)
        print("End of progressbar window")
        self.destroy()

    # This code comes from pyocclient
    # https://github.com/owncloud/pyocclient
    # and has been modified to implement progressbar
    def _put_file_chunked(self, filename, dest=None, dest_filename=None):

        # determine storage node
        if dest is None:
            # if none set, upload to cloud drive node
            if not hasattr(self.megaclient.mega, 'root_id'):
                self.megaclient.mega.get_files()
            dest = self.megaclient.mega.root_id

        # request upload url, call 'u' method
        with open(filename, 'rb') as input_file:
            file_size = os.path.getsize(filename)

            self.progress["value"] = 0
            self.maxbytes = file_size
            self.progress["maximum"] = file_size

            ul_url = self.megaclient.mega._api_request({'a': 'u', 's': file_size})['p']  # noqa: E501

            # generate random aes key (128) for file
            ul_key = [random.randint(0, 0xFFFFFFFF) for _ in range(6)]
            k_str = a32_to_str(ul_key[:4])
            count = Counter.new(
                128, initial_value=((ul_key[4] << 32) + ul_key[5]) << 64
            )
            aes = AES.new(k_str, AES.MODE_CTR, counter=count)

            upload_progress = 0
            completion_file_handle = None

            mac_str = '\0' * 16
            mac_encryptor = AES.new(k_str, AES.MODE_CBC, mac_str.encode("utf8"))  # noqa: E501
            iv_str = a32_to_str([ul_key[4], ul_key[5], ul_key[4], ul_key[5]])
            if file_size > 0:
                for chunk_start, chunk_size in get_chunks(file_size):
                    chunk = input_file.read(chunk_size)
                    upload_progress += len(chunk)

                    encryptor = AES.new(k_str, AES.MODE_CBC, iv_str)
                    for i in range(0, len(chunk) - 16, 16):
                        block = chunk[i:i + 16]
                        encryptor.encrypt(block)

                    # fix for files under 16 bytes failing
                    if file_size > 16:
                        i += 16
                    else:
                        i = 0

                    block = chunk[i:i + 16]
                    if len(block) % 16:
                        block += makebyte('\0' * (16 - len(block) % 16))
                    mac_str = mac_encryptor.encrypt(encryptor.encrypt(block))

                    # encrypt file and upload
                    chunk = aes.encrypt(chunk)
                    output_file = requests.post(
                        ul_url + "/" + str(chunk_start),
                        data=chunk,
                        timeout=self.megaclient.mega.timeout
                    )
                    completion_file_handle = output_file.text
                    logger.info(
                        '%s of %s uploaded', upload_progress, file_size
                    )

                    self.progress["value"] = upload_progress
                    self.update()

            else:
                output_file = requests.post(
                    ul_url + "/0", data='',
                    timeout=self.megaclient.mega.timeout
                )
                completion_file_handle = output_file.text

            logger.info('Chunks uploaded')
            logger.info('Setting attributes to complete upload')
            logger.info('Computing attributes')
            file_mac = str_to_a32(mac_str)

            # determine meta mac
            meta_mac = (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3])

            dest_filename = dest_filename or os.path.basename(filename)
            attribs = {'n': dest_filename}

            encrypt_attribs = base64_url_encode(
                encrypt_attr(attribs, ul_key[:4])
            )
            key = [
                ul_key[0] ^ ul_key[4], ul_key[1] ^ ul_key[5],
                ul_key[2] ^ meta_mac[0], ul_key[3] ^ meta_mac[1], ul_key[4],
                ul_key[5], meta_mac[0], meta_mac[1]
            ]
            encrypted_key = a32_to_base64(encrypt_key(key, self.megaclient.mega.master_key))  # noqa: E501
            logger.info('Sending request to update attributes')
            # update attributes
            data = self.megaclient.mega._api_request(
                {
                    'a': 'p',
                    't': dest,
                    'i': self.megaclient.mega.request_id,
                    'n': [
                        {
                            'h': completion_file_handle,
                            't': 0,
                            'a': encrypt_attribs,
                            'k': encrypted_key
                        }
                    ]
                }
            )
            logger.info('Upload complete')
            return data


# setup_logging()
# logger = logging.getLogger(__name__)
# logger.info('Startlogging:')

# MAIN PROGRAM here :

with open(config_file, encoding='utf-8') as json_file:
    data = json.load(json_file)

casim_account = data.get("Casimages")

app = AccountChoice(config=data)
app.protocol("WM_DELETE_WINDOW", app._quit)
app.mainloop()

# print("GUI has closed")

account = app.selected_account
print(f"User chose account : {account}")
# account_config = data[account]
# print(account_config)

# Instantiate MegaClient :
megaclient = MegaClient(data[account])
print("megaclient instantiated")

# MAIN PROGRAM here :
app2 = PathChoice(file_=config_file, account=account, mega=megaclient)
app2.protocol("WM_DELETE_WINDOW", app2._quit)
app2.mainloop()

# print("GUI has closed")
cloud_dir = app2.selected_cloud_dir
cover_bool = bool(app2.check_casi.get())
variant_bool = bool(app2.check_variant.get())
print(f"Choice for cover upload is   : {cover_bool}")
print(f"Choice for variant upload is : {variant_bool}")

redim_val = app2.redim.get()
print(f"Redim val is : {redim_val}")

# Checkint if not empty
if cloud_dir:
    print("********************")
    print(cloud_dir)
else:
    print("Dossier vide non valide")
    mb.askokcancel("Erreur", "Dossier vide (racine) non accepté.")
    sys.exit(1)

# # Check if cloud dir exists :
try:
    megaclient.login()
    list_dir = megaclient.ls_l(cloud_dir)
    # print("YATA !!")
except MegaException:
    print("Dossier non valide")
    mb.askokcancel("Erreur", "Dossier invalide")
    megaclient.logout()
    sys.exit(1)


# # Local file is the script argument
local_file = sys.argv[1]
# # Get file basename
if os.path.isfile(local_file):
    basename = os.path.basename(local_file)
    # print(basename)
else:
    sys.exit(1)

try:
    app = UploadApp(megaclient=megaclient,
                    local_file=local_file,
                    remote_path=cloud_dir)
    app.mainloop()
    cloud_file = app.mega_file
except Exception as e:
    print(e)


share = megaclient.share(cloud_file)
print(share)

print(casim_account)

if zipfile.is_zipfile(local_file) and cover_bool:
    print("Is zip AND with cover upload")
    cover = extract_cover(local_file)
    # print(cover)

    if casim_account:
        if casim_account.get("login") and casim_account.get("passwd"):
            casi_upload = CasimLogged(cover, resize=redim_val)
            casi_upload.login(casim_account.get("login"),
                              casim_account.get("passwd"))
            casi_upload.change_folder(casim_account.get("folder"))
        else:
            casi_upload = Casim(cover, resize=redim_val)
    else:
        casi_upload = Casim(cover, resize=redim_val)
    cover_url = casi_upload.get_link()
    os.remove(cover)

    if variant_bool:
        variant = extract_cover(local_file, index=1)
        print(variant)
        if casim_account:
            if casim_account.get("login") and casim_account.get("passwd"):
                casi_upload = CasimLogged(variant, resize=redim_val)
                casi_upload.login(casim_account.get("login"),
                                  casim_account.get("passwd"))
                casi_upload.change_folder(casim_account.get("folder"))
            else:
                casi_upload = Casim(variant, resize=redim_val)
        else:
            casi_upload = Casim(variant, resize=redim_val)
        variant_url = casi_upload.get_link()
        os.remove(variant)
        print(variant_url)
        print(f"[url={share}][img]{cover_url}[/img] [img]{variant_url}[/img][/url]")  # noqa:E501
    else:
        variant_url = None
        print(f"[url={share}][img]{cover_url}[/img][/url]")

    print("**********************************************")

    output = OutputShare(with_cover=True, with_variant=variant_bool,
                         name=basename, share=share, cover=cover_url,
                         variant=variant_url)
    output.mainloop()

else:
    print("No cover upload (or no zip)")
    print("**********************************************")
    print(share)
    print(f"[url={share}]{no_ext(basename)}[/url]")
    print("**********************************************")
    # output = OutputShare(with_cover=False, name=basename, share=share)
    output = OutputShare(name=basename, share=share)
    output.mainloop()
