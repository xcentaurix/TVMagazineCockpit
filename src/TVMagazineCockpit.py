# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


import os
from time import time, strftime, localtime
from enigma import eTimer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.config import config
from .EventDetails import EventDetails
from .More import More
from .__init__ import _
from .EventList import EventList
from .Debug import logger
from .TVMagazineData import TVMagazineData
from .FileUtils import createDirectory, deleteDirectory
from .ChannelUtils import readChannelList, readChannelDict, getCurrentBouquetName
from .Picture import Picture
from .Column import Column
from .Navigation import Navigation
from .ConfigInit import COLS
from .Page import Page
from .ConfigInit import data_sources
from .CacheUtils import loadEvents
from .SetupScreen import SetupScreen


class TVMagazineCockpit(Screen, More, Picture):

    def __init__(self, session):
        logger.info("...")
        Screen.__init__(self, session)
        self.skinName = "TVMagazineCockpit"
        More.__init__(self, session)
        self.channel_dict = readChannelDict()
        self.channel_list = readChannelList(self.channel_dict)
        self.tvmagazine_data = TVMagazineData(self.channel_dict)
        self.date_str = strftime("%Y-%m-%d", localtime(int(time())))
        self.temp_dir = os.path.join(
            config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)
        Picture.__init__(self, self.temp_dir)
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
        self.data_source = data_sources[config.plugins.tvmagazinecockpit.data_source.value]
        self.bouquet = getCurrentBouquetName(session)

        self.events = {}
        self.list_columns = []
        self.list_indices = []
        self.page_channel_list = []
        self.prime_event_indices = []
        self.timestamp = 0
        # Tracks urlsendung values with an in-flight async detail fetch, so an
        # event isn't fetched twice if it's still visible when showColumn()
        # runs again before the first fetch completes.
        self.pending_detail_fetches = set()

        self.navigation = Navigation(self)
        self.column_handler = Column(self)
        self.page_handler = Page(self)

        self["key_red"] = Button(_("More") + " ...")
        self["key_green"] = Button(_("20:15"))
        self["key_yellow"] = Button(_("22:00"))
        self["key_blue"] = Button(_("Now"))
        # The skin binds key_menu/key_info via plain name="..." (GUIComponent
        # style, same as the Button widgets above) rather than source=/render=,
        # so these need to be Buttons too - a Source like StaticText doesn't
        # bind that way and silently fails to render.
        self["key_menu"] = Button("Menu")
        self["key_info"] = Button("Info")

        for i in range(COLS):
            self[f"list{i}"] = EventList()
            self[f"channel{i}"] = Label()
            self[f"picon{i}"] = Pixmap()
            self[f"programpix{i}"] = Pixmap()
            self[f"time{i}"] = Label()
            self[f"description{i}"] = Label()

        self["day_selector"] = Label()

        self["actions"] = ActionMap(
            ["TVC_Actions", "NumberActions"],
            {
                "0": self.reload,
                "ok": self.key_ok,
                "cancel": self.close,
                "info": self.key_ok,
                "up": self.moveUp,
                "down": self.moveDown,
                "left": self.left,
                "right": self.right,
                "next": self.key_next,
                "back": self.key_back,
                "red": self.key_red,
                "green": self.key_green,
                "yellow": self.key_yellow,
                "blue": self.key_blue,
                "menu": self.key_menu,
                "channelup": self.channelup,
                "channeldown": self.channeldown,
            },
            prio=-1
        )

        createDirectory(self.temp_dir)
        self.events = loadEvents()
        self.onClose.append(self.__onClose__)
        self.onLayoutFinish.append(self.reload)

        # The active column's selection highlight doesn't visually stick when
        # enabled as part of the initial synchronous reload()/showPage() burst
        # (six columns' setList()/moveToIndex() calls firing back-to-back with
        # no GUI idle time in between), even though the exact same call works
        # correctly moments later on a real keypress. Re-apply it once more
        # shortly after layout settles.
        self.selection_fixup_timer = eTimer()
        self.selection_fixup_timer.callback.append(self.fixupSelection)

    def showPage(self, events=None):
        """Display the current page of TV channels."""
        self.page_handler.showPage(events)

    def showColumn(self, events, service_ref, channel):
        """Display events for a specific channel in its designated column."""
        self.column_handler.showColumn(events, service_ref, channel)

    def left(self):
        self[f"list{self.navigation.list_index}"].setSelectionEnable(False)
        refresh = self.navigation.left()
        self[f"list{self.navigation.list_index}"].setSelectionEnable(True)
        if refresh:
            self.prime_event_indices = [-1] * COLS
            self.page_handler.showPage()

    def right(self):
        self[f"list{self.navigation.list_index}"].setSelectionEnable(False)
        refresh = self.navigation.right()
        self[f"list{self.navigation.list_index}"].setSelectionEnable(True)
        if refresh:
            self.prime_event_indices = [-1] * COLS  # Reset prime event indices
            self.page_handler.showPage()

    def moveUp(self):
        self.navigation.moveUp()
        self.page_handler.showPage()

    def moveDown(self):
        self.navigation.moveDown()
        self.page_handler.showPage()

    def channelup(self):
        self[f"list{self.navigation.list_index}"].setSelectionEnable(False)
        self.navigation.channelup()
        self.prime_event_indices = [-1] * COLS  # Reset prime event indices
        self[f"list{self.navigation.list_index}"].setSelectionEnable(True)
        self.page_handler.showPage()

    def channeldown(self):
        self[f"list{self.navigation.list_index}"].setSelectionEnable(False)
        self.navigation.channeldown()
        self.prime_event_indices = [-1] * COLS  # Reset prime event indices
        self[f"list{self.navigation.list_index}"].setSelectionEnable(True)
        self.page_handler.showPage()

    def key_next(self):
        self.navigation.key_next()
        self.reload()

    def key_back(self):
        self.navigation.key_back()
        self.reload()

    def key_ok(self):
        logger.info("...")
        current_selection = self[f"list{self.navigation.list_index}"].getCurrent()
        if current_selection:
            logger.debug("current_selection: %s", current_selection)
            service_ref = self.page_channel_list[self.navigation.list_index]
            channel_id = self.channel_dict.get(
                service_ref, {}).get(self.data_source_id, "")
            detailed_event = self.tvmagazine_data.getDetailedEvent(
                current_selection)
            if detailed_event:
                self.session.open(EventDetails, self.date_str,
                                  detailed_event, service_ref, channel_id)

    def key_red(self):
        logger.info("...")
        service_ref = self.page_channel_list[self.navigation.list_index]
        current_selection = self[f"list{self.navigation.list_index}"].getCurrent()
        self.openMore(service_ref, current_selection)

    def key_green(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp("20:15")
        self.page_handler.showPage()

    def key_yellow(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp("22:00")
        self.page_handler.showPage()

    def key_blue(self):
        logger.info("...")
        self.timestamp = self.navigation.getTimestamp(strftime("%H:%M"))
        self.page_handler.showPage()

    def key_menu(self):
        logger.info("...")
        self.session.openWithCallback(
            self.openSetupScreenCallback,
            SetupScreen,
        )

    def openSetupScreenCallback(self, changed=False):
        logger.info("changed: %s", changed)
        if changed:
            prev_temp_dir = os.path.dirname(self.temp_dir)
            logger.debug("Previous temp directory: %s", prev_temp_dir)
            self.temp_dir = os.path.join(
                config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)
            logger.debug("New temp directory: %s", self.temp_dir)
            if self.data_source_id != config.plugins.tvmagazinecockpit.data_source.value + "_id":
                self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
                logger.debug("Data source ID changed to: %s",
                             self.data_source_id)
                for i in range(COLS):
                    self.clearColumn(i)
                deleteDirectory(prev_temp_dir)
                createDirectory(self.temp_dir)
                self.events = {}
            self.reload()

    def clearColumn(self, i):
        logger.info("i: %s", i)
        self[f"list{i}"].setList([])
        self[f"channel{i}"].setText("")
        self[f"picon{i}"].instance.setPixmap(None)
        self[f"programpix{i}"].instance.setPixmap(None)
        self[f"time{i}"].setText("")
        self[f"description{i}"].setText("")
        # A cleared column with no channel data would otherwise still show its
        # (now blank) bordered cell/labels as an empty box in the grid - hide
        # the whole slot instead so it collapses into genuinely empty space.
        self[f"list{i}"].hide()
        self[f"channel{i}"].hide()
        self[f"picon{i}"].hide()
        self[f"programpix{i}"].hide()
        self[f"time{i}"].hide()
        self[f"description{i}"].hide()

    def showColumnWidgets(self, i):
        self[f"list{i}"].show()
        self[f"channel{i}"].show()
        self[f"picon{i}"].show()
        self[f"programpix{i}"].show()
        self[f"time{i}"].show()
        self[f"description{i}"].show()

    def reload(self):
        logger.info("self.channel_list: %s", self.channel_list)
        self.channel_dict = readChannelDict()
        self.channel_list = readChannelList(self.channel_dict)
        self.navigation.reload(len(self.channel_list))
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
        self.data_source = data_sources[config.plugins.tvmagazinecockpit.data_source.value]
        self.timestamp = self.navigation.getTimestamp("20:15")
        self["day_selector"].setText(
            strftime("< %A, %d. %b %Y >", localtime(self.navigation.day_int)))
        self.list_columns = [[] for _i in range(COLS)]
        self.list_indices = [-1] * COLS
        self.prime_event_indices = [-1] * COLS
        # showPage() (below) sets each column's list, which resets its selection
        # to the skin template's default (disabled - see screenpart_EventCell.xmlinc)
        # and then re-enables just the active column, so no explicit
        # setSelectionEnable() calls are needed here.
        self.page_handler.showPage()
        self.selection_fixup_timer.start(50, True)

    def fixupSelection(self):
        self[f"list{self.navigation.list_index}"].setSelectionEnable(True)

    def __onClose__(self):
        logger.info("...")
        # Async detail fetches (Column.resolveEventDetails) can still be
        # in flight when the screen is closed - their callbacks arrive
        # later via reactor.callFromThread and would otherwise run against
        # a torn-down screen. Tell the column handler to stop waiting for
        # them.
        self.column_handler.cancelPendingRefresh()
