import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Location, Contact
from telegram.ext import ConversationHandler
from vars_module import *
from route_requests import create_route_request, get_similar_routes_request
from registration_requests import get_user


def add_ride(update, context):
    keyboard = [[InlineKeyboardButton("Однократна поїздка", callback_data=str(ONE_TIME))],
                [InlineKeyboardButton("Регулярна поїздка", callback_data=str(REGULAR))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Якщо ви здійснюєте цю поїздку регулярно - повідомте про це, будь ласка.',
                              reply_markup=reply_markup)
    return GET_RIDE_STATUS


def get_ride_status_and_user_id(update, context):
    query = update.callback_query
    ride_type = query.data

    if ride_type is ONE_TIME:
        context.user_data['ride_type'] = 'ONE_TIME'
        text = 'Введіть час відправлення у форматі HH.MM:'
    else:
        context.user_data['ride_type'] = 'REGULAR'
        text = 'Надішліть координати старту.'

    update.callback_query.edit_message_text(f'Тип вашої поїздки: {context.user_data["ride_type"]}\n\n{text}')

    if ride_type is ONE_TIME:
        return GET_DEPARTURE_TIME
    else:
        return GET_START_POINT


def get_departure_time(update, context):
    time_of_departure = update.message.text
    context.user_data['time_of_departure'] = time_of_departure

    update.message.reply_text(f'Час вашого відправлення:{context.user_data["time_of_departure"]}\n\n'
                              f'Будь ласка, тепер введіть дату поїздки у форматі DD.MM.YYYY')
    return GET_DEPARTURE_DATE


def get_departure_date(update, context):
    date_of_departure = update.message.text
    context.user_data['date_of_departure'] = date_of_departure

    update.message.reply_text(f'Дата вашого відправлення: {context.user_data["date_of_departure"]}.\n\n'
                              f'Тепер надішліть нам локацію місця вашого відправлення:')
    return GET_START_POINT


def get_ride_type_or_start_point(update, context):
    if update.callback_query:
        query = update.callback_query
        ride_type = query.data

        if ride_type is ONE_TIME:
            context.user_data['ride_type'] = 'ONE_TIME'
        else:
            context.user_data['ride_type'] = 'REGULAR'
        text = f'Тип вашої поїздки: {context.user_data["ride_type"]}'
        update.callback_query.edit_message_text(chat_id=update.effective_message.chat_id, text=text)
    else:
        location = update.message.location
        latitude, longitude = location.latitude, location.longitude

        # adding vars to user_data
        context.user_data['start_latitude'] = latitude
        context.user_data['start_longitude'] = longitude

    context.bot.send_message(chat_id=update.effective_message.chat_id, text='А тепер вкажіть, куди ви прямуєте:')
    return GET_FINISH_POINT


def get_finish_point_and_send_requests(update, context):
    location = update.message.location
    latitude, longitude = location.latitude, location.longitude

    context.user_data['finish_latitude'] = latitude
    context.user_data['finish_longitude'] = longitude
    context.user_data['telegram_id'] = update.effective_message.chat_id

    response = None
    if context.user_data['ride_type'] == 'ONE_TIME':
        response = create_route_request(telegram_id=context.user_data['telegram_id'],
                                        time_of_departure=context.user_data['time_of_departure'],
                                        date_of_departure=context.user_data['date_of_departure'],
                                        start_latitude=context.user_data['start_latitude'],
                                        start_longitude=context.user_data['start_longitude'],
                                        finish_latitude=context.user_data["finish_latitude"],
                                        finish_longitude=context.user_data["finish_longitude"])
    elif context.user_data['ride_type'] == 'REGULAR':
        response = create_route_request(telegram_id=context.user_data['telegram_id'],
                                        start_latitude=context.user_data['start_latitude'],
                                        start_longitude=context.user_data['start_longitude'],
                                        finish_latitude=context.user_data["finish_latitude"],
                                        finish_longitude=context.user_data["finish_longitude"])

    if response.status_code == 201:
        update.effective_message.reply_text('Маршрут успішно додано до бази даних!')
    else:
        update.effective_message.reply_text('Сталася якась помилка. Будь ласка, спробуйте пізніше. Також будьте '
                                            'уважні прі вводі часу та дати. Система сприймає дані лише у зазначеному'
                                            'форматі.')

    return get_db_response(update, context)


def get_db_response(update, context):

    # отправляем запрос на наличие совпадений -- GET
    if context.user_data['ride_type'] == 'ONE_TIME':
        response = get_similar_routes_request(telegram_id=context.user_data['telegram_id'],
                                              time_of_departure=context.user_data['time_of_departure'],
                                              date_of_departure=context.user_data['date_of_departure'],
                                              start_latitude=context.user_data['start_latitude'],
                                              start_longitude=context.user_data['start_longitude'],
                                              finish_latitude=context.user_data["finish_latitude"],
                                              finish_longitude=context.user_data["finish_longitude"])
    else:
        response = get_similar_routes_request(telegram_id=context.user_data['telegram_id'],
                                              start_latitude=context.user_data['start_latitude'],
                                              start_longitude=context.user_data['start_longitude'],
                                              finish_latitude=context.user_data["finish_latitude"],
                                              finish_longitude=context.user_data["finish_longitude"])

    context.user_data['response'] = response

    if len(context.user_data['response']):

        user_type = context.user_data['response'][0]['user']['type']

        if user_type == 'doctor':
            keyboard = [[InlineKeyboardButton("Деталі", callback_data=str(GET_DETAILS))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Ми знайшли медиків поряд з місцем вашого відправлення!',
                                      reply_markup=reply_markup)

            for route in response:
                medic_telegram_id = route['user']['telegram_id']
                context.bot.send_message(chat_id=medic_telegram_id,
                                         text="Поряд з місцем вашого відправлення знайшлися водії!\n"
                                              "Ми відправили їм ваши контакти, та інформацію про ваш маршрут.\n"
                                              "Можливо скоро з вами зв'яжуться!")

            # после отправки запроса перезаписываем содержимое user_data, чтобы передать их в get_details
            context.user_data.clear()
            context.user_data['response'] = response

            return GET_RESULT_LIST
        else:
            # отправка сообщения медику
            update.message.reply_text("Поряд з місцем вашого відправлення знайшлися водії!\n"
                                      "Ми відправили їм ваши контакти, та інформацію про ваш маршрут.\n"
                                      "Можливо скоро з вами зв'яжуться!")

            # рассылка уведомлений водителям
            for route in response:
                driver_telegram_id = route['user']['telegram_id']
                medic_user_instance = get_user(update.effective_user.id)
                data = medic_user_instance.content.decode('utf-8')
                user_instance = json.loads(data)

                location = Location(latitude=context.user_data['finish_latitude'],
                                    longitude=context.user_data['finish_longitude'])

                user_contact = Contact(phone_number=user_instance['phone_number'],
                                       first_name=user_instance['first_name'],
                                       last_name=user_instance['last_name'],
                                       user_id=user_instance['telegram_id'])

                if context.user_data.get('time_of_departure'):
                    date = context.user_data['date_of_departure']
                    time = context.user_data['time_of_departure']
                    text = f'Ми знайшли нове співпадіння за маршрутом!\n' \
                           f'Час та дата відправлення: {date}, {time}.\n' \
                           f'Місце призначення:'
                else:
                    text = 'Ми знайшли нове співпадіння за маршрутом!\n' \
                           'Регулярна поїздка.\n' \
                           'Місце призначення:'

                context.bot.send_message(chat_id=driver_telegram_id, text=text)
                context.bot.send_location(chat_id=driver_telegram_id, location=location)
                context.bot.send_contact(chat_id=driver_telegram_id, contact=user_contact)

                context.bot.send_message(chat_id=driver_telegram_id,
                                         text="Перегляньте місця призначення. Якщо вам по дорозі, "
                                              "будь ласка, зв'яжіться з медиком, аби домовитися про "
                                              "поїздку!")

                context.user_data.clear()
            return ConversationHandler.END
    else:
        update.message.reply_text('Наразі у систумі немає Ваших попутників. Ми повідомимо, коли такі знайдуться.')
        context.user_data.clear()
        return ConversationHandler.END










