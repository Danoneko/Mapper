import dataclass_factory
import yaml

from dataclasses import dataclass

from redis import Redis

from dal.redis.config import RedisConfiguration
from controllers.bot.bot import TelegramBotConfiguration
from services.geo.geo import OSMConfiguration
from dal.open_maps_broker.open_maps_broker import OpenMapsBroker
from dal.redis.osm_handlers import OSMRedisHelper
from controllers.bot.bot import TelegramBot
from services.geo.geo import OSMService


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


def inject() -> None:
    config = load_config()

    geo_broker = OpenMapsBroker()
    geo_service = OSMService(categories=config.osm_broker.categories_to_amenities_map, geo_broker=geo_broker)

    osm_redis_helper = OSMRedisHelper(redis=configure_redis(config.redis))

    telegram_bot = TelegramBot(bot_config=config.telegram_bot, geo_service=geo_service, redis=osm_redis_helper)

    app = telegram_bot.initialize_bot()

    app.run_polling()