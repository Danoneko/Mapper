import json
import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ContextTypes, Application, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

from dal.entities import Location, Node
from dal.redis.osm_handlers import OSMRedisHelper
from services.geo.entities import GeoService

from geopy.distance import distance


@dataclass
class TelegramBotConfiguration:
    token_env_name: str
    workers_count: int

    bot_token: str = ""

    def __post_init__(self):
        load_dotenv()

        self.bot_token = os.environ.get(self.token_env_name)


class TelegramBot:
    def __init__(self, bot_config: TelegramBotConfiguration, geo_service: GeoService, redis: OSMRedisHelper):
        self.bot_config = bot_config
        self.geo_service = geo_service
        self.redis = redis
        self.LOCATION, self.DISTANCE, self.CATEGORY = range(3)

    def get_categories_menu(self) -> InlineKeyboardMarkup:
        inline_buttons: List[List[InlineKeyboardButton]] = []
        for category_slug, category in self.geo_service.osm_categories_map.items():
            button = InlineKeyboardButton(category.name, callback_data=category_slug)
            inline_buttons.append([button])

        return InlineKeyboardMarkup(inline_buttons)

    @staticmethod
    def get_nodes_menu(nodes: List[Node]) -> InlineKeyboardMarkup:
        inline_buttons: List[List[InlineKeyboardButton]] = []
        for node in nodes:
            button = InlineKeyboardButton(node.name,
                                          callback_data=f"{node.name},{node.latitude},{node.longitude}")
            inline_buttons.append([button])

        inline_buttons.append([InlineKeyboardButton("Назад", callback_data="0,0,0")])

        return InlineKeyboardMarkup(inline_buttons)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Привет! Я бот по поиску ближайших мест."
            "Прежде чем начать поиск, поделись своей live-геолокацией."
        ),

        return self.LOCATION

    async def location(self, update: Update, context) -> int:
        message = None

        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message

        location = Location(latitude=message.location.latitude, longitude=message.location.longitude)

        await self.redis.set_location_info(message.chat_id, location)

        await message.reply_text("Пожалуйста выберите категорию:", reply_markup=self.get_categories_menu())

        return self.CATEGORY

    async def list_nodes_for_category(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()

        location = self.redis.get_location_by_chat_id(query.message.chat.id)
        nodes = self.geo_service.get_nodes_for_category(category=query.data, user_location=location)

        await query.edit_message_text("Выберите место:", reply_markup=self.get_nodes_menu(nodes))

        return self.DISTANCE

    async def calc_distance(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()

        name, latitude, longitude = query.data.split(",")

        if name == "0":
            await query.edit_message_text("Пожалуйста выберите категорию:", reply_markup=self.get_categories_menu())

            return self.CATEGORY

        node = Node(
            name=name,
            latitude=float(latitude),
            longitude=float(longitude),
        )

        await self.redis.set_user_choice(query.chat_instance, node)

        user_location = self.redis.get_location_by_chat_id(query.message.chat.id)

        dist = distance((user_location.latitude, user_location.longitude), (node.latitude, node.longitude)).meters

        await query.edit_message_text(f"Расстояние до {node.name}: {dist:.2f} метров")
        await context.bot.send_location(chat_id=update.effective_chat.id, latitude=node.latitude, longitude=node.longitude)

        return self.DISTANCE

    @staticmethod
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""

        await update.message.reply_text(
            "Ну и не надо, ну и на здоровье"
        )

    def initialize_bot(self) -> Application:
        application = Application.builder().token(self.bot_config.bot_token).build()
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.LOCATION: [MessageHandler(filters.LOCATION, self.location)],
                self.CATEGORY: [CallbackQueryHandler(self.list_nodes_for_category)],
                self.DISTANCE: [CallbackQueryHandler(self.calc_distance)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        application.add_handler(conv_handler)

        return application
