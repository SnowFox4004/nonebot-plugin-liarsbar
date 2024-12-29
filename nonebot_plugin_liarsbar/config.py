from nonebot import get_plugin_config, logger
from pydantic import BaseModel


class Config(BaseModel):
    """
    Configuration class for the application.
    """

    liars_num_bullet: int = 1  # 每玩家枪内子弹数


config = get_plugin_config(Config)
logger.info(f"Liar's Bar Plugin config loaded: {config}")
