# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from twisted.internet import threads, reactor
from .WebRequests import WebRequests
from .TVSUtils import tvs_parse, tvs_parse_details
from .Index import idx
from .Debug import logger
from .CacheUtils import saveEvents


class TVSData(WebRequests):
    def __init__(self, channel_dict):
        WebRequests.__init__(self)
        self.channel_dict = channel_dict

    def getDetailedEvent(self, event):
        logger.info("getDetailedEvent: %s", event)
        url = event[idx["urlsendung"]]
        logger.info("url: %s", url)
        if url:
            content = self.getContent(url)
            event = tvs_parse_details(content, event)
        return event

    def downloadEvents(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        threads.deferToThread(self.downloading, day,
                              page_channel_list, all_events, callback)

    def downloading(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        if day not in all_events:
            all_events[day] = {}

        for service_ref in page_channel_list:
            channel = self.channel_dict.get(service_ref, {})
            channel_id = channel.get("tvs_id", "")
            if service_ref not in all_events[day]:
                all_events[day][service_ref] = []
            for page in (1, 2):
                url = f'https://www.tvspielfilm.de/tv-programm/sendungen/?channel={channel_id}&date={day}&page={page}'
                logger.debug("tvs url channel: %s", url)
                result = self.getContent(url)
                # logger.info("result: %s", result)
                if result:
                    events = tvs_parse(result)
                    logger.debug("events: %s", events)
                    all_events[day][service_ref] += events
        # logger.debug("all_events: %s", all_events)
        saveEvents(all_events)
        logger.debug("callback: %s", callback)
        reactor.callFromThread(callback, all_events)
