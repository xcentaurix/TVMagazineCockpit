# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from time import time, strftime, localtime
from Components.config import config
from .ChannelUtils import readChannelDict, readChannelList
from .TVMagazineData import TVMagazineData
from .FileUtils import createDirectory, deleteDirectory
from .WebRequests import WebRequests
from .Index import idx
from .DateTimeUtils import timestamp_to_day_int
from .EventUtils import find_time_event_index
from .Debug import logger


class Cache:
    def __init__(self):
        logger.info("...")
        self.events = {}
        self.channel_dict = readChannelDict()
        self.channel_list = readChannelList(self.channel_dict)
        self.date_str = strftime("%Y-%m-%d", localtime(int(time())))
        self.tvmagazine_data = TVMagazineData(self.channel_dict)
        self.temp_dir = os.path.join(
            config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)
        self.cache_path = os.path.join(self.temp_dir, "events.json")
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
        createDirectory(self.temp_dir)

    def downloadEvents(self):
        if not os.path.exists(self.cache_path):
            logger.debug("channel_list: %s", self.channel_list)
            self.tvmagazine_data.downloadEvents(
                self.date_str,
                self.channel_list,
                self.events,
                self.downloadEventsCallback
            )

    def downloadEventsCallback(self, events):
        logger.info("events: %s", events)
        start_time = timestamp_to_day_int(time()) + 20 * 3600 + 15 * 60

        events_of_the_day = events.get(self.date_str, {})
        for service_ref in events_of_the_day:
            channel_id = self.channel_dict.get(
                service_ref, {}).get(self.data_source_id, "")
            event_list = events_of_the_day.get(service_ref, {})
            i = find_time_event_index(event_list, start_time)
            if i != -1:
                event = event_list[i]
                event = self.tvmagazine_data.getDetailedEvent(event)
                if event:
                    url = event[idx["photo_url"]]
                    ident = f"{event[idx['startTime']]}-{channel_id}"
                    path = os.path.join(
                        self.temp_dir, "programpix-" + ident + ".jpg")
                    WebRequests().downloadFile(url, path)

    def cleanup(self):
        logger.info("Cleaning up old cache directories...")
        adir = os.path.dirname(self.temp_dir)
        for name in os.listdir(adir):
            path = os.path.join(adir, name)
            if os.path.isdir(path) and name != self.date_str:
                deleteDirectory(path)
