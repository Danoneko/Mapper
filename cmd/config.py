import os

import dataclass_factory
import yaml

from dataclasses import dataclass
from typing import List, Dict

from redis import Redis

from dal.redis.config import RedisConfiguration
from services.bot.bot import TelegramBotConfiguration
from services.geo.geo import OSMConfiguration


@dataclass
class Config:
    osm_broker: OSMConfiguration
    redis: RedisConfiguration
    telegram_bot: TelegramBotConfiguration


def configure_redis(redis_config: RedisConfiguration) -> Redis:
    return Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.database,
        password=redis_config.password,
    )


def load_config():
    with open('config.yaml', 'r') as stream:
        yaml_config = yaml.safe_load(stream)

        factory = dataclass_factory.Factory()
        config: Config = factory.load(yaml_config, Config)

        return config
