import os

import logging
import time
import requests
import telegram

from exception import (PrakticumTokenException, TelegramBotTokenException,
                       TelegramChatException, HomeworkError, ApiException)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)

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
    """Проверяет доступность переменных окружения"""
    if PRACTICUM_TOKEN is None:
        logging.critical('PRACTICUM_TOKEN не найден')
        raise PrakticumTokenException('PRACTICUM_TOKEN не найден')
    if TELEGRAM_TOKEN is None:
        logging.critical('TELEGRAM_TOKEN не найден')
        raise TelegramBotTokenException('TELEGRAM_TOKEN не найден')
    if TELEGRAM_CHAT_ID is None:
        logging.critical('TELEGRAM_CHAT_ID не найден')
        raise TelegramChatException('TELEGRAM_CHAT_ID не найден')
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug("Сообщение отправлено")
    except Exception as error:
        logging.error(f'Бот не смог отправить сообщение:{error}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту"""
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params={'from_date': timestamp})
    except requests.RequestException:
        logging.error('Бот не смог отправить сообщение')
    if response.status_code != 200:
        raise ApiException("API недоступен")
    return response.json()


def check_response(response):
    """Проверка соответствия API"""
    if not isinstance(response, dict):
        raise TypeError('')
    if response.get('homeworks') is None:
        logging.error('Ошибка в ключе homework')
        raise HomeworkError('Ошибка в ключе homework')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Ошибка типа данных')
    if response['homeworks'] == []:
        return {}
    status = response.get('homeworks')[0].get('status')
    if status not in HOMEWORK_VERDICTS:
        logging.error(f'Ошибка статуса {status}')
        raise HomeworkError('Ошибка в статусе homework')


def parse_status(homework):
    """Изменение статуса работы"""
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
    while True:
        try:
            homeworks = get_api_answer(timestamp)
            check_response(homeworks)

            if len(homeworks) != 0:
                homework = homeworks['homeworks'][0]
                new_status = parse_status(homework)
                send_message(bot, new_status)
            logging.debug('izm sat')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
