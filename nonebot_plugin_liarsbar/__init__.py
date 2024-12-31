from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from . import liars as liars
from .config import Config, config

__version__ = "1.0.3"
__plugin_meta__ = PluginMetadata(
    name="Liar's Bar",
    usage="/createroon /startgame /fp <card> /zy /help /quitroom",
    description="适用于 nonebot2 框架的 liar's bar 插件",
    type="application",
    config=Config,
    homepage="https://github.com/SnowFox4004/nonebot-plugin-liarsbar",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    extra={
        "version": __version__,
        "Author": "SnowFox4004",
    },
)
