# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from .__init__ import _
from .Debug import logger
from .ConfigScreen import ConfigScreen
from .About import about
from .Version import PLUGIN
from .FileUtils import deleteDirectory, createDirectory
from .ConfigInit import COLS


class Menu():
    def __init__(self, session):
        logger.info("...")
        self.session = session
        self.temp_dir = config.plugins.tvmagazinecockpit.temp_dir.value
        self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"

    def openMenu(self):
        logger.info("...")
        alist = [
            (_("Settings"), "settings"),
            (_("About"), "about"),
        ]

        self.session.openWithCallback(
            self.openMenuCallback,
            ChoiceBox,
            title=PLUGIN,
            list=alist,
        )

    def openMenuCallback(self, answer=None):
        logger.info("...")
        if answer:
            screen = answer[1]
            if screen == "settings":
                self.session.openWithCallback(
                    self.openConfigScreenCallback,
                    ConfigScreen,
                    config.plugins.tvmagazinecockpit
                )
            elif screen == "about":
                about(self.session)

    def openConfigScreenCallback(self, changed=False):
        logger.info("changed: %s", changed)
        if changed:
            prev_temp_dir = os.path.dirname(self.temp_dir)
            logger.debug("Previous temp directory: %s", prev_temp_dir)
            self.temp_dir = os.path.join(
                config.plugins.tvmagazinecockpit.temp_dir.value, self.date_str)  # pylint: disable=no-member
            logger.debug("New temp directory: %s", self.temp_dir)
            if self.data_source_id != config.plugins.tvmagazinecockpit.data_source.value + "_id":
                self.data_source_id = config.plugins.tvmagazinecockpit.data_source.value + "_id"
                logger.debug("Data source ID changed to: %s",
                             self.data_source_id)
                for i in range(COLS):
                    self.clearColumn(i)  # pylint: disable=no-member
                deleteDirectory(prev_temp_dir)
                createDirectory(self.temp_dir)
                self.events = {}
            self.reload()  # pylint: disable=no-member
