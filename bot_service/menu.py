import base64
import logging
from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup

from dal.osm_broker.models import Node


def get_base64_callback_data(callback_data: str):
    return base64.b64encode(callback_data.encode("utf-8")).decode("utf-8")


def get_callback_data_from_base64(encoded_string: str):
    try:
        return base64.b64decode(encoded_string).decode("utf-8")
    except Exception as e:
        logging.error(e)

        return None


def get_categories_menu(categories: list) -> InlineKeyboardMarkup:
    inline_buttons = []
    for category in categories:
        button = InlineKeyboardButton(category["name"], callback_data=str(category["id"]))
        inline_buttons.append([button])

    inline_buttons.append([InlineKeyboardButton("Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_buttons)


def get_nodes_menu(nodes: List[Node]) -> InlineKeyboardMarkup:
    inline_buttons: List[List[InlineKeyboardButton]] = []
    for node in nodes:
        callback_data = f"{node.latitude},{node.longitude}"

        button = InlineKeyboardButton(node.name, callback_data=get_base64_callback_data(callback_data))
        inline_buttons.append([button])

    inline_buttons.append([InlineKeyboardButton("Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_buttons)


def get_main_menu() -> InlineKeyboardMarkup:
    options = [
        [InlineKeyboardButton("Ближайшее место", callback_data="nearest"),
         InlineKeyboardButton("Конкретный адрес", callback_data="specific"), ],
        [InlineKeyboardButton("Изменить радиус поиска", callback_data="update")],
        [InlineKeyboardButton("Удалить все данные", callback_data="delete")],
    ]
    return InlineKeyboardMarkup(options)


def get_cancel_menu() -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('Отменить путешествие', callback_data='cancel')]]

    return InlineKeyboardMarkup(button)


def get_data_deletion_menu() -> ReplyKeyboardMarkup:
    button = [[KeyboardButton('Удалить все данные')]]

    return ReplyKeyboardMarkup(button)


def get_back_menu() -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('Отменить путешествие', callback_data='back')]]

    return InlineKeyboardMarkup(button)
