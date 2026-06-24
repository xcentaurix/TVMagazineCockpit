# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

import math

from .Debug import logger
from .Index import idx


def find_time_event_index(events, timestamp):
    """
    Find event closest to the specified time point.

    Args:
        events (list): List of events to search
        timestamp (int): Reference timestamp to find closest event to

    Returns:
        int: Index of the closest event
    """
    if not events:
        logger.debug("No input events")
        return -1

    closest_index = 0
    min_time_diff = math.inf

    for index, event in enumerate(events):
        event_time = event[idx["startTime"]]
        time_diff = abs(timestamp - event_time)
        if time_diff < min_time_diff:
            min_time_diff = time_diff
            closest_index = index

    logger.debug("Found closest event at index %s with time difference %s",
                 closest_index, min_time_diff)
    return closest_index
