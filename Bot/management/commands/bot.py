from django.core.management.base import BaseCommand
from telegram import Bot, Update, ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Filters, MessageHandler, Updater, CommandHandler, CallbackContext, InlineQueryHandler
from telegram.utils.request import Request

import logging

from django.conf import settings

from Bot.models import Appl, Message, Client

from .config import T_CHAT, C_CHAT, ADMIN_ID

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%H:%M:%S')
log = logging.getLogger(f"bot")


def log(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logging.error(f'Произошла ошибка: {e.args}')

    return inner


def message_start(update: Update, context: CallbackContext) -> None:
    context.user_data['App'] = {'who_help': None, 'id': None, 'is_start': True, 'ship': None, 'location': None}
    context.user_data['Wait_info'] = None
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='ТЕХНИКИ')],
            [KeyboardButton(text='СТАРШИЙ ШКИПЕР')],
            [KeyboardButton(text='ОСТАВИТь ЖАЛОБУ')],
        ],
        resize_keyboard=True, one_time_keyboard=True,
    )

    update.message.reply_text(
        text='Здравствуйте, выберите чья помощь вам нужна.',
        reply_markup=reply_keyboard,
    )


def handler_manger(update: Update, context: CallbackContext) -> None:
    logging.info(update.message.chat_id)
    answer = update.message.text
    if update.message.reply_to_message and update.message.chat_id in (T_CHAT, C_CHAT):
        reply = update.message.reply_to_message
        context.bot.send_message(
            chat_id=reply.forward_from.id,
            text=update.message.text,
        )
        return None
    if answer.startswith('Закрыть заявку №'):
        id_app = answer.replace('Закрыть заявку №', '')[:1]
        update.message.reply_text(text=f'Заявка №{id_app} закрыта.')
        return None
        '''TO DO: Make check for data chat type'''
    if context.user_data['App']['is_start']:
        if answer == 'ТЕХНИКИ':
            context.user_data['App']['type'] = 1
            app = Appl.objects.create()
            Message.objects.create(text=answer, app=app)
            try:
                client, _ = Client.objects.get_or_create(id=update.message.from_user.id,
                                                         telegram_username=update.message.from_user.name,
                                                         chat_id=update.message.chat_id,
                                                         app=app,
                                                         defaults={
                                                             'id': update.message.from_user.id,
                                                             'telegram_username': update.message.from_user.name,
                                                             'chat_id': update.message.chat_id
                                                         })
            except:
                client = Client.objects.get(id=update.message.from_user.id)
                client.chat_id = update.message.chat_id
                client.save()
            context.user_data['Wait_info'] = 'Ship name'
            context.user_data['App']['is_start'] = False
            context.user_data['App']['id'] = app.id
            update.message.reply_text(text='Напишите название лодки')
            return None
        elif answer == 'СТАРШИЙ ШКИПЕР':
            context.user_data['App']['type'] = 2
            app = Appl.objects.create()
            Message.objects.create(text=answer, app=app)
            try:
                client, _ = Client.objects.get_or_create(id=update.message.from_user.id,
                                                         telegram_username=update.message.from_user.name,
                                                         chat_id=update.message.chat_id,
                                                         app=app,
                                                         defaults={
                                                             'id': update.message.from_user.id,
                                                             'telegram_username': update.message.from_user.name,
                                                             'chat_id': update.message.chat_id
                                                         })
            except:
                client = Client.objects.get(id=update.message.from_user.id)
                client.chat_id = update.message.chat_id
                client.save()
            context.user_data['Wait_info'] = 'Ship name'
            context.user_data['App']['is_start'] = False
            context.user_data['App']['id'] = app.id
            update.message.reply_text(text='Напишите название лодки')
            return None
        elif answer == 'ОСТАВИТЬ ЖАЛОБУ':
            # TODO: сделать жалобу
            pass

    if context.user_data['Wait_info'] == 'Ship name':
        context.user_data['App']['ship'] = answer
        context.user_data['Wait_info'] = 'location'
        update.message.reply_text(text='Отправте ваше местоположение.')
        return None

    if context.user_data['Wait_info'] == 'location':
        context.user_data['App']['location'] = answer
        context.user_data['Wait_info'] = 'problem'
        update.message.reply_text(text='Опишите вашу проблему.')
        return None

    if context.user_data['Wait_info'] == 'problem':
        context.user_data['Wait_info'] = 'breefing'
        # TODO: сделать регистарцию заявки
        app = Appl.objects.get(id=context.user_data['App']['id'])
        app.ship = context.user_data['App']['ship']
        update.message.reply_text(text='Заявка зарегестрированна.')
        if context.user_data['App']['type'] == 1:
            context.bot.send_message(
                chat_id=T_CHAT,
                text=f"""Заявка №{app.id}"""
            )
            context.bot.forward_message(
                chat_id=T_CHAT,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

        if context.user_data['App']['type'] == 2:
            context.bot.send_message(
                chat_id=T_CHAT,
                text=f"""Заявка №{app.id}"""
            )
            context.bot.forward_message(
                chat_id=C_CHAT,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

        return None

    return None


def location_handler(update: Update, context: CallbackContext) -> None:
    if context.user_data['Wait_info'] == 'location':
        location = update.message.location.to_json()
        Message.objects.create(metadata=location)
        context.user_data['App']['location'] = update.message.location.to_json()
        context.user_data['Wait_info'] = 'problem'
        update.message.reply_text(text='Опишите вашу проблему.')
        logging.info(location)
        return None

    return None


def inline_handler(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if query in 'Закрыть заявку':
        logging.info(query)
        result = list()
        for el in Appl.objects.all():
            result.append(
                InlineQueryResultArticle(
                    id=el.id,
                    title=f'Заявка № {el.id}',
                    input_message_content=InputTextMessageContent(
                        message_text=f'Закрыть заявку №{el.id}.'
                    )
                )
            )
        update.inline_query.answer(results=result, cache_time=10)
        return None
    return None


class Command(BaseCommand):
    help = 'Телеграм бот'

    @log
    def handle(self, *args, **options):
        logging.info('Запуск бота')
        logging.info('Подключение к телеграм')
        request = Request(**{'read_timeout': 1000, 'connect_timeout': 1000})
        bot = Bot(
            request=request,
            token=settings.TG_TOKEN
        )
        logging.info('Подключение обработчика')
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        logging.info('Подключение handler к dispatcher')
        updater.dispatcher.add_handler(CommandHandler('start', callback=message_start))
        updater.dispatcher.add_handler(InlineQueryHandler(callback=inline_handler))
        updater.dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=handler_manger))
        updater.dispatcher.add_handler(MessageHandler(filters=(Filters.location | Filters.photo | Filters.video),
                                                      callback=location_handler))

        logging.info('Начинаю цикл прослушки')
        updater.start_polling()
        updater.idle()
