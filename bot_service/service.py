import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import query
from telegram import Update, CallbackQuery
from telegram.constants import ChatAction
from telegram.error import BadRequest
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from dal.osm_broker.broker import OpenMapsBroker
from dal.osm_broker.models import Location
from dal.storage.storage import Storage
from bot_service.menu import get_main_menu, get_categories_menu, get_callback_data_from_base64, get_nodes_menu, \
    get_cancel_menu, get_data_deletion_menu, get_back_menu

from geopy.distance import distance


@dataclass
class Status:
    STARTING = "starting"  # Начал работу с ботом, ждем шар локации
    IN_MENU = "InMenu"  # Либо закончил путешествие, либо еще не начинал, но пошарил локацию
    IN_CATEGORY = "InCategory"  # Выбрал пункт меню "ближайшее место"
    CHOOSING = "Choosing"  # Выбирает точку из категории или вводит адрес
    IN_PROGRESS = "InProgress"  # Идет до точки
    UPDATING = "Updating"  # Обновляет радиус поиска


class BotService:
    def __init__(self, storage: Storage, osm_broker: OpenMapsBroker, bot_token: str):
        self.storage = storage
        self.osm_broker = osm_broker
        self.bot_token = bot_token
        self.__logger = logging.getLogger("bot_service")

    def initialize_bot(self):
        application = Application.builder().token(self.bot_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.LOCATION, self.location_handler))
        application.add_handler(CallbackQueryHandler(self.callback_handler))
        application.add_handler(MessageHandler(None, self.message_handler))

        return application

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        image_path = './icon.jpg'

        message = update.message if update.message else update.edited_message

        with open(image_path, 'rb') as image_file:
            await message.reply_photo(
                photo=image_file,
                caption='Привет! 👋\n\n\
Это бот-путеводитель. Я умею искать ближайшие и нужные для тебя места. \
А также уведомлять о приближении к пункту назначения.\n\n\
Чтобы начать новый маршрут, поделитесь своей live-геолокацией 🧭'
            )

    async def location_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message if update.message else update.edited_message

        user = self.storage.get_user(chat_id=message.chat_id)

        # Создаем пользователя и выводим главное меню.
        if not user:
            # Проверяем, поделился ли пользователь LIVE-геолокацией или просто точкой.

            if not message.location.live_period:
                await message.reply_text("⚠️Бот умеет работать только с live-геолокацией ⚠️")

                return

            self.storage.create_user(chat_id=message.chat_id, status=Status.STARTING,
                                     latitude=message.location.latitude,
                                     longitude=message.location.longitude)

            bot = message.get_bot()

            await message.reply_text('Удачных путешествий! \n\n Чтобы вызвать меню, введите в чат /menu',
                                     reply_markup=get_main_menu())

            self.storage.update_user_status(chat_id=message.chat_id, status=Status.IN_MENU)

            return

        self.storage.update_user_location(chat_id=message.chat_id, latitude=message.location.latitude,
                                          longitude=message.location.longitude)

        # Работаем только с пользователем, который идет до точки
        if user["status"] == Status.IN_PROGRESS:
            await context.bot.sendChatAction(chat_id=message.chat_id, action=ChatAction.TYPING)
            destination = self.storage.get_destination(user_id=user["id"])

            if destination and message.location.latitude and message.location.longitude:
                dist = distance((message.location.latitude, message.location.longitude),
                                (destination["latitude"], destination["longitude"])).meters

                bot = message.get_bot()

                if dist <= 30:
                    self.storage.update_user_status(chat_id=message.chat_id, status=Status.IN_MENU)
                    self.storage.delete_destination(user_id=user["id"])

                    try:
                        await bot.edit_message_text('Поздравляю! Вы дошли до пункта назначения! \n До новых встреч!',
                                                    chat_id=message.chat_id, message_id=destination["message_id"])
                    except BadRequest as e:
                        await message.reply_text('Поздравляю! Вы дошли до пункта назначения! \n До новых встреч!',
                                                 reply_markup=get_main_menu())

                    return

                try:
                    await bot.edit_message_text(f'Расстояние до {destination["name"]}: {dist:.2f} метров',
                                                chat_id=message.chat_id, message_id=destination["message_id"],
                                                reply_markup=get_cancel_menu())

                except BadRequest as e:
                    await message.reply_text(f'Расстояние до {destination["name"]}: {dist:.2f} метров',
                                             reply_markup=get_cancel_menu())

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user = self.storage.get_user(chat_id=query.message.chat.id)

        if not user:
            await query.edit_message_text('Сначала поделитесь гео-локацией')


        if query.data == "nearest":
            self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.IN_CATEGORY)

            categories = self.storage.get_categories()

            await query.edit_message_text('Выберите категорию:', reply_markup=get_categories_menu(categories))

        elif query.data == "specific":
            self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.CHOOSING)

            await query.edit_message_text('Введите улицу и номер дома. Допустимый формат сообщения: Первомайская,208',
                                          reply_markup=get_back_menu())

        elif query.data == "update":
            self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.UPDATING)

            await query.edit_message_text('Введите радиус поиска в метрах')

        elif query.data == "back":
            destination = self.storage.get_destination(user_id=user["id"])

            if destination:
                self.storage.delete_destination(user_id=user["id"])

            self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.IN_MENU)

            await query.edit_message_text('Что ищете?', reply_markup=get_main_menu())
        elif query.data == "cancel":
            self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.IN_MENU)

            destination = self.storage.get_destination(user_id=user["id"])

            bot = query.message.get_bot()
            chat_id = query.message.chat.id

            await bot.delete_message(chat_id=chat_id, message_id=destination["map_message_id"])
            await bot.delete_message(chat_id=chat_id, message_id=destination["message_id"])

            await bot.send_message(chat_id=chat_id, text='Путешествие отменено!', reply_markup=get_main_menu())

            self.storage.delete_destination(user_id=user["id"])
        elif query.data == "delete":
            self.storage.delete_user(chat_id=query.message.chat.id)

            await query.edit_message_text('Данные удалены, чтобы начать заново, поделитель локацией.')
        else:
            await context.bot.sendChatAction(chat_id=query.message.chat.id, action=ChatAction.TYPING)

            data = get_callback_data_from_base64(query.data)

            if user["status"] == Status.CHOOSING and data:
                latitude, longitude = data.split(',')

                name = ""

                for button in query.message.reply_markup.inline_keyboard:
                    if button[0]["callback_data"] == query.data:
                        name = button[0]["text"]

                        break

                dist = distance((user["latitude"], user["longitude"]),
                                (latitude, longitude)).meters

                bot = query.message.get_bot()
                chat_id = query.message.chat.id

                map_message = await bot.send_location(chat_id=chat_id, latitude=latitude, longitude=longitude)

                await bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)

                message = await bot.send_message(chat_id=chat_id, text=f'Расстояние до {name}: {dist:.2f} метров',
                                                 reply_markup=get_cancel_menu())

                self.storage.create_destination(user_id=user["id"], name=name, latitude=latitude, longitude=longitude,
                                                message_id=message.message_id, map_message_id=map_message.message_id)

                self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.IN_PROGRESS)

            elif user["status"] == Status.IN_CATEGORY:
                osm_types = self.storage.get_osm_types(uuid.UUID(query.data))

                nodes = []

                location = Location(latitude=user["latitude"], longitude=user["longitude"],
                                    search_distance=user["search_distance"])

                for osm_type in osm_types:
                    nodes.extend(self.osm_broker.get_nodes(osm_type=osm_type["type"], osm_name=osm_type["name"],
                                                           user_location=location))

                await query.edit_message_text("Выберите место:", reply_markup=get_nodes_menu(nodes))

                self.storage.update_user_status(chat_id=query.message.chat.id, status=Status.CHOOSING)

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message if update.message else update.edited_message

        user = self.storage.get_user(message.chat.id)

        if user:
            if message.text == '/menu':
                if user["status"] != Status.IN_MENU:
                    await message.reply_text('Нельзя вызвать меню, пока есть активный маршрут! Отмените маршрут!')

                    return

                await message.reply_text("Удачных путешеcтвий!", reply_markup=get_main_menu())
            if user["status"] == Status.UPDATING:
                try:
                    search_distance = int(message.text)
                    self.storage.update_search_distance(chat_id=message.chat.id, search_distance=search_distance)

                    await message.reply_text('Радиус обновлен', reply_markup=get_main_menu())

                    self.storage.update_user_status(chat_id=message.chat.id, status=Status.IN_MENU)
                except ValueError:
                    await message.reply_text('Неверное значение', reply_markup=get_main_menu())

                    self.storage.update_user_status(chat_id=message.chat.id, status=Status.IN_MENU)
            elif user["status"] == Status.CHOOSING:
                try:
                    name, house_number = message.text.split(',')
                    house_number = int(house_number)

                    location = Location(latitude=user["latitude"], longitude=user["longitude"],
                                        search_distance=user["search_distance"])
                    node = self.osm_broker.get_street(name, house_number, location)

                    bot = message.get_bot()
                    chat_id = message.chat.id

                    map_message = await bot.send_location(chat_id=chat_id, latitude=float(node.latitude),
                                                          longitude=float(node.longitude))

                    dist = distance((user["latitude"], user["longitude"]), (node.latitude, node.longitude)).meters

                    message = await bot.send_message(chat_id=chat_id,
                                                     text=f'Расстояние до {name}, {str(house_number)}: {dist:.2f} метров',
                                                     reply_markup=get_cancel_menu())

                    self.storage.create_destination(user_id=user["id"], name=name, latitude=node.latitude,
                                                    longitude=node.longitude,
                                                    message_id=message.message_id,
                                                    map_message_id=map_message.message_id)

                    self.storage.update_user_status(chat_id=message.chat.id, status=Status.IN_PROGRESS)
                except ValueError as e:
                    self.__logger.exception(e)
                    await message.reply_text('Адрес введен некорректно', reply_markup=get_main_menu())

                    self.storage.update_user_status(chat_id=message.chat.id, status=Status.IN_MENU)
                except IndexError as e:
                    self.__logger.exception(e)
                    await message.reply_text('Не смогли найти адрес в радиусе 10км от вас:(',
                                             reply_markup=get_main_menu())

                    self.storage.update_user_status(chat_id=message.chat.id, status=Status.IN_MENU)
