import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, ContextTypes, Application, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

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
        self.LOCATION, self.DISTANCE, self.CATEGORY, self.NEW_ROUTE, self.SELECT_ROUTE = range(5)

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
            callback_data = f"{node.name},{node.latitude},{node.longitude}"
            if len(callback_data) > 64:
                callback_data = callback_data[:64]  # Обрезаем строку до 64 символов
            button = InlineKeyboardButton(node.name, callback_data=callback_data)
            inline_buttons.append([button])

        inline_buttons.append([InlineKeyboardButton("Назад", callback_data="back")])
        return InlineKeyboardMarkup(inline_buttons)    
    
    def get_search_options_menu(self) -> InlineKeyboardMarkup:
        options = [
            InlineKeyboardButton("Ближайшее место", callback_data="nearest"),
            InlineKeyboardButton("Конкретный адрес", callback_data="specific")
        ]
        return InlineKeyboardMarkup([options])
    
# =====================================================================================================

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        image_path = './icon.jpg'
        new_route_keyboard = [[KeyboardButton("Начать новый маршрут!")]]
        reply_markup = ReplyKeyboardMarkup(new_route_keyboard, resize_keyboard=True, one_time_keyboard=True)

        message = update.message if update.message else update.edited_message
        self.redis.delete_location_by_chat_id(message.chat_id)
        
        with open(image_path, 'rb') as image_file:
            await message.reply_photo(
                photo=image_file,
                reply_markup=reply_markup,
                caption='Привет! 👋\n\n\
Это бот-путеводитель. Я умею искать ближайшие и нужные для тебя места. \
А также уведомлять о приближении к пункту назначения.\n\n\
Давай начнем новый маршрут!\
\n📍📍📍'
            )
        return self.NEW_ROUTE

# =====================================================================================================

    async def new_route(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message = update.message if update.message else update.edited_message
        self.redis.delete_choice_by_chat_id(message.chat_id)

        location = self.redis.get_location_by_chat_id(message.chat_id)
        if location is None:
            await message.reply_text("Чтобы начать новый маршрут, поделитесь своей live-геолокацией 🧭")
            return self.LOCATION
        
        await message.reply_text("Что ищем?🧐", reply_markup=self.get_search_options_menu())
        return self.SELECT_ROUTE

# =====================================================================================================

    async def location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message = update.message if update.message else update.edited_message
        location = Location(latitude=message.location.latitude, longitude=message.location.longitude, live_period=message.location.live_period)
        
        await self.redis.set_location_info(message.chat_id, location)

        await message.reply_text("Что ищем?🧐", reply_markup=self.get_search_options_menu())
        return self.SELECT_ROUTE
      
# =====================================================================================================

    async def select_route(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()

        if query.data == "nearest":
            await query.edit_message_text("Выберите категорию:", reply_markup=self.get_categories_menu())
            return self.CATEGORY
        elif query.data == "specific":
            await query.edit_message_text("Введите конкретный адрес:")
            return self.NEW_ROUTE
        elif query.data == "back":
            await query.edit_message_text("Что ищем?🧐", reply_markup=self.get_search_options_menu())
            return self.SELECT_ROUTE
        else:
            await query.edit_message_text("Некорректный выбор, пожалуйста, попробуйте снова.")
            return self.SELECT_ROUTE

# =====================================================================================================

    async def category(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            await query.edit_message_text("Что ищем?🧐", reply_markup=self.get_search_options_menu())
            return self.SELECT_ROUTE

        location = self.redis.get_location_by_chat_id(query.message.chat.id)

        try:
            nodes = self.geo_service.get_nodes_for_category(category=query.data, user_location=location)
        except KeyError:
            back_button = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back")]])
            await query.edit_message_text("По вашему запросу ничего не найдено. Пожалуйста, выберите категорию:", reply_markup=back_button)
            return self.CATEGORY

        if nodes:
            await query.edit_message_text("Выберите место:", reply_markup=self.get_nodes_menu(nodes))
        else:
            back_button = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data="back")]])
            await query.edit_message_text("По вашему запросу ничего не найдено", reply_markup=back_button)

        return self.DISTANCE

# =====================================================================================================

    async def distance(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        await query.answer()

        if query.data == "back":
            await query.edit_message_text("Выберите категорию:", reply_markup=self.get_categories_menu())
            return self.CATEGORY

        try:
            name, latitude, longitude = query.data.split(",")
        except ValueError:
            await query.edit_message_text("Выберите категорию:", reply_markup=self.get_categories_menu())
            return self.CATEGORY

        node = Node(
            name=name,
            latitude=float(latitude),
            longitude=float(longitude),
        )

        choice = self.redis.get_choice_by_chat_id(query.message.chat_id)
        user_location = self.redis.get_location_by_chat_id(query.message.chat.id)
        dist = distance((user_location.latitude, user_location.longitude), (node.latitude, node.longitude)).meters

        if choice is None:
            await self.redis.set_user_choice(query.message.chat.id, node)
            await context.bot.send_location(chat_id=update.effective_chat.id, latitude=node.latitude, longitude=node.longitude)


        new_route_keyboard = [[KeyboardButton("Начать новый маршрут!")]]
        reply_markup = ReplyKeyboardMarkup(new_route_keyboard, resize_keyboard=True, one_time_keyboard=True)
        if dist <= 5:
            self.redis.delete_choice_by_chat_id(query.message.chat_id)
            await query.message.edit_message_text("Маршрут окончен!", reply_markup=reply_markup)
            return self.NEW_ROUTE

        await query.edit_message_text(f"Расстояние до {node.name}: {dist:.2f} метров")

        return self.DISTANCE

# =====================================================================================================  

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        message = update.message
        self.redis.delete_choice_by_chat_id(message.chat_id)
        await message.reply_text(
            "До встречи! 👋\n\nПопутешествуем в следующий раз!"
        )
        return ConversationHandler.END

# =====================================================================================================

    def initialize_bot(self) -> Application:
        application = Application.builder().token(self.bot_config.bot_token).build()
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.LOCATION: [MessageHandler(filters.LOCATION, self.location)],
                self.CATEGORY: [CallbackQueryHandler(self.category, pattern="^.+$")],
                self.DISTANCE: [CallbackQueryHandler(self.distance, pattern="^.+$")],
                self.NEW_ROUTE: [MessageHandler(filters.TEXT & filters.Regex('^Начать новый маршрут!$'), self.new_route)],
                self.SELECT_ROUTE: [CallbackQueryHandler(self.select_route, pattern="^.+$")],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            allow_reentry=True,
            per_message=False 
        )
        application.add_handler(conv_handler)
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^Начать новый маршрут!$'), self.new_route))
        return application
