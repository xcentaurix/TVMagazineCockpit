# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import json
from enigma import eServiceCenter, eServiceReference
from Screens.ChannelSelection import service_types_tv
from Screens.InfoBar import InfoBar
from Components.config import config
from .ChannelListUtils import getServiceList
from .ConfigInit import plugindir, configdir
from .Debug import logger
from .__init__ import _


def getCurrentBouquet():
    last_root = config.tv.lastroot.value.split(";")
    bouquet = last_root[-2]
    logger.debug("bouquet: %s", bouquet)
    return bouquet


def getCurrentBouquetName(session):
    logger.info("...")
    bouquet_name = _("Unknown")
    service = session.nav.getCurrentlyPlayingServiceReference()
    if service:
        allservice = eServiceReference(f"{service_types_tv} ORDER BY name")
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
                if (currlist is not None) and (service.toString() in currlist.getContent("S", True)):
                    # Get the bouquet name
                    info = serviceHandler.info(bouquet)
                    if info:
                        bouquet_name = info.getName(bouquet)
                    break
        logger.debug("Found service in bouquet: %s", bouquet_name)
    return bouquet_name


def getBouquetServices(bouquet, channel_dict):
    # Get the list of services (channels) in the bouquet
    service_list = getServiceList(bouquet)
    services = []
    for service, _name in service_list:
        channel = channel_dict.get(service, {})
        if "::" not in service and config.plugins.tvmagazinecockpit.data_source.value + "_id" in channel:
            services.append(service)
    logger.debug("services: %s", services)
    return services


def readChannelList(channel_dict):
    services = getBouquetServices(getCurrentBouquet(), channel_dict)
    return services


def readChannelDict():
    logger.info("...")
    channel_dict = {}
    channel_dict_filename = "tvc_channel_dict.json"
    dirs = [configdir, plugindir]
    for adir in dirs:
        path = os.path.join(adir, channel_dict_filename)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as data_file:
                channel_dict = json.load(data_file)
            break
    # logger.debug("channel_dict: %s", channel_dict)
    return channel_dict
