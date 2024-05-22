import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardMarkup, KeyboardButton
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
        self.LOCATION, self.DISTANCE, self.CATEGORY, self.ROUTE_TYPE = range(4)

    def get_categories_menu(self) -> InlineKeyboardMarkup:
        inline_buttons: List[List[InlineKeyboardButton]] = []
        for category_slug, category in self.geo_service.osm_categories_map.items():
            button = InlineKeyboardButton(category_slug, callback_data=category_slug)
            inline_buttons.append([button])

        return InlineKeyboardMarkup(inline_buttons)

    @staticmethod
    def get_nodes_menu(nodes: List[Node]) -> InlineKeyboardMarkup:
        inline_buttons: List[List[InlineKeyboardButton]] = []
        for node in nodes:
            button = InlineKeyboardButton(node.name, callback_data=f"{node.name},{node.latitude},{node.longitude}")
            inline_buttons.append([button])
        inline_buttons.append([InlineKeyboardButton("Назад", callback_data="0,0,0")])

        return InlineKeyboardMarkup(inline_buttons)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        image_path = './icon.jpg'
        new_route_keyboard = [[KeyboardButton("Начать новый маршрут!")]]
        reply_markup = ReplyKeyboardMarkup(new_route_keyboard, resize_keyboard=True, one_time_keyboard=True)
        with open(image_path, 'rb') as image_file:
            await update.message.reply_photo(
                photo=image_file,
                reply_markup=reply_markup,
                caption="Привет! 👋\n\nЭто бот-путеводитель. Я умею искать ближайшие и нужные для тебя места. А также уведомлять о приближении к пункту назначения.\n\nДавай начнем новый маршрут!\n📍📍📍"
            )

        return self.ROUTE_TYPE
    
    async def choose_route(self, update: Update, context: CallbackContext) -> int:
        new_route_keyboard = [[KeyboardButton("Конкретный адрес"), KeyboardButton("Ближайшее место")]]
        reply_markup = ReplyKeyboardMarkup(new_route_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Что ищем? 🧐",
            reply_markup=reply_markup
        )
        await update.message.reply_text(
            "Чтобы начать искать поделись своей live-локацией 🧭"
        )
        
        return self.LOCATION

    async def location(self, update: Update, context) -> int:
        message = None
        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message

        location = Location(latitude=message.location.latitude, longitude=message.location.longitude)
        await self.redis.set_location_info(message.chat_id, location)

        choice = self.redis.get_choice_by_chat_id(message.chat_id)
        if choice is None:
            await message.reply_text("Выберите категорию:", reply_markup=self.get_categories_menu())
            return self.CATEGORY
        
        dist = distance((message.location.latitude, message.location.longitude), (choice.latitude, choice.longitude)).meters
        if dist <= 5:
            self.redis.delete_choice_by_chat_id(message.chat_id)
            await message.reply_message_text("Маршрут окончен!")
            return self.ROUTE_TYPE
        
        await message.edit_message_text(f"Расстояние до {choice.name}: {dist:.2f} метров")

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
        await self.redis.set_user_choice(query.message.chat.id, node)
        user_location = self.redis.get_location_by_chat_id(query.message.chat.id)
        dist = distance((user_location.latitude, user_location.longitude), (node.latitude, node.longitude)).meters
        await query.edit_message_text(f"Расстояние до {node.name}: {dist:.2f} метров")
        await context.bot.send_location(chat_id=update.effective_chat.id, latitude=node.latitude, longitude=node.longitude)

        return self.DISTANCE
    
    @staticmethod
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        message = None
        self.redis.delete_choice_by_chat_id(message.chat_id)
        await update.message.reply_text(
            "До встречи! 👋\n\nПопутешествуем в следующий раз!"
        )

    def initialize_bot(self) -> Application:
        application = Application.builder().token(self.bot_config.bot_token).build()
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.LOCATION: [MessageHandler(filters.LOCATION, self.location)],
                self.CATEGORY: [CallbackQueryHandler(self.list_nodes_for_category)],
                self.DISTANCE: [CallbackQueryHandler(self.calc_distance)],
                self.ROUTE_TYPE: [MessageHandler(filters.TEXT & filters.Regex('^Начать новый маршрут!$'), self.choose_route)],

            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        application.add_handler(conv_handler)

        return application
