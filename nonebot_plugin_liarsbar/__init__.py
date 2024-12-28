from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
# require("nonebot_plugin_localstore")
# require("nonebot_plugin_uninfo")
require("nonebot_plugin_waiter")

from .config import Config, config
from . import liars as liars

__version__ = config.version
__plugin_meta__ = PluginMetadata(
    name="Liar's Bar",
    description=config.description,
    usage="/liar",
    type="application",
    config=Config,
    homepage="https://github.com/SnowFox4004/nonebot-plugin-liarsbar",  # should be changed
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_waiter"
    ),
    extra={
        "version": __version__,
        "Author": "SnowFox4004",
    },
)
