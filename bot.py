from telebot import TeleBot, types
from uuid import uuid1
import logging
from db.db_handler import create_user, create_meeting, get_user, get_meetings, delete_meeting
from settings import BOT_TOKEN
from oauth import get_zoom_authorize_link
from api import get_my_zoom_info, create_zoom_meeting

logger = logging.getLogger('app_log')
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger.setLevel(logging.INFO)

options = ['Add meeting', 'Show meetings',
           'Create new meeting', 'Remove meeting']

bot = TeleBot(BOT_TOKEN, parse_mode=None)


def create_keyboard_markup(opts):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(*opts)
    return markup


options_markup = create_keyboard_markup(options)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data = {
        'telegram_id': message.from_user.id,
        'redirect_hash': uuid1(),
        'telegram_username':  message.from_user.username
    }
    try:
        user = get_user({'telegram_id': message.from_user.id})
        if user is None:
            create_user({**user_data, 'zoom_access_token': None})
            user = get_user({'telegram_id': message.from_user.id})

        if user['zoom_access_token'] is None:
            msg = bot.send_message(message.chat.id,
                                   'Please follow the link to login to zoom: {}'.format(
                                       get_zoom_authorize_link(user['redirect_hash'])),
                                   reply_markup=options_markup
                                   )
            bot.register_next_step_handler(msg, process_option_step)
        else:
            msg = bot.reply_to(message, 'Hi {}! Choose an option:'.format(
                message.from_user.username), reply_markup=options_markup)
            bot.register_next_step_handler(msg, process_option_step)
    except Exception as e:
        logger.error('Error while creating user', e)
        msg = bot.reply_to(message, 'Hi {}! Something went wrong. Please try /start again'.format(
            message.from_user.username))


def process_option_step(message):
    option = message.text
    if message.text == options[0]:
        msg = bot.reply_to(message, text='Enter meeting name')
        bot.register_next_step_handler(msg, process_input_name_step)

    if message.text == options[1]:
        try:
            meetings = get_meetings({'user_telegram_id': message.from_user.id})
            names = [m['name'] for m in meetings]
            markup = create_keyboard_markup([*names, 'Back'])
            msg = bot.reply_to(
                message, text='Here\'s your zoom meetings', reply_markup=markup)
            bot.register_next_step_handler(
                msg, process_choose_meeting_step, meetings)
        except Exception as e:
            logger.error('Error while getting meetings', e)
            msg = bot.reply_to(message, text='Something went wrong. Please try again',
                               reply_markup=options_markup)
            bot.register_next_step_handler(msg, process_option_step)
    if message.text == options[2]:
        try:
            zoom_token = get_user({'telegram_id': message.from_user.id})[
                'zoom_access_token']
            zoom_id = get_my_zoom_info(zoom_token)['id']
            new_meeting_url = create_zoom_meeting(zoom_token, zoom_id)['join_url']
            msg = bot.reply_to(message, text='Here\'s your zoom meeting link: {}'.format(new_meeting_url),
                               reply_markup=options_markup)
            bot.register_next_step_handler(msg, process_option_step)
        except Exception as e:
            logger.error('Error while creating new zoom meeting', e)
            msg = bot.reply_to(
                message, text='Something went wrong. Please try again', reply_markup=options_markup)
            bot.register_next_step_handler(msg, process_option_step)
    if message.text == options[3]:
        meetings = get_meetings({'user_telegram_id': message.from_user.id})
        names = [m['name'] for m in meetings]
        markup = create_keyboard_markup([*names, 'Back'])
        msg = bot.reply_to(
            message, text='Choose meeting to delete', reply_markup=markup)
        bot.register_next_step_handler(msg, process_delete_meeting_step)


def process_input_name_step(message):
    name = message.text
    msg = bot.reply_to(message, text='Enter meeting link')
    bot.register_next_step_handler(
        msg, process_input_link_step, {'name': name})


def process_input_link_step(message, data):
    meeting_data = {
        'link': message.text,
        'user_telegram_id': message.from_user.id,
        **data
    }
    try:
        meeting = create_meeting(meeting_data)
        msg = bot.reply_to(message, text='Meeting saved',
                           reply_markup=options_markup)
        bot.register_next_step_handler(msg, process_option_step)
    except Exception as e:
        logger.error('Error while creating meeings', e)
        msg = bot.reply_to(message, text='Something went wrong. Please try again',
                           reply_markup=options_markup)
        bot.register_next_step_handler(msg, process_option_step)


def process_choose_meeting_step(message, meetings):
    choice = message.text
    if choice == 'Back':
        msg = bot.reply_to(message, 'Choose an option:'.format(
            message.from_user.username), reply_markup=options_markup)
        bot.register_next_step_handler(msg, process_option_step)
    else:
        if len(meetings) > 0:
            meeting_link = [
                i for i in meetings if i['name'] == choice][0]['link']
            markup = create_keyboard_markup(
                [*[m['name'] for m in meetings], 'Back'])
            msg = bot.send_message(message.chat.id, 'Here\'s {} meeting link: {}'.format(
                choice, meeting_link), reply_markup=markup)
            bot.register_next_step_handler(
                msg, process_choose_meeting_step, meetings)


def process_delete_meeting_step(message):
    name_to_delete = message.text
    try:
        delete_meeting(
            {'user_telegram_id': message.from_user.id, 'name': name_to_delete})
        msg = bot.reply_to(message, text='Meeting deleted',
                           reply_markup=options_markup)
        bot.register_next_step_handler(msg, process_option_step)
    except Exception as e:
        logger.error('Error while deleting meeting', e)
        msg = bot.reply_to(message, text='Something went wrong. Please try again',
                           reply_markup=options_markup)
        bot.register_next_step_handler(msg, process_option_step)


def run_bot():
    logger.info('Starting bot')
    bot.polling(none_stop=True)
