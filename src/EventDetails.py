# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from time import strftime, localtime
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Components.config import config
from enigma import eServiceReference
# from StreamPlayer import StreamPlayer
from .Debug import logger
from .ServiceUtils import getPicon
from .__init__ import _
from .Picture import Picture
from .CockpitPlayer import CockpitPlayer
from .Index import idx
from .SkinUtils import getSkinPath
from .FileUtils import readFile


class EventDetails(Screen, Picture):
    skin = readFile(getSkinPath("EventDetails.xml"))

    def __init__(self, session, date_str, event, service_ref, channel_id):
        logger.info("...")
        self.temp_dir = os.path.join(
            config.plugins.tvmagazinecockpit.temp_dir.value, date_str)
        Picture.__init__(self, self.temp_dir)
        self.event = event
        self.channel_id = channel_id
        self.service_ref = service_ref
        self.video_url = self.event[idx["video_url"]]
        Screen.__init__(self, session)
        self["description"] = ScrollLabel()
        self["actions"] = ActionMap(
            ["TVC_Actions"],
            {
                "ok": self.key_ok,
                "yellow": self.key_ok,
                "cancel": self.close,
                "red": self.close,
                "up": self["description"].pageUp,
                "left": self["description"].pageUp,
                "down": self["description"].pageDown,
                "right": self["description"].pageDown
            },
            -2
        )

        self['key_red'] = Label(_("Back"))
        self['key_green'] = Label()
        self["key_yellow"] = Label(_("Trailer"))
        if not self.video_url:
            self["key_yellow"].setText((""))
            self["key_yellow"].hide()
        self['key_blue'] = Label()

        self["programpix"] = Pixmap()
        self["videopix"] = Pixmap()
        self["picon"] = Pixmap()

        self["title"] = Label()
        self["subtitle"] = Label()
        self["duration"] = Label()

        self.onLayoutFinish.append(self._init)

    def _init(self):
        """Initialize the UI with event data"""
        self.setTitle(_("Event Details"))
        self._populate_event_information()
        self._setup_images()

    def _populate_event_information(self):
        """Populate event information in the UI"""
        logger.info("...")
        # logger.debug("event: %s", self.event)
        year = self.event[idx["year"]]
        title = self.event[idx["title"]]
        if year:
            title += f" ({year})"
        self["title"].setText(title)
        self["subtitle"].setText(self.event[idx["subtitle"]])
        start_time = strftime("%H:%M", localtime(self.event[idx["startTime"]]))
        self["duration"].setText(f"{start_time}, {self.event[idx['duration']]} {_('min')}")
        self["picon"].setPixmap(getPicon(self.service_ref))
        self["description"].setText(self.event[idx["description"]])

    def _setup_images(self):
        """Setup and display images for the event"""
        logger.info("...")
        url = self.event[idx["photo_url"]]
        time = self.event[idx["startTime"]]
        if url:
            ident = f"{time}-{self.channel_id}"
            self.showPicture(self["programpix"], "programpix-", ident, url)

    def key_ok(self):
        logger.info("...")
        if self.video_url and self.video_url.endswith(("mp4")):
            sref = eServiceReference(
                eServiceReference.idServiceMP3, 0, self.video_url)
            sref.setName(self.event[idx["title"]] + "-Trailer")
            self.session.open(CockpitPlayer, sref)
