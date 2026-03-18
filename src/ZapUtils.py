# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Screens.InfoBar import InfoBar
from Screens.ChannelSelection import service_types_tv
from enigma import eServiceCenter, eServiceReference
from .Debug import logger


def zapService(service_str):
    logger.info("service_str: %s", service_str)
    if service_str:
        service = eServiceReference(str(service_str))
        if service:
            allservice = eServiceReference(
                f"{service_types_tv} ORDER BY name")
            serviceHandler = eServiceCenter.getInstance()
            bouquet_root = InfoBar.instance.servicelist.bouquet_root
            bouquet = bouquet_root
            bouquetlist = serviceHandler.list(bouquet_root)
            if bouquetlist is not None:
                while True:
                    bouquet = bouquetlist.getNext()
                    if not bouquet.valid():
                        bouquet = allservice
                        break
                    currlist = serviceHandler.list(bouquet)
                    if (currlist is not None) and (service_str in currlist.getContent("S", True)):
                        break
            if InfoBar.instance.servicelist.getRoot() != bouquet:  # already in correct bouquet?
                InfoBar.instance.servicelist.clearPath()
                if bouquet_root != bouquet:
                    InfoBar.instance.servicelist.enterPath(bouquet_root)
                InfoBar.instance.servicelist.enterPath(bouquet)
            InfoBar.instance.servicelist.setCurrentSelection(
                service)  # select the service in servicelist
            InfoBar.instance.servicelist.zap()
