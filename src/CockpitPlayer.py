# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.ActionMap import ActionMap
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarServiceErrorPopupSupport
from .Debug import logger


class CockpitPlayer(MoviePlayer, InfoBarServiceErrorPopupSupport):
    def __init__(self, session, service):
        logger.info("...")
        MoviePlayer.__init__(self, session, service)
        InfoBarServiceErrorPopupSupport.__init__(self)
        InfoBarServiceErrorPopupSupport.STATE_TUNING = ""
        InfoBarServiceErrorPopupSupport.STATE_CONNECTING = ""
        InfoBarServiceErrorPopupSupport.MESSAGE_WAIT = ""
        InfoBarServiceErrorPopupSupport.STATE_RECONNECTING = ""
        self.skinName = "MoviePlayer"

        self["CockpitPlayerActions"] = ActionMap(
            ["MoviePlayerActions"],
            {
                "leavePlayer": self.leavePlayer,
                "leavePlayerOnExit": self.leavePlayer,
            },
            -2
        )

    def leavePlayer(self):
        logger.info("...")
        self.session.nav.stopService()
        self.close()

    def show(self):
        # disable the info bar
        logger.info("...")
