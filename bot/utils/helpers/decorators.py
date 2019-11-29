import logging
from functools import wraps

from pyrogram import Client
from pyrogram import Message
from pyrogram import ContinuePropagation
from pyrogram.errors import FloodWait

from .mwt import MWT
from config import config


logger = logging.getLogger(__name__)


def admin(permission=None, warn=False):
    def real_decorator(func):
        @wraps(func)
        def wrapped(client: Client, message: Message, *args, **kwargs):
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            if user_id in config.telegram.admins:
                logger.debug('%d is admin in %d', user_id, chat_id)
                return func(client, message, *args, **kwargs)
    
            @MWT(timeout=60 * 60 * 4)
            def get_admins(ids_only=False):
                logger.debug('executing get_chat_members request')
                
                chat_admins = client.get_chat_members(chat_id, filter='administrators')
                if ids_only:
                    return [a.user.id for a in chat_admins]
                
                return chat_admins
            
            admins = get_admins(ids_only=permission)  # we just need the admins IDs if we don't have to check the permissions
            if not permission and user_id in admins:
                logger.debug('%d is admin in %d', user_id, chat_id)
                return func(client, message, *args, **kwargs)
            elif permission:
                chat_member = [a for a in admins if a.user.id == user_id][0]  # get the ChatMember object of the user
                
                if getattr(chat_member, permission, False):
                    logger.debug('%d is admin in %d and has the %s permission', user_id, chat_id, permission)
                    return func(client, message, *args, **kwargs)
            
            # if warn is True, warn the user and do not continue the propagation. Otherwise,
            # just continue to propagate the update
            if warn:
                message.reply('You are not allowed to use this command')
            else:
                raise ContinuePropagation

        return wrapped

    return real_decorator


def catch_exceptions(answer=True, answer_on_flood_wait_only=False):
    def real_decorator(func):
        @wraps(func)
        def wrapped(client, message, *args, **kwargs):
            try:
                return func(client, message, *args, **kwargs)
            except NotImplementedError:
                message.reply('Whoa whoa whoa slow down, buddy. I\'m not ready for this yet', quote=True)
            except FloodWait as fw:
                logger.error('error while running handler callback: FloodWait', exc_info=True)

                if answer or answer_on_flood_wait_only:
                    message.reply(
                        'Oops, it looks like I\'m a bit overheated, I\'m sorry. I need some rest. Retry in some minutes!',
                        quote=True
                    )
            except Exception as e:
                error_str = str(e) or 'you fucked up big time, buddy'
                logger.error('error while running handler callback: %s', error_str, exc_info=True)
                if answer:
                    text = 'Whoops, something went wrong: <code>{}</code>'.format(error_str)
                    if config.public.report_errors_to:
                        text += '\nIf you think this is a bug, please report the error <a href="">here</a>!'.format(
                            config.public.report_errors_to
                        )

                    message.reply(text, quote=True)

        return wrapped

    return real_decorator
