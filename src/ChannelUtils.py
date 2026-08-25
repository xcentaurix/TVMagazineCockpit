# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
import json
from enigma import eServiceCenter, eServiceReference
from Screens.ChannelSelection import service_types_tv
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
    configured_bouquet = config.plugins.tvmagazinecockpit.bouquet.value
    if configured_bouquet:
        bouquet_ref = eServiceReference(configured_bouquet)
        info = eServiceCenter.getInstance().info(bouquet_ref)
        if info:
            return info.getName(bouquet_ref)
    bouquet_name = _("Unknown")
    service = session.nav.getCurrentlyPlayingServiceReference()
    if service:
        allservice = eServiceReference(f"{service_types_tv} ORDER BY name")
        serviceHandler = eServiceCenter.getInstance()
        # Built directly (matching ChannelSelection.recallBouquetMode()) rather than read from
        # InfoBar.instance.servicelist.bouquet_root, which reflects whatever bouquet the channel
        # list UI last happened to be navigated to in this session - before that ever happens
        # (e.g. the first time this runs after a restart) it can point at the wrong root and
        # resolve the current service to whichever bouquet the search reaches first, such as an
        # auto-created "Last scanned" bouquet, instead of the user's real one.
        if config.usage.multibouquet.value:
            bouquet_root = eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet')
        else:
            bouquet_root = eServiceReference(f'{service_types_tv} FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet')
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
    data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
    for service, _name in service_list:
        channel = channel_dict.get(service, {})
        if "::" not in service and channel.get("name") and channel.get(data_source_id):
            services.append(service)
    logger.debug("services: %s", services)
    return services


def readChannelList(channel_dict):
    bouquet = config.plugins.tvmagazinecockpit.bouquet.value or getCurrentBouquet()
    services = getBouquetServices(bouquet, channel_dict)
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
