# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from .Debug import logger
from .TVFAData import TVFAData
from .TVMData import TVMData
from .TVSData import TVSData


class TVMagazineData():
    def __init__(self, channel_dict):
        self.channel_dict = channel_dict
        self.data_sources = {
            "tvfa": TVFAData,
            "tvm": TVMData,
            "tvs": TVSData
        }

    def downloadEvents(self, day, page_channel_list, events, callback):
        logger.info("page_channel_id_list: %s, day: %s",
                    page_channel_list, day)
        tv_data_mgr = self.data_sources[config.plugins.tvmagazinecockpit.data_source.value](
            self.channel_dict)
        tv_data_mgr.downloadEvents(day, page_channel_list, events, callback)

    def getDetailedEvent(self, event):
        if config.plugins.tvmagazinecockpit.data_source.value == "tvs":
            tv_data_mgr = self.data_sources[config.plugins.tvmagazinecockpit.data_source.value](
                self.channel_dict)
            event = tv_data_mgr.getDetailedEvent(event)
        return event
