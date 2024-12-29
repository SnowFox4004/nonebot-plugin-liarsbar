from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from . import liars as liars
from .config import Config, config

__version__ = config.version
__plugin_meta__ = PluginMetadata(
    name="Liar's Bar",
    usage="/createroon /startgame /fp <card> /zy /help",
    description="Nonebot plugin for playing liar's bar",
    type="application",
    config=Config,
    homepage="https://github.com/SnowFox4004/nonebot-plugin-liarsbar",  # should be changed
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={
        "version": __version__,
        "Author": "SnowFox4004",
    },
)
