# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from .Debug import logger
from .ConfigInit import COLS
from .__init__ import _


class Page:
    """Class handling page display and management for TV Magazine Cockpit."""

    def __init__(self, parent):
        """
        Initialize Page class with reference to parent TVMagazineCockpit instance.

        Args:
            parent: Parent TVMagazineCockpit instance for UI access
        """
        self.parent = parent
        self.navigation = self.parent.navigation

    def showPage(self, events=None):
        """
        Display the current page of TV channels.

        Args:
            events (dict, optional): Optional events data to update
        """
        logger.info("...")
        if events is not None:
            self.parent.events = events

        logger.debug("self.events: %s", self.parent.events.get(
            self.navigation.date_str, {}).keys())
        logger.debug("self.channel_list: %s", self.parent.channel_list)

        missing_channels_list = []
        logger.info("self.events: %s", self.parent.events)

        # Calculate page range
        start = self.navigation.page_index * COLS
        stop = min(start + COLS, len(self.parent.channel_list))
        self.parent.page_channel_list = self.parent.channel_list[start:stop]

        logger.debug("page_channel_list: %s", self.parent.page_channel_list)

        # Process each channel in the current page
        for i, service_ref in enumerate(self.parent.page_channel_list):
            channel = self.parent.channel_dict.get(service_ref, {})
            if channel:
                logger.debug("channel: %s", channel)
                self.parent[f"channel{i}"].setText(channel["name"])
                column_events = self.parent.events.get(
                    self.navigation.date_str, {}).get(service_ref, {})
                if column_events:
                    logger.debug("data already available")
                    self.parent.showColumn(column_events, service_ref, channel)
                    # Set selection on first column if this is first load
                    if i == 0 and self.parent.first:
                        self.parent.first = False
                        self.parent["list0"].setSelectionEnable(True)
                else:
                    logger.debug("need to download data")
                    missing_channels_list.append(service_ref)
                    self.parent.showColumn(column_events, service_ref, channel)
        i = len(self.parent.page_channel_list)
        while i < COLS:
            self.parent.clearColumn(i)
            i += 1

        # Handle missing events
        logger.debug("missing_channels_list: %s", missing_channels_list)
        if len(missing_channels_list) == len(self.parent.page_channel_list):
            if events is None:
                self.parent.tvmagazine_data.downloadEvents(
                    self.navigation.date_str,
                    missing_channels_list,
                    self.parent.events,
                    self.showPage
                )
                title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet} - {_('Loading...')}"
            else:
                title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet} - {_('No event data available')}"
        else:
            title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet}, {_('Page')}: {self.navigation.page_index + 1}/{self.navigation.pages}, {_('Services')}: {len(self.parent.channel_list)}"

        self.parent.setTitle(title)
