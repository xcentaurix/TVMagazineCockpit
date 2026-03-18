# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
from time import strftime, localtime
from twisted.internet import threads, reactor
from .Debug import logger
from .WebRequests import WebRequests
from .Index import idx
from .DateTimeUtils import iso_to_epoch
from .CacheUtils import saveEvents


BASE_URL = "https://tvfueralle.de"


class TVFAData(WebRequests):
    def __init__(self, channel_dict):
        WebRequests.__init__(self)
        self.channel_dict = channel_dict

    def parseEvent(self, event):
        content = event.get('content', {})
        # logger.debug("content: %s", content)
        texts = content.get('texts', {})
        # very_short_value = ""
        long_value = ""
        if isinstance(texts, dict):
            # very_short_value = texts.get('VeryShort', {}).get('value', "")
            long_value = texts.get('Long', {}).get('value', "")
        photo_url = event.get('photo', {}).get('url', '')
        if photo_url:
            photo_url = BASE_URL + photo_url
        startTime = iso_to_epoch(event.get('startTime'))
        startHM = strftime("%H:%M", localtime(startTime))

        formatted_event = [None] * (len(idx) + 1)

        formatted_event[idx['startHM']] = startHM
        formatted_event[idx['title']] = event.get('title')
        formatted_event[idx['subtitle']] = content.get('subtitle')
        formatted_event[idx['year']] = content.get('year')
        formatted_event[idx['startTime']] = startTime
        formatted_event[idx['country']] = content.get('country')
        formatted_event[idx['category']] = ""
        formatted_event[idx['genre']] = ""
        formatted_event[idx['endTime']] = iso_to_epoch(event.get('endTime'))
        formatted_event[idx['duration']] = event.get('duration') / 60
        formatted_event[idx['channel']] = ""
        formatted_event[idx['urlsendung']] = ""
        formatted_event[idx['has_video']] = False
        formatted_event[idx['photo_url']] = photo_url
        formatted_event[idx['description']] = long_value
        formatted_event[idx['video_url']] = ""

        # logger.debug("formatted_event: %s", formatted_event)
        return formatted_event

    def downloadEvents(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        threads.deferToThread(self.downloading, day,
                              page_channel_list, all_events, callback)

    def downloading(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        page_channel_id_list = []
        channel_id2service_ref = {}
        for service_ref in page_channel_list:
            channel_id = self.channel_dict.get(
                service_ref, {}).get("tvfa_id", "")
            channel_id2service_ref[channel_id] = service_ref
            page_channel_id_list.append(channel_id)

        url = f"{BASE_URL}/api/broadcasts/{day}"
        logger.debug("url: %s", url)
        result = self.getContent(url)
        # logger.info("result: %s", result)
        if result:
            events = json.loads(result).get("events", {})
            # logger.debug("events: %s", events)
            if day not in all_events:
                all_events[day] = {}
            for event in events:
                # logger.debug("event: %s", event)
                channel_id = event.get('channel', -1)
                if channel_id in page_channel_id_list:
                    service_ref = channel_id2service_ref.get(channel_id, "")
                    if service_ref not in all_events[day]:
                        all_events[day][service_ref] = []
                    parsed_event = self.parseEvent(event)
                    if parsed_event:
                        all_events[day][service_ref].append(parsed_event)
        saveEvents(all_events)
        reactor.callFromThread(callback, all_events)
