#!/usr/bin/python3
# -*-coding:utf-8 -*-

import tkinter as tk
from tkinter import END


class AccountChoice(tk.Tk):

    def __init__(self, *args, config=None, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.withdraw()

        self.title("Choix du compte Mega")
        self.conf = config

        self.selected_account = ""

        # self._print_list()

        self.accounts_list = self.conf.keys()

        # One frame for lisbox and scrollbar
        self.frame = tk.Frame(self)

        self.lb = tk.Listbox(self.frame, width=60, height=12,
                             font=("Helvetica", 12))
        [self.lb.insert(END, item) for item in self.accounts_list]

        self.frame.pack(fill="both", expand=1)

        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.lb.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.lb.config(yscrollcommand=self.scrollbar.set)
        self.lb.pack(side="left", fill="both", expand=1)
        self.lb.bind('<Double-Button-1>', self.double_click)

        self._center()
        self.deiconify()

    def _print_list(self):
        for a in self.conf.keys():
            print(a)

    def double_click(self, event):
        widget = event.widget
        selection = widget.curselection()
        self.selected_account = widget.get(selection[0])
        self._quit()

    def _quit(self):
        self.destroy()
        print("end of Account Choice")

    def _center(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
