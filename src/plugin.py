# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from Plugins.Plugin import PluginDescriptor
from . import ConfigInit  # noqa: F401, pylint: disable=unused-import
from .Debug import logger
from .Version import VERSION
from . import _
from .TVMagazineCockpit import TVMagazineCockpit
from .Cache import Cache
from .SkinUtils import loadPluginSkin


loadPluginSkin()


cache_instance = None


def main(session, **__kwargs):
    logger.info("...")
    session.open(TVMagazineCockpit)


def autoStart(reason, **kwargs):
    global cache_instance  # pylint: disable=global-statement
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            cache_instance = Cache()
            cache_instance.cleanup()
            cache_instance.downloadEvents()
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")
        cache_instance = None


def Plugins(**__kwargs):
    return [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART
            ],
            fnc=autoStart,
            needsRestart=True
        ),
        PluginDescriptor(
            name="TVMagazineCockpit",
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
                PluginDescriptor.WHERE_EXTENSIONSMENU,
            ],
            icon="TVMagazineCockpit.png",
            description=_("Browse TV Magazine"),
            fnc=main,
            needsRestart=True
        ),
    ]
