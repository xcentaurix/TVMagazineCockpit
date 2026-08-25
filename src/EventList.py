# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from Components.Sources.List import List
from .Debug import logger


class EventList(List):

    def __init__(self, alist=None):
        logger.info("...")
        List.__init__(self, list=alist if alist else [], enableWrapAround=True)

    def moveToIndex(self, index):
        logger.info("...")
        self.index = index

    def getCurrentIndex(self):
        logger.info("...")
        return self.index

    def moveUp(self):
        logger.info("...")
        self.up()

    def moveDown(self):
        logger.info("...")
        self.down()

    def setSelectionEnable(self, selectionEnabled=True):
        renderers = self.master.downstream_elements if self.master is not None else []
        logger.info("selectionEnabled: %s, self.master is None: %s, renderer instances: %s",
                    selectionEnabled, self.master is None,
                    [getattr(r, "instance", "<no instance attr>") for r in renderers])
        if self.master is not None:
            self.master.downstream_elements.setSelectionEnabled(selectionEnabled)

    def hide(self):
        if self.master is not None:
            self.master.downstream_elements.hide()

    def show(self):
        if self.master is not None:
            self.master.downstream_elements.show()
