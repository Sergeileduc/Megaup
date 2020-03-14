#!/usr/bin/python3
# -*-coding:utf-8 -*-


import sys
sys.path.append('../')

from utils.casimages import Casimages

cover = "sample image.jpg"

casi_upload = Casimages(cover, size=640)
casi_upload.upload_cover()
cover_url = casi_upload.get_share_url()

print(cover_url)
