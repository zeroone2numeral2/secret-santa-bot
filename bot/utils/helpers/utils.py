import logging
import logging.config
import json
import re
from datetime import timedelta
from html import escape

from pyrogram import Message

from config import config


def load_logging_config(file_name='logging.json'):
    with open(file_name, 'r') as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)


def html_escape(string, *args, **kwargs):
    if string is None:
        return None

    return escape(string, *args, **kwargs)


def plugin_name(name: str):
    return name.split('.')[-1]


def delete_message_safe(messages: [[Message], Message], revoke=True):
    if not isinstance(messages, (list, tuple)):
        messages = [messages]

    for message in messages:
        # noinspection PyBroadException
        try:
            message.delete(revoke=revoke)
        except Exception:
            pass


def message_link(message: Message):
    if message.chat.username:
        return 'https://t.me/{}/{}'.format(message.chat.username, message.message_id)
    else:
        chat_id = str(message.chat.id).replace('-100', '')
        return 'https://t.me/c/{}/{}'.format(chat_id, message.message_id)


def inline_mention(user):
    return '<a href="tg://user?id={}">{}</a>'.format(user.id, html_escape(user.first_name))
