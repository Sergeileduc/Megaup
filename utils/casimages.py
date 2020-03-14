#!/usr/bin/python3
# -*-coding:utf-8 -*-

import os
import requests

from bs4 import BeautifulSoup


class Casimages():

    # CASIMAGES
    url = "https://www.casimages.com/"
    url_upload = "https://www.casimages.com/upload_ano_multi.php"
    url_casi_share = "https://www.casimages.com/codes_ano_multi.php?img={}"

    headers = {
        "Accept": "application/json",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0",  # noqa: E501
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "X-Requested-With": "XMLHttpRequest"
              }

    def __init__(self, cover, variant=None, size=640):
        self.cover = cover
        self.variant = variant
        self.size = size
        self.redim = size if size in ["640", "320", "125"] else "640"
        print(f"inside value of redim : {self.redim}")
        self.url_redim = f"https://www.casimages.com/ajax/s_ano_resize.php?dim={self.redim}"  # noqa:E501

        self.cover_id = None

        # Session (keep cookies)
        self.session = requests.Session()

        # Init for cookies
        r = self.session.get(Casimages.url)
        print(r.status_code)

        self._set_redim()

    def _set_redim(self):
        # Redim 640
        self.session.get(self.url_redim)

    def upload_cover(self):
        """Upload cover and return id."""
        with open(self.cover, 'rb') as f:
            file_ = {'Filedata': ('cover', f, 'image/jpg')}
            r = self.session.post(Casimages.url_upload,
                                  files=file_, headers=Casimages.headers)

        self.cover_id = r.text  # casimages share page ID
        # delete cover
        os.remove(self.cover)
        return self.cover_id

    def get_share_url(self):
        r = self.session.get(Casimages.url_casi_share.format(self.cover_id))
        soup = BeautifulSoup(r.text, 'html.parser')

        form_rows = soup.select("div.col-sm-9 > div.form-row")
        form_cols = form_rows[2].select("div.form-group.col-lg-6 > input")
        if self.size != "Miniature":
            self.cover_url = form_cols[1]["value"]
        else:
            self.cover_url = form_cols[0]["value"]
        return self.cover_url
