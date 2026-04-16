# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Components.UsageConfig import preferredTimerPath
from RecordTimer import RecordTimerEntry
from Screens.TimerEdit import TimerSanityConflict
from Screens.TimerEntry import TimerEntry
from Screens.ChoiceBox import ChoiceBox
from enigma import eServiceReference
from ServiceReference import ServiceReference
from .__init__ import _
from .Debug import logger
from .Version import PLUGIN
from .ZapUtils import zapService
from .PluginUtils import getPlugin, WHERE_MEDIATHEK_SEARCH, WHERE_TMDB_MOVIELIST
from .ServiceUtils import getService
from .Index import idx


class More():
    def __init__(self, session):
        logger.info("...")
        self.session = session
        self.mediathek_plugin = getPlugin(WHERE_MEDIATHEK_SEARCH)
        self.tmdb_plugin = getPlugin(WHERE_TMDB_MOVIELIST)

    def openMore(self, service, event):
        logger.info("service: %s", service)
        logger.info("event: %s", event)
        if event:
            self._service = service
            self._event = event
            alist = [
                (_("Zap"), "zap"),
                (_("Add Timer"), "timer"),
            ]
            if self.mediathek_plugin:
                alist.append(
                    (self.mediathek_plugin.description, "mediathek_search"))
            if self.tmdb_plugin:
                alist.append((self.tmdb_plugin.description, "tmdb_search"))

            self.session.openWithCallback(
                self.openMoreCallback,
                ChoiceBox,
                title=PLUGIN,
                list=alist,
            )

    def openMoreCallback(self, answer=None):
        logger.info("...")
        if answer:
            action = answer[1]
            if action == "zap":
                zapService(self._service)
                self.close()  # pylint: disable=no-member
            elif action == "timer":
                serviceref = ServiceReference(eServiceReference(self._service))
                begin = self._event[idx["startTime"]] - \
                    config.recording.margin_before.value * 60
                end = self._event[idx["endTime"]] + \
                    config.recording.margin_after.value * 60
                eventdata = (
                    begin, end, self._event[idx["title"]], self._event[idx["subtitle"]], None)
                newEntry = RecordTimerEntry(
                    serviceref, checkOldTimers=True, dirname=preferredTimerPath(), *eventdata)
                self.session.openWithCallback(
                    self.finishedAdd, TimerEntry, newEntry)
            elif action == "mediathek_search":
                self.mediathek_plugin(self.session, self._event[idx["title"]])
            elif action == "tmdb_search":
                service = getService("", self._event[idx["title"]])
                self.tmdb_plugin(self.session, service)

    def finishedAdd(self, answer):
        logger.info("...")
        if answer[0]:
            entry = answer[1]
            # Handle timer conflicts by adjusting end times when possible
            simulTimerList = self.session.nav.RecordTimer.record(entry)
            if simulTimerList is not None:
                for x in simulTimerList:
                    if x.setAutoincreaseEnd(entry):
                        self.session.nav.RecordTimer.timeChanged(x)
                # Try recording again after adjustments
                simulTimerList = self.session.nav.RecordTimer.record(entry)
                if simulTimerList is not None:
                    # If conflicts still exist, show conflict resolution dialog
                    self.session.openWithCallback(
                        self.finishedAdd, TimerSanityConflict, simulTimerList)
        else:
            logger.debug("Timeredit aborted")
