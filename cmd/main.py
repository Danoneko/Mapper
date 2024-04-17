from pprint import pprint

from redis import Redis
from telegram.ext import MessageHandler, filters, Application
from telegram import Update

from cmd.config import load_config, configure_redis
from dal.open_maps_broker.open_maps_broker import OpenMapsBroker
from dal.entities import Location, GeoBroker
from dal.redis.osm_handlers import OSMRedisHelper
from services.bot.bot import TelegramBot
from services.geo.entities import GeoService
from services.geo.geo import OSMService


def inject() -> None:
    config = load_config()

    geo_broker = OpenMapsBroker()
    geo_service = OSMService(categories=config.osm_broker.categories_to_amenities_map, geo_broker=geo_broker)

    osm_redis_helper = OSMRedisHelper(redis=configure_redis(config.redis))

    telegram_bot = TelegramBot(bot_config=config.telegram_bot, geo_service=geo_service, redis=osm_redis_helper)

    app = telegram_bot.initialize_bot()

    app.run_polling()


if __name__ == '__main__':
    inject()
