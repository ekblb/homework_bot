import logging
import os
import sys
import time
from exeptions import BadResponse, FailSendMessage

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus


load_dotenv()

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
    """Проверка доступности переменных окружения."""
    missing_tokens = []
    env_vars = {
        'practicum_token': PRACTICUM_TOKEN,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
    }
    logging.debug('Начало проверки доступности переменных окружения')
    for key, value in env_vars.items():
        if not value:
            missing_tokens.append(key)
    if missing_tokens:
        logging.critical(
            f'Отсутствие обязательных переменных окружения {missing_tokens}'
        )
        sys.exit('Недостаточно переменных окружения')
    logging.debug('Проверка доступности переменных окружения прошла успешно')


def get_api_answer(timestamp):
    """Отправка запроса к API."""
    try:
        logging.debug('Начало отправки запроса к API')
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        raise f'Недоступность эндпоинта {ENDPOINT} ({error})'
    if response.status_code != HTTPStatus.OK:
        raise BadResponse(
            f'Получен код ответа {response.status_code}'
        )
    logging.debug('Успешное получение ответа')
    try:
        return response.json()
    except requests.JSONDecodeError as error:
        raise f'Невозможно привести ответ из формата JSON ({error})'


def check_response(response):
    """Проверка ответа на соответствие документации."""
    key_homeworks = 'homeworks'
    key_current_date = 'current_date'
    logging.debug('Начало проверки ответа на соответствие документации')
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарем')
    if key_homeworks not in response or key_current_date not in response:
        raise KeyError('Отсутствие ожидаемых ключей в ответе API')
    if not isinstance(response.get(key_homeworks), list):
        raise TypeError(f'Ответ не содержит список {key_homeworks}')
    logging.debug('Проверка структуры ответа прошла успешно')


def parse_status(homework):
    """Извлечение статуса из домашней работы."""
    logging.debug('Начало извлечения статуса из домашней работы')
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ homework_name в ответе API')
    homework_name = homework['homework_name']
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(
            f'Неожиданный статус - {status} - домашней работы в ответе API'
        )
    verdict = HOMEWORK_VERDICTS[status]
    return (f'Изменился статус проверки работы '
            f'"{homework_name}". {verdict}')


def send_message(bot, message):
    """Отправка сообщения в чат."""
    logging.debug('Начало отправки сообщения в чат')
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        logging.error(f'Сбой при отправке сообщения в Telegram {error}')
        raise FailSendMessage(
            f'Сбой при отправке сообщения в Telegram {error}'
        )
    logging.debug(f'Удачная отправка сообщения в Telegram: "{message}"')


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    timestamp = int(time.time())
    last_message = ''

    while True:
        try:
            response_api = get_api_answer(timestamp)
            check_response(response_api)
            homeworks = response_api.get('homeworks')
            if homeworks:
                homework = homeworks[0]
                message_status_homework = parse_status(homework)
                logging.debug('Статус из домашней работы успешно извлечен')
                if last_message != message_status_homework:
                    try:
                        send_message(bot, message_status_homework)
                    except FailSendMessage:
                        pass
                    last_message = message_status_homework
            else:
                time.sleep(RETRY_PERIOD)
                logging.debug('Отсутствие в ответе новых статусов')
            timestamp = int(time.time())
        except FailSendMessage:
            logging.error(
                'Timestamp не обновлен из-за сбоя отправки сообщения.'
                'Повторная отправка через 10 минут.'
            )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.debug('Сформировано сообщение "Сбой в работе программы"')
            if last_message != message:
                send_message(bot, message)
                last_message = message
            logging.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(stream=sys.stdout)]
    )
    main()
