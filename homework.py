import json
import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exception import (ApiException, HomeworkError, PrakticumTokenException,
                       TelegramBotTokenException, TelegramChatException)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log',
                              maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logger.critical('PRACTICUM_TOKEN не найден')
        raise PrakticumTokenException('PRACTICUM_TOKEN не найден')
    if TELEGRAM_TOKEN is None:
        logger.critical('TELEGRAM_TOKEN не найден')
        raise TelegramBotTokenException('TELEGRAM_TOKEN не найден')
    if TELEGRAM_CHAT_ID is None:
        logger.critical('TELEGRAM_CHAT_ID не найден')
        raise TelegramChatException('TELEGRAM_CHAT_ID не найден')
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug("Сообщение отправлено")
        logging.debug("Сообщение отправлено")
    except Exception as error:
        logger.error(f'Бот не смог отправить сообщение:{error}')
        raise TelegramError


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту."""
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params={'from_date': timestamp})
        response.json()
    except requests.RequestException:
        logger.error('Бот не смог отправить сообщение')
    except json.errors.JSONDecodeError:
        logger.error('Не удалось преобразовать в JSON')
        raise ValueError
    if response.status_code != HTTPStatus.OK:
        raise ApiException("API недоступен")
    return response.json()


def check_response(response):
    """Проверка соответствия API."""
    if not isinstance(response, dict):
        raise TypeError('Ошибка типа данных')
    if response.get('homeworks') is None:
        logger.error('Ошибка в ключе homework')
        raise HomeworkError('Ошибка в ключе homework')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Ошибка типа данных')
    if not response['homeworks']:
        raise ValueError('Пустой список')
    return response['homeworks'][0]


def parse_status(homework):
    """Изменение статуса работы."""
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS.get(status)
    if status not in HOMEWORK_VERDICTS.keys():
        raise NameError("Неожиданный статус дз")
    if homework_name is None:
        raise ValueError("Неожиданный статус дз")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)

            if homework:
                message = parse_status(homework)
            else:
                message = 'Статус не изменен'
            if message != last_message:
                send_message(bot, message)
                last_message = message
            logger.debug(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            raise error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
