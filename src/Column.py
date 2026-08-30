# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from time import strftime, localtime
from enigma import eTimer, gPixmapPtr
from Components.config import config
from .Debug import logger
from .ServiceUtils import getPicon
from .ConfigInit import ROWS
from .Index import idx
from .EventUtils import find_time_event_index
from .__init__ import _


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
        # Async detail fetches can resolve in a rapid burst (many rows at
        # once) - calling setList() on the eListbox widget that often, that
        # fast, crashed enigma2 in eListboxPythonMultiContent::paint(), so
        # resolved columns are coalesced and applied via a single setList()
        # per short window instead of one per resolved event.
        self.pending_refresh_columns = set()
        self.refresh_timer = eTimer()
        self.refresh_timer.callback.append(self.flushPendingRefresh)

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

        current_event_index = find_time_event_index(
            event_list, self.parent.timestamp)
        self.parent.list_indices[i] = current_event_index
        start = max(0, current_event_index - 1)
        stop = current_event_index - 1 + ROWS

        # Kick off async detail fetches (incl. the NEU flag, idx['is_new'])
        # for every event about to be shown - is_new stays None until
        # resolved, so an event already seen isn't re-fetched, and the
        # screen updates incrementally as each fetch completes rather than
        # blocking here.
        for j in range(start, min(stop, len(event_list))):
            self.resolveEventDetails(event_list, j, service_ref)

        if self.parent.prime_event_indices[i] == -1:
            prime_event_index = find_time_event_index(
                event_list, self.parent.navigation.getTimestamp("20:15"))
            self.parent.prime_event_indices[i] = prime_event_index
            if prime_event_index != -1:
                self.resolveEventDetails(
                    event_list, prime_event_index, service_ref)
                self.showPrimeEvent(
                    i, event_list[prime_event_index], service_ref, channel)
            else:
                self.showPrimeEvent(i, {}, service_ref, channel)

        self.updateEventList(service_ref, event_list, start, stop)

    def resolveEventDetails(self, event_list, j, service_ref):
        """Kick off an async detail fetch for event_list[j] unless it's
        already resolved or already has a fetch in flight."""
        event = event_list[j]
        if event[idx['is_new']] is not None:
            return
        url = event[idx['urlsendung']]
        if not url or url in self.parent.pending_detail_fetches:
            return
        self.parent.pending_detail_fetches.add(url)
        self.parent.tvmagazine_data.getDetailedEventAsync(
            event,
            lambda detailed_event: self.onEventDetailsResolved(
                event_list, j, url, detailed_event, service_ref)
        )

    def onEventDetailsResolved(self, event_list, j, url, detailed_event, service_ref):
        """Runs on the GUI thread once an async detail fetch completes."""
        if self.parent is None:
            return  # screen was closed before this fetch resolved
        self.parent.pending_detail_fetches.discard(url)
        if j >= len(event_list) or event_list[j][idx['urlsendung']] != url:
            return
        event_list[j] = detailed_event

        if service_ref not in self.parent.page_channel_list:
            return  # navigated away from this channel/page in the meantime
        i = self.parent.page_channel_list.index(service_ref)
        if self.parent.list_columns[i] is not event_list:
            return  # this column now shows different content

        if j == self.parent.prime_event_indices[i]:
            channel = self.parent.channel_dict.get(service_ref, {})
            self.showPrimeEvent(i, detailed_event, service_ref, channel)

        current_event_index = self.parent.list_indices[i]
        start = max(0, current_event_index - 1)
        stop = current_event_index - 1 + ROWS
        if start <= j < stop:
            self.pending_refresh_columns.add(i)
            # A fixed window from the first pending event, not reset on each
            # new one - guarantees the flush actually fires even if
            # resolutions keep arriving less than 150ms apart.
            if not self.refresh_timer.isActive():
                self.refresh_timer.start(150, True)

    def cancelPendingRefresh(self):
        """Stop waiting on in-flight async detail fetches and drop the
        parent reference. Called from TVMagazineCockpit.__onClose__ so
        fetches that resolve after the screen closes become no-ops in
        onEventDetailsResolved instead of touching a torn-down screen."""
        self.refresh_timer.stop()
        self.pending_refresh_columns.clear()
        self.parent = None

    def flushPendingRefresh(self):
        """Applies all columns' setList() updates coalesced since the last
        flush, instead of one setList() call per resolved event."""
        if self.parent is None:
            return
        for i in self.pending_refresh_columns:
            if i >= len(self.parent.page_channel_list):
                continue
            service_ref = self.parent.page_channel_list[i]
            event_list = self.parent.list_columns[i]
            if not event_list:
                continue
            current_event_index = self.parent.list_indices[i]
            start = max(0, current_event_index - 1)
            stop = current_event_index - 1 + ROWS
            self.updateEventList(service_ref, event_list, start, stop)
        self.pending_refresh_columns.clear()

    def updateEventList(self, service_ref, event_list, start, stop):
        i = self.parent.page_channel_list.index(service_ref)
        # Extract a subset of events around the current index
        sub_list = []
        if event_list:
            sub_list = event_list[start:stop]
            # Pad the list to ensure it has ROWS number of items (only when there
            # are real events to pad around, e.g. near the start/end of the day -
            # a channel with no event data at all should show no rows, not ROWS
            # blank ones). Padded far enough to cover idx['is_new'] (the skin's
            # text=9 NEU badge field) too - a short tuple there previously hit
            # an out-of-range PyTuple_GetItem in eListboxPythonMultiContent's
            # C++ paint code and crashed enigma2.
            padding = (" ", " ", " ", " ", 0) + \
                (None,) * (idx['is_new'] - 5) + ("",)
            while len(sub_list) < ROWS:
                sub_list.append(padding)
        # the underlying eListboxPythonMultiContent requires each entry to be a tuple,
        # and the skin displays the is_new field as text, so the raw boolean needs
        # turning into the "NEU" badge string (or "" when absent/not new) here
        sub_list = [tuple(entry) if not isinstance(entry, tuple) else entry for entry in sub_list]
        sub_list = [
            entry[:idx['is_new']] + (_("NEU") if entry[idx['is_new']] else "",) + entry[idx['is_new'] + 1:]
            if len(entry) > idx['is_new'] else entry
            for entry in sub_list
        ]

        self.parent[f"list{i}"].setList(sub_list)
        if i == self.navigation.list_index:
            # setList() just reset this column's selection to the skin template's
            # default (disabled). Re-enable it before moveToIndex() below, so the
            # selectionChanged event that call fires happens while selection is
            # already enabled - enabling it only afterwards doesn't retroactively
            # repaint the row as selected.
            self.parent[f"list{i}"].setSelectionEnable(True)
        self.parent[f"list{i}"].moveToIndex(
            1)  # Position at the current event

    def showPrimeEvent(self, i, event, service_ref, channel):
        """Display prime time event information and thumbnail."""
        logger.info("Prime event: %s", event)
        # Channel name and picon come from the channel itself, not from the
        # prime-time event - show them even when the channel has no program
        # data for this specific time slot, rather than blanking the whole
        # column.
        self.parent[f"channel{i}"].setText(channel["name"])
        self.parent[f"picon{i}"].instance.setPixmap(getPicon(service_ref))
        if event:
            data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
            channel_id = channel[data_source_id]
            self.parent[f"time{i}"].setText(
                strftime("%H:%M", localtime(event[idx["startTime"]])))
            self.parent[f"description{i}"].setText(event[idx["title"]])

            # photo_url is only known once the async detail fetch resolves -
            # showPrimeEvent() is called again with the resolved event once
            # it arrives, so the picture just pops in a moment later
            url = event[idx["photo_url"]]
            start_time = event[idx["startTime"]]
            if url:
                ident = f"{start_time}-{channel_id}"
                self.parent.showPicture(
                    self.parent[f"programpix{i}"], "programpix-", ident, url)
        else:
            self.parent[f"time{i}"].setText("")
            self.parent[f"description{i}"].setText("")
            self.parent[f"programpix{i}"].instance.setPixmap(gPixmapPtr())
