# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.GUIComponent import GUIComponent
from Components.MultiContent import MultiContentEntryText
from enigma import eListbox, eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER, RT_WRAP
from .Debug import logger


class EventList(GUIComponent):

    def __init__(self, alist=None):
        logger.info("...")
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()  # noqa: E741
        self.l.setFont(0, gFont("Regular", 23))
        self.l.setFont(1, gFont("Regular", 20))
        self.l.setFont(2, gFont("Regular", 17))
        self.l.setItemHeight(140)
        self.list = alist if alist else []
        self.l.setList(self.list)
        self.l.setBuildFunc(self.buildEntry)

    def buildEntry(self, startHM, title, subtitle, year, _startTime, *_args):
        res = [None]
        res.append(MultiContentEntryText(pos=(5, 7), size=(55, 23), font=1, flags=RT_HALIGN_LEFT, text=str(startHM) if startHM else "", backcolor=None))
        res.append(MultiContentEntryText(pos=(65, 5), size=(245, 75), font=0, flags=RT_HALIGN_LEFT | RT_WRAP, text=str(title) if title else "", backcolor=None))
        res.append(MultiContentEntryText(pos=(65, 87), size=(245, 23), font=1, flags=RT_HALIGN_LEFT | RT_WRAP, text=str(subtitle) if subtitle else "", color=0xa0a0a0, color_sel=0xa0a0a0, backcolor=None))
        res.append(MultiContentEntryText(pos=(65, 115), size=(245, 23), font=1, flags=RT_HALIGN_LEFT | RT_WRAP, text=str(year) if year else "", color=0xa0a0a0, color_sel=0xa0a0a0, backcolor=None))
        res.append(MultiContentEntryText(pos=(0, 0), size=(320, 140), font=1, flags=RT_VALIGN_CENTER, text="", border_width=1, border_color=0x595959))
        return res

    def getCurrent(self):
        logger.info("...")
        return self.l.getCurrentSelection()

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        logger.info("...")
        instance.setContent(self.l)
        instance.setSelectionEnable(False)

    def preWidgetRemove(self, instance):
        logger.info("...")
        instance.setContent(None)

    def moveToIndex(self, index):
        logger.info("...")
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        logger.info("...")
        return self.instance.getCurrentIndex()

    def moveUp(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveUp)

    def moveDown(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveDown)

    def moveLeft(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveLeft)

    def moveRight(self):
        logger.info("...")
        if self.instance is not None:
            self.instance.moveSelection(self.instance.moveRight)

    def invalidate(self):
        logger.info("...")
        self.l.invalidate()

    def entryRemoved(self, index):
        logger.info("...")
        self.l.entryRemoved(index)

    def setSelectionEnable(self, selectionEnabled=True):
        logger.info("...")
        self.instance.setSelectionEnable(selectionEnabled)
