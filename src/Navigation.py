# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from .Debug import logger
from .ConfigInit import COLS
from .DateTimeUtils import get_day_details

MAX_DAYS = 15


class Navigation:
    """Class handling navigation functions for TV Magazine Cockpit."""

    def __init__(self, parent):
        """
        Initialize Navigation class with reference to parent TVMagazineCockpit instance.

        Args:
            parent: Parent TVMagazineCockpit instance for UI access
            channel_count: Total number of channels to navigate
        """
        self.parent = parent
        self.channel_count = 0
        self.list_index = 0  # current column index
        self.page_index = 0
        self.pages = 0

        self.date_str = "YY-MM-DD"
        self.day_int = 0
        self._selected_day = 1

    def reload(self, channel_count):
        self.channel_count = channel_count
        self.pages = (channel_count + COLS - 1) // COLS

        self.list_index = 0
        self.page_index = 0

        self.date_str, self.day_int = get_day_details(self._selected_day)

    def left(self):
        """Handle navigation to the left column."""
        logger.info("...")
        self.list_index -= 1
        if self.list_index < 0:
            self.list_index = COLS - 1
            self.page_index -= 1
            if self.page_index < 0:
                self.page_index = self.pages - 1
                max_list_index = self.channel_count % COLS - 1
                if max_list_index >= 0:
                    self.list_index = max_list_index
            return True
        return False

    def right(self):
        """Handle navigation to the right column."""
        logger.info("...")
        max_list_index = self.channel_count % COLS - 1
        if max_list_index < 0:
            max_list_index = COLS - 1
        self.list_index += 1
        if (self.list_index > COLS - 1 or (self.page_index == self.pages - 1 and self.list_index > max_list_index)):
            self.list_index = 0
            self.page_index += 1
            if self.page_index > self.pages - 1:
                self.page_index = 0
            return True
        return False

    def moveUp(self):
        """Navigate up within a column."""
        logger.info("list_index: %s", self.list_index)
        if self.parent.list_indices[self.list_index] > 1:
            self.parent.list_indices[self.list_index] -= 1
            self.setTimestamp()

    def moveDown(self):
        """Navigate down within a column."""
        logger.info("list_index: %s", self.list_index)
        logger.debug(
            "index: %s, len(list): %s",
            self.parent.list_indices[self.list_index],
            len(self.parent.list_columns[self.list_index])
        )
        if self.parent.list_indices[self.list_index] < len(self.parent.list_columns[self.list_index]) - 1:
            self.parent.list_indices[self.list_index] += 1
            self.setTimestamp()
        logger.debug(
            "new index: %s, len(list): %s",
            self.parent.list_indices[self.list_index],
            len(self.parent.list_columns[self.list_index])
        )

    def channelup(self):
        """Navigate to next page of channels."""
        logger.info("...")
        self.page_index += 1
        if self.page_index >= self.pages:
            self.page_index = 0
        self.list_index = 0

    def channeldown(self):
        """Navigate to previous page of channels."""
        logger.info("...")
        self.page_index -= 1
        if self.page_index < 0:
            self.page_index = self.pages - 1
            self.list_index = COLS - \
                1 if self.channel_count % COLS == 0 else self.channel_count % COLS - 1
        else:
            self.list_index = COLS - 1

    def key_next(self):
        """Move to next day."""
        logger.info("...")
        if self._selected_day < MAX_DAYS:
            self._selected_day += 1
        else:
            self._selected_day = 0
        self.date_str, self.day_int = get_day_details(self._selected_day)

    def key_back(self):
        """Move to previous day."""
        logger.info("...")
        if self._selected_day > 0:
            self._selected_day -= 1
        else:
            self._selected_day = MAX_DAYS
        self.date_str, self.day_int = get_day_details(self._selected_day)

    def setTimestamp(self):
        """Set the global timestamp for the new row."""
        index = self.parent.list_indices[self.list_index]
        column = self.parent.list_columns[self.list_index]
        self.parent.timestamp = column[index][4]

    def getTimestamp(self, hm):
        """
        Calculate Unix timestamp for a given time on the current day.

        Args:
            hm (str): Hour and minute string in format "HH:MM"

        Returns:
            int: Unix timestamp for the specified time
        """
        logger.info("hm: %s", hm)
        midnight = self.day_int
        h, m = hm.split(":")
        # Add hours and minutes to midnight
        timestamp = midnight + int(h) * 3600 + int(m) * 60
        logger.debug("Calculated timestamp: %s (midnight: %s + %s:%s)",
                     timestamp, midnight, h, m)
        return timestamp
