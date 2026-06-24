# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from twisted.internet import threads, reactor
from enigma import ePicLoad, gPixmapPtr
from Components.AVSwitch import AVSwitch
from Tools.BoundFunction import boundFunction
from .Debug import logger
from .WebRequests import WebRequests


class Picture(WebRequests):
    def __init__(self, temp_dir):
        WebRequests.__init__(self)
        self.temp_dir = temp_dir
        self.sc = AVSwitch().getFramebufferScale()
        self.picload_cache = {}
        self.picload_conn_cache = {}

    def showPicture(self, pixmap, atype, ident, url):
        logger.info("atype: %s, ident: %s, url: %s", atype, ident, url)
        path = os.path.join(self.temp_dir, atype + str(ident) + ".jpg")
        if url and not url.endswith("None") and not os.path.isfile(path):
            threads.deferToThread(self.downloadPicture,
                                  pixmap, url, path, self.displayPicture)
        else:
            self.displayPicture(pixmap, path)

    def downloadPicture(self, pixmap, url, path, callback):
        logger.info("path: %s", path)
        self.downloadFile(url, path)
        logger.debug("downloaded: %s", path)
        reactor.callFromThread(callback, pixmap, path)

    def displayPicture(self, pixmap, path):
        logger.info("path: %s", path)
        if os.path.isfile(path):
            if path not in self.picload_cache:
                self.picload_cache[path] = ePicLoad()
            picload = self.picload_cache[path]
            if path not in self.picload_conn_cache:
                picload.PictureData.get().append(boundFunction(self.onPictureReady, path, pixmap))
                self.picload_conn_cache[path] = True
            picload.setPara(
                (
                    pixmap.instance.size().width(),
                    pixmap.instance.size().height(),
                    self.sc[0], self.sc[1],
                    False,
                    1,
                    "#ff000000"
                )
            )
            picload.startDecode(path)  # Asynchronous call
        else:
            logger.error("pixmap not found: %s", path)
            pixmap.instance.setPixmap(gPixmapPtr())

    def onPictureReady(self, path, pixmap, _picInfo=""):
        logger.info("...")
        ptr = self.picload_cache[path].getData()
        if ptr is not None:
            pixmap.instance.setPixmap(ptr)
        else:
            pixmap.instance.setPixmap(gPixmapPtr())
        self.picload_cache.pop(path, None)
        self.picload_conn_cache.pop(path, None)
