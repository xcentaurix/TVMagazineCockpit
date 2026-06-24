# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from time import strftime, localtime
from enigma import gPixmapPtr
from Components.config import config
from .Debug import logger
from .ServiceUtils import getPicon
from .ConfigInit import ROWS
from .Index import idx
from .EventUtils import find_time_event_index


class Column:
    """Class handling TV channel display and events formatting."""

    def __init__(self, parent):
        """
        Initialize Column class with reference to parent TVMagazineCockpit instance.

        Args:
            parent: Parent TVMagazineCockpit instance for UI access
        """
        self.parent = parent
        self.navigation = self.parent.navigation

    def showColumn(self, event_list, service_ref, channel):
        """
        Display events for a specific channel in its designated column.

        Args:
            event_list (list): List of events for the channel
            service_ref (str): Service reference identifier for the channel
            channel (dict): Channel information dictionary
        """

        i = self.parent.page_channel_list.index(service_ref)
        logger.info("Processing channel column: %s", i)
        # debug("event_list: %s", event_list)

        self.parent.list_columns[i] = event_list

        if self.parent.prime_event_indices[i] == -1:
            prime_event_index = find_time_event_index(
                event_list, self.parent.navigation.getTimestamp("20:15"))
            self.parent.prime_event_indices[i] = prime_event_index
            if prime_event_index != -1:
                self.showPrimeEvent(
                    i, event_list[prime_event_index], service_ref, channel)
            else:
                self.showPrimeEvent(i, {}, service_ref, channel)

        current_event_index = find_time_event_index(
            event_list, self.parent.timestamp)
        self.parent.list_indices[i] = current_event_index
        # Extract a subset of events around the current index
        sub_list = []
        if event_list:
            sub_list = event_list[max(
                0, current_event_index - 1):current_event_index - 1 + ROWS]
        # Pad the list to ensure it has ROWS number of items
        while len(sub_list) < ROWS:
            sub_list.append((" ", " ", " ", " ", 0))
        # setBuildFunc requires each entry to be a tuple
        sub_list = [tuple(entry) if not isinstance(entry, tuple) else entry for entry in sub_list]

        self.parent[f"list{i}"].l.setList(sub_list)
        self.parent[f"list{i}"].moveToIndex(
            1)  # Position at the current event

    def showPrimeEvent(self, i, event, service_ref, channel):
        """Display prime time event information and thumbnail."""
        logger.info("Prime event: %s", event)
        if event:
            data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
            channel_id = channel[data_source_id]
            self.parent[f"channel{i}"].setText(channel["name"])
            self.parent[f"time{i}"].setText(
                strftime("%H:%M", localtime(event[idx["startTime"]])))
            self.parent[f"description{i}"].setText(event[idx["title"]])
            self.parent[f"picon{i}"].instance.setPixmap(
                getPicon(service_ref))

            detailed_event = self.parent.tvmagazine_data.getDetailedEvent(
                event)
            url = detailed_event[idx["photo_url"]]
            start_time = event[idx["startTime"]]
            if url:
                ident = f"{start_time}-{channel_id}"
                self.parent.showPicture(
                    self.parent[f"programpix{i}"], "programpix-", ident, url)
        else:
            self.parent[f"channel{i}"].setText("")
            self.parent[f"time{i}"].setText("")
            self.parent[f"description{i}"].setText("")
            self.parent[f"picon{i}"].instance.setPixmap(gPixmapPtr())
            self.parent[f"list{i}"].l.setList([])
            self.parent[f"programpix{i}"].instance.setPixmap(gPixmapPtr())
