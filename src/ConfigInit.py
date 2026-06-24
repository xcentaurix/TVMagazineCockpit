# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config, ConfigSelection, ConfigSubsection, ConfigNothing, ConfigDirectory, NoSave
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CONFIG
from .Debug import logger, log_levels, initLogging

COLS = 6
ROWS = 5

plugindir = resolveFilename(SCOPE_PLUGINS, "Extensions/TVMagazineCockpit/")
configdir = resolveFilename(SCOPE_CONFIG)


data_sources = {
    "tvfa": "TVFürAlle",
    "tvm": "TVMovie",
    "tvs": "TVSpielfilm"
}

data_source_choices = list(data_sources.items())


class ConfigInit():

    def __init__(self):
        logger.info("...")
        config.plugins.tvmagazinecockpit = ConfigSubsection()
        config.plugins.tvmagazinecockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.tvmagazinecockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        config.plugins.tvmagazinecockpit.temp_dir = ConfigSelection(
            default="/data/TVC", choices=[("/data/TVC", "/data/TVC")])
        config.plugins.tvmagazinecockpit.data_source = ConfigSelection(
            default="tvfa", choices=data_source_choices)
        config.plugins.tvmagazinecockpit.piconspath = ConfigDirectory(
            default="/usr/share/enigma2/picon/")
        initLogging()
