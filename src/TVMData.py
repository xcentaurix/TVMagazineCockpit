# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
from time import strftime, localtime
from twisted.internet import threads, reactor
from .Debug import logger
from .WebRequests import WebRequests
from .DateTimeUtils import iso_to_epoch
from .Index import idx
from .CacheUtils import saveEvents


EPG_SEARCH_URL = "https://proxy.xceler8.io/v2/epg-search"
IMAGE_BASE_URL = "https://images.tvmovie.de"


class TVMData(WebRequests):
    def __init__(self, channel_dict):
        WebRequests.__init__(self)
        self.channel_dict = channel_dict

    def buildImageUrl(self, image):
        """Build image URL from the image object returned by the API."""
        if not image:
            return ""
        seo_name = image.get('seoName', '')
        image_id = image.get('imageId', '')
        if seo_name and image_id:
            return f"{IMAGE_BASE_URL}/{seo_name},id={image_id},b=tvmovie,w=640,rm=sk.jpeg"
        return ""

    def parseEvent(self, broadcast):
        logger.debug("parseEvent: %s", broadcast)
        # Format datetime strings to epoch timestamps
        start_time = iso_to_epoch(broadcast.get('airTime'))
        end_time = iso_to_epoch(broadcast.get('airTimeEnd'))

        # Get image URL if available
        photo_url = self.buildImageUrl(broadcast.get('image'))

        # Get country of production
        countries = broadcast.get('countriesOfProduction', [])
        country = ", ".join(countries) if countries else ""

        startHM = strftime("%H:%M", localtime(start_time))

        # Build formatted event object
        formatted_event = [None] * (len(idx) + 1)

        formatted_event[idx['startHM']] = startHM
        formatted_event[idx['title']] = broadcast.get('title', '')
        formatted_event[idx['subtitle']] = broadcast.get('subTitle', '')
        formatted_event[idx['year']] = str(broadcast.get('productionYear', ''))
        formatted_event[idx['startTime']] = start_time
        formatted_event[idx['country']] = country
        formatted_event[idx['category']] = broadcast.get('categoryName', '')
        formatted_event[idx['genre']] = broadcast.get('genreName', '')
        formatted_event[idx['endTime']] = end_time
        formatted_event[idx['duration']] = broadcast.get('runtime', 0)
        formatted_event[idx['channel']] = ""
        formatted_event[idx['urlsendung']] = "https://www.tvmovie.de" + broadcast.get('url', '')
        formatted_event[idx['has_video']] = broadcast.get('hasAutoPlay', False)
        formatted_event[idx['photo_url']] = photo_url
        formatted_event[idx['description']] = ""
        formatted_event[idx['video_url']] = ""

        return formatted_event

    def downloadEvents(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_id_list: %s, day: %s",
                    page_channel_list, day)
        threads.deferToThread(self.downloading, day,
                              page_channel_list, all_events, callback)

    def downloading(self, day, page_channel_list, all_events, callback):
        logger.info("page_channel_list: %s, day: %s", page_channel_list, day)
        if day not in all_events:
            all_events[day] = {}

        referer_headers = {"Referer": "https://www.tvmovie.de/"}
        air_time = f"{day}T04:00:00.000Z"

        for service_ref in page_channel_list:
            channel_id = self.channel_dict.get(
                service_ref, {}).get("tvm_id", "")
            if not channel_id:
                logger.info("no tvm_id for: %s", service_ref)
                continue

            url = f"{EPG_SEARCH_URL}?channelId={channel_id}&airTime={air_time}&limit=50"
            logger.debug("url: %s", url)
            result = self.getContent(url, headers=referer_headers)
            logger.debug("result length: %s", len(result) if result else 0)
            if result:
                try:
                    results = json.loads(result).get('results', [])
                except Exception as e:
                    logger.error("JSON parse error: %s", e)
                    continue
                if service_ref not in all_events[day]:
                    all_events[day][service_ref] = []
                for entry in results:
                    broadcasts = entry.get('broadcasts', [])
                    for event in broadcasts:
                        logger.debug("event: %s", event)
                        parsed_event = self.parseEvent(event)
                        if parsed_event:
                            all_events[day][service_ref].append(parsed_event)
        saveEvents(all_events)
        reactor.callFromThread(callback, all_events)
