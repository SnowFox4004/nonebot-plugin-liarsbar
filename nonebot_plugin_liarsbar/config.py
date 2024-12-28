from pydantic import BaseModel
from nonebot import logger, get_plugin_config


class Config(BaseModel):
    """
    Configuration class for the application.
    """

    version: str = "1.0.0"
    description: str = "Nonebot plugin for playing Liar's Bar"


config = get_plugin_config(Config)
logger.info(f"Liar's Bar Plugin config loaded: {config}")
