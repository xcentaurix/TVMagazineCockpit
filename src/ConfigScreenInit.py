# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from .Debug import logger
from .__init__ import _


class ConfigScreenInit():
    def __init__(self, _csel, session):
        self.session = session
        self.section = 400 * "¯"
        # text, config, on save, on ok, e2 usage level, depends on rel parent, description
        self.config_list = [
            (self.section, _("COCKPIT"), None, None, 0, [], ""),
            (_("Data source"), config.plugins.tvmagazinecockpit.data_source, None, None, 0, [], _("Select the data source for event information.")),
            (_("Picon directory"), config.plugins.tvmagazinecockpit.piconspath, self.validatePath, None, 0, [], _("Select the directory the picons are stored in.")),
            (self.section, _("DEBUG"), None, None, 2, [], ""),
            (_("Log level"), config.plugins.tvmagazinecockpit.debug_log_level, self.setLogLevel, None, 2, [], _("Select the debug log level.")),
        ]

    @staticmethod
    def save(_conf):
        logger.debug("...")

    def openLocationBox(self, element):
        logger.debug("element: %s", element.value)
        return True

    def setLogLevel(self, element):
        logger.debug("element: %s", element.value)
        return True

    def validatePath(self, element):
        logger.debug("element: %s", element.value)
        return True
