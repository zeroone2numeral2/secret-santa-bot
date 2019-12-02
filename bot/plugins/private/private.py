import logging

from pyrogram import Client
from pyrogram import Message
from pyrogram import Filters
from pyrogram import Emoji

from bot.utils import decorators
from bot.utils import utils
from config import config

__plugin__ = utils.plugin_name(__name__)

logger = logging.getLogger('plugin:' + __plugin__)

START_MESSAGE = """Hello {first_name}!
I can help you organize a <b>Secret Santa</b> {shhh}{santa}{gift} in your group chats :)
Just add me to a chat and I'll tell you what to do.

Use /help for more info"""

HELP_MESSAGE = """There isn't much to say about the bot: you add it to a group and answer to one of its messages with \
"match" (or "draw", or "pair"). It will get the list of the chat members and send them their match via \
private message, anonymously. Using /match, /pair and /draw works too.

{} <b>Important</b>: the bot will include in the draw only the people he is able to message, \
that is, those who already started it. That's because bots cannot initiate a conversation with an user, \
the user must be the one who starts it.

If you want to <b>not</b> be included in a Secret Santa draw, just block the bot. He will not include you in the draw.

The bot will not work on groups with more than {} members because, when the people to message are too many, \
Telegram will start to rate-limit your bot. Secret Santas are usually organized in small groups of friends, so \
I think that's a fair number.

This bot doesn't store <i>any</i> data about the users and it only logs runtime errors. \
Everything is done in real time so there's no need to store anything"""

GROUP_COMMAND = """{} You have to use this command in a group where you've added me!
/help for more info"""


@Client.on_message(Filters.text & Filters.private & Filters.command(['start'], prefixes=['/']))
@decorators.catch_exceptions()
def on_start(_, message: Message):
    logger.debug('entered handler')

    text = START_MESSAGE.format(
        first_name=utils.html_escape(message.from_user.first_name),
        santa=Emoji.SANTA_CLAUS_MEDIUM_LIGHT_SKIN_TONE,
        shhh=Emoji.SHUSHING_FACE,
        gift=Emoji.WRAPPED_GIFT
    )

    if config.public.source_code:
        text += '. Source code <a href="{}">here</a>'.format(config.public.source_code)

    message.reply(text, disable_web_page_preview=True)


@Client.on_message(Filters.text & Filters.private & Filters.command(['help'], prefixes=['/']))
@decorators.catch_exceptions()
def on_help(_, message: Message):
    logger.debug('entered handler')

    message.reply(HELP_MESSAGE.format(Emoji.WARNING, config.bot.chat_max_members))


@Client.on_message(Filters.text & Filters.private & Filters.command(['pair', 'draw', 'match'], prefixes=['/']))
@decorators.catch_exceptions()
def on_group_command(_, message: Message):
    logger.debug('entered handler')

    message.reply(GROUP_COMMAND.format(Emoji.CROSS_MARK), disable_web_page_preview=True)
