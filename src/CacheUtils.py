# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
from time import time, strftime, localtime
import json
from Components.config import config
from .Debug import logger


date_str = strftime("%Y-%m-%d", localtime(int(time())))


def loadEvents():
    logger.info("Loading events...")
    events = {}
    cache_path = os.path.join(
        config.plugins.tvmagazinecockpit.temp_dir.value, date_str, "events.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as fp:
            events = json.load(fp)
            logger.info("Events loaded successfully.")
            logger.debug("Loaded events: %s", events)
    else:
        logger.warning("Events cache file does not exist: %s", cache_path)
    return events


def saveEvents(events):
    logger.info("Saving events: %s", events)
    cache_path = os.path.join(
        config.plugins.tvmagazinecockpit.temp_dir.value, date_str, "events.json")
    if date_str in events:
        with open(cache_path, 'w', encoding='utf-8') as fp:
            json.dump(events, fp, indent=4)
            logger.info("Events saved successfully to %s", cache_path)
