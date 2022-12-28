import logging
import time
import requests

from . import exception

load_dotenv()


PRACTICUM_TOKEN = ...
TELEGRAM_TOKEN = ...
TELEGRAM_CHAT_ID = ...

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
        raise exception.PrakticumTokenException('PRACTICUM_TOKEN не найден')
    if TELEGRAM_TOKEN is None:
        logging.critical('TELEGRAM_TOKEN не найден')
        raise exception.TelegramBotTokenException('TELEGRAM_TOKEN не найден')
    if TELEGRAM_CHAT_ID is None:
        logging.critical('TELEGRAM_CHAT_ID не найден')
        raise exception.TelegramChatException('TELEGRAM_CHAT_ID не найден') 
    return True           



def send_message(bot, message):
    """Отправляет сообщение в Telegram чат"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Бот не смог отправить сообщение:{error}') 
        bot.send_message(TELEGRAM_CHAT_ID, error)


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту"""
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params={'from_date': timestamp})
    return homework_statuses.json()

def check_response(response):
    if not isinstance(response, dict):
        raise TypeError('')
    if response.get('homeworks') is None:
        $$$logger.error('$$$$') 
        raise $$$$   
    if not isinstance(response['homework'], list):
        raise TypeError('') 
    if response['homework']==[]:
        return {}
    status=response['homework'][0].get('status')
    if status not in HOMEWORK_VERDICTS:
        $$$logger.error(f'Ошибка статуса {status}')
        raise ####@@@@
    return response['homework'][0]





def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:
            send_message(bot,message)
            time.sleep(RETRY_PERIOD)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        else:
            #soobshenie otpravleno


if __name__ == '__main__':
    main()
