import logging
import os
import time
# from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get("homework_name")
    if not homework_name:
        err_text = 'Свойства homework_name не существует'
        logging.error(err_text)
        return(err_text)
    statuses = {
        "rejected": 'К сожалению в работе нашлись ошибки.',
        "approved": ('Ревьюеру всё понравилось, можно '
                     'приступать к следующему уроку.'),
        "reviewing": 'Ревьюер приступил к проверке',
    }
    status = homework.get("status")
    if not status:
        err_text = 'Свойства status не существует'
        logging.error(err_text)
        return(err_text)
    if status in statuses:
        verdict = statuses[status]
    else:
        err_text = 'Неизвестный статус'
        logging.error(err_text)
        return err_text
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'},
        )
        return homework_statuses.json()
    except Exception:
        logging.exception()
        return {}
    except ValueError:
        logging.exception()
        return {}


def send_message(message, bot_client):
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0  # int(time.time())
    i = 0
    while i < 2:
        logging.debug('Программа запущена')
        try:
            new_homework = get_homework_statuses(current_timestamp, bot)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot
                )
                logging.info('Сообщение отправлено')
            if new_homework.get("current_date"):
                current_timestamp = new_homework.get("current_date")
            else:
                current_timestamp = int(time.time())
            # time.sleep(900)
            time.sleep(1)

        except Exception as error:
            logging.exception()
            send_message(
                f'Бот столкнулся с ошибкой: {error}',
                bot,
            )
            time.sleep(5)
        i += 1


if __name__ == '__main__':
    main()
