import logging

from pyrogram import Client
from pyrogram import Message
from pyrogram import Filters
from pyrogram import InlineKeyboardMarkup
from pyrogram import InlineKeyboardButton
from pyrogram import Emoji

from bot import bot
from bot.utils import decorators
from bot.utils import utils
from config import config

__plugin__ = utils.plugin_name(__name__)

logger = logging.getLogger('plugin:' + __plugin__)

NEW_CHAT_MESSAGE = """Hello! I'm a bot that helps people organize a Secret Santa {shhh}{santa}{gift} \
Just answer to this message with "match" to start the Secret Santa draw!

<b>Important: everyone who's willing to participate must start me in private first, otherwise I won't be \
able to send them their match!</b>"""


def bot_added(_, message: Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.is_self:
                return True


bot_added_filter = Filters.create(bot_added)


@Client.on_message(bot_added_filter)
@decorators.catch_exceptions(answer_on_flood_wait_only=True)
def on_new_group(client: Client, message: Message):
    logger.debug('entered handler')

    client.send_message(message.chat.id, NEW_CHAT_MESSAGE.format(
        shhh=Emoji.SHUSHING_FACE,
        santa=Emoji.SANTA_CLAUS_MEDIUM_LIGHT_SKIN_TONE,
        gift=Emoji.WRAPPED_GIFT
    ))


