import logging
import random
import re
from collections import defaultdict

from pyrogram import Client
from pyrogram import Message
from pyrogram import Filters
from pyrogram import Emoji
from pyrogram.errors import UserIsBlocked
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors import BadRequest

from bot import bot
from bot.utils import decorators
from bot.utils import utils
from config import config

__plugin__ = utils.plugin_name(__name__)

logger = logging.getLogger('plugin:' + __plugin__)


SECRET_SANTA_MESSAGE = """<a href="{message_link}">{chat_name}'s Secret Santa draw</a>: you are \
{receiver_mention}'s Secret Santa! {santa}{wrapped_gift}{christmas_tree}

{draw_id}"""

PAIR_RESULT = """I've been able to match <b>{number}</b> people! \
{father_christmas}{father_christmas}{father_christmas}
You should have received a message with the name of your match, go check it out :)"""

BLOCKED_US = """\n\nI have not included {blocked_us_list} in the draw because they haven't started me yet, \
or they blocked me {pensive_face}"""

OTHER_ERRORS_PREFIX = """Aaaaand also, I have excluded the following people because something went wrong with the \
matching process:"""

OTHER_ERRORS_LIST = """{users_list} (<code>{error_description}</code>)"""

NOT_ENOUGH_PEOPLE = """Uh-oh, it looks like a lot of people here didn\'t start me yet. You must be at least in two :/"""


def reply_to_our_message_test(_, message):
    return message.reply_to_message and message.reply_to_message.from_user.id == bot.me.id


def bot_command_extended_test(_, message):
    if message.text:
        return bool(re.search(r'^\/(?:pair|match|draw)(?:@{})?$'.format(bot.me.username), message.text, re.I))


reply_to_our_message_filter = Filters.create(reply_to_our_message_test)

bot_command_extended_filter = Filters.create(bot_command_extended_test)


def list_to_text(users):
    if not isinstance(users, (list, tuple)):
        users = [users]

    if len(users) == 1:
        return utils.inline_mention(users[0])

    last_item_index = len(users) - 1
    users, last_user = users[:last_item_index], users[last_item_index:][0]

    return '{} and {}'.format(
        ', '.join([utils.inline_mention(u) for u in users]),
        utils.inline_mention(last_user)
    )


@Client.on_message(
    Filters.text & Filters.group & (
        bot_command_extended_filter
        | (reply_to_our_message_filter & Filters.regex(r'^(?:pair|match|draw)\b.*', flags=re.I))
    )
)
@decorators.catch_exceptions(answer_on_flood_wait_only=True)
def on_pair(client: Client, message: Message):
    logger.debug('entered handler')

    limit = config.bot.chat_max_members + 20 + 20 + 3  # 20 bots + 20 possible deleted accounts + 3 padding
    if limit > 200:
        limit = 200

    logger.info('draw id %d: limit %d', message.message_id, limit)

    all_members = client.get_chat_members(message.chat.id, limit=limit)

    valid_members = list()
    for member in all_members:
        if member.user.is_bot or member.user.is_deleted:
            logger.debug('%s (%d) is a bot or has been deleted', member.user.first_name, member.user.id)
            continue

        logger.debug('%s (%d) is a valid user', member.user.first_name, member.user.id)
        valid_members.append(member.user)

    logger.info('number of members after removing bots and deleted accounts: %d', len(valid_members))

    if len(valid_members) > config.bot.chat_max_members:
        message.reply('Sorry, this command works only in groups with {} members or less {}'.format(
            config.bot.chat_max_members,
            Emoji.PENSIVE_FACE)
        )
        return

    chat_message = message.reply('{} <i>Pairing users...</i>'.format(Emoji.HAMMER_AND_WRENCH))

    # store the names of the users we haven't been able to contact
    blocked_us = list()
    generic_errors = defaultdict(lambda: [])

    # store the users we are allowed to message
    users_to_message = list()
    users_to_pick = list()
    for user in valid_members:
        logger.debug('testing chat action to %s (%d)', user.first_name, user.id)
        try:
            client.send_chat_action(user.id, 'typing')
            logger.debug('...success')

            users_to_message.append(user)
            users_to_pick.append(user)
        except (UserIsBlocked, PeerIdInvalid):
            logger.debug('...failed: not started yet/blocked us')
            blocked_us.append(user)
        except BadRequest as br:
            logger.error('bad request when testing chat action for user %d', user.id, exc_info=True)

            # save other errors
            error_message = re.search(r'(?:^\[.+\]: )?(.*)', str(br), re.I).group(1).strip()
            logger.debug('...failed: %s', error_message)
            generic_errors[error_message].append(user)

    number_of_users = len(users_to_message)
    logger.info('number of users involved: %d', number_of_users)
    assert(number_of_users == len(users_to_pick))

    if number_of_users < 2:
        chat_message.edit_text(NOT_ENOUGH_PEOPLE)
        return

    random.shuffle(users_to_pick)

    # we should make sure the last user of the users_to_message lists is not the
    # same of the first user of the users_to_pick list, otherwise when we loop
    # the last user of the list, the is no other user to pick (paired with self)
    while users_to_message[-1].id == users_to_pick[0].id:
        logger.info('shuffling again...')
        random.shuffle(users_to_pick)

    chat_message.edit_text('{} <i>Sending messages...</i>'.format(Emoji.HAMMER_AND_WRENCH))
    for user in users_to_message:
        pick = users_to_pick.pop()  # this is already shuffled, so we just pop the last item

        if pick.id == user.id:
            logger.info('picked self, picking again...')
            # do not pick self, pick another user and insert the old one at the end
            old_pick = pick
            new_pick = users_to_pick.pop()
            users_to_pick.append(old_pick)
            pick = new_pick

        logger.debug('picked %s (%d) for %s (%d)', pick.first_name, pick.id, user.first_name, user.id)

        text = SECRET_SANTA_MESSAGE.format(
            receiver_mention=utils.inline_mention(pick),
            chat_name=utils.html_escape(message.chat.title),
            wrapped_gift=Emoji.WRAPPED_GIFT,
            santa=Emoji.SANTA_CLAUS_MEDIUM_LIGHT_SKIN_TONE,
            christmas_tree=Emoji.CHRISTMAS_TREE,
            message_link=utils.message_link(chat_message),
            draw_id='<code>draw ID: {}</code>'.format(message.message_id) if config.public.draw_id else ''
        )

        logger.debug('sending pairing to %s (%d): %s', user.first_name, user.id, pick.first_name)
        client.send_message(user.id, text)

    text = PAIR_RESULT.format(father_christmas=Emoji.SANTA_CLAUS_MEDIUM_LIGHT_SKIN_TONE, number=len(users_to_message))

    if blocked_us:
        text += BLOCKED_US.format(blocked_us_list=list_to_text(blocked_us), pensive_face=Emoji.PENSIVE_FACE)

    chat_message.edit_text(text)

    if generic_errors:
        other_errors_texts = list()
        for error_desc, users in generic_errors.items():
            other_errors_texts.append(OTHER_ERRORS_LIST.format(
                users_list=list_to_text(users),
                error_description=error_desc
            ))

        text = '{prefix}\n{errors_list}'.format(
            prefix=OTHER_ERRORS_PREFIX,
            errors_list='\n'.join(other_errors_texts)
        )

        client.send_message(message.chat.id, text)
