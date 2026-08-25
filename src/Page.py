# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


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
        logger.debug("self.events: %s", self.parent.events)

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
                self.parent.showColumnWidgets(i)
                self.parent[f"channel{i}"].setText(channel["name"])
                column_events = self.parent.events.get(
                    self.navigation.date_str, {}).get(service_ref, {})
                if column_events:
                    logger.debug("data already available")
                    self.parent.showColumn(column_events, service_ref, channel)
                else:
                    logger.debug("need to download data")
                    missing_channels_list.append(service_ref)
                    self.parent.showColumn(column_events, service_ref, channel)
            else:
                logger.debug("service_ref not in channel_dict: %s", service_ref)
                self.parent.clearColumn(i)
        i = len(self.parent.page_channel_list)
        while i < COLS:
            self.parent.clearColumn(i)
            i += 1

        # Each column's setList() resets its selection to the skin template's
        # default (disabled - see screenpart_EventCell.xmlinc), so the active
        # column's highlight has to be re-applied every time the page content
        # is refreshed, not just once on first load.
        self.parent[f"list{self.navigation.list_index}"].setSelectionEnable(True)

        # Handle missing events. Only kick off a download on the first pass
        # through this page (events is None) - once the download callback
        # re-enters showPage() with the merged results, whatever is still
        # missing genuinely has no data and must not re-trigger another
        # download, or a channel with no data on the source would loop
        # forever instead of settling on "no data available".
        logger.debug("missing_channels_list: %s", missing_channels_list)
        if missing_channels_list and events is None:
            self.parent.tvmagazine_data.downloadEvents(
                self.navigation.date_str,
                missing_channels_list,
                self.parent.events,
                self.showPage
            )
            title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet} - {_('Loading...')}"
        elif missing_channels_list and len(missing_channels_list) == len(self.parent.page_channel_list):
            title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet} - {_('No event data available')}"
        else:
            title = f"{self.parent.data_source} - {_('Bouquet')}: {self.parent.bouquet}, {_('Page')}: {self.navigation.page_index + 1}/{self.navigation.pages}, {_('Services')}: {len(self.parent.channel_list)}"

        self.parent.setTitle(title)
