import logging
import time

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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Бот не смог отправить сообщение:{error}') 
        bot.send_message(TELEGRAM_CHAT_ID, error)


def get_api_answer(timestamp):
    ...


def check_response(response):
    ...


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
            logging.debug(message)
        ...


if __name__ == '__main__':
    main()
