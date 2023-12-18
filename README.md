# Telegram-bot

Данный Telegram-bot обращается к API сервиса Практикум.Домашка и узнает статус проверки проекта: взят ли проект в ревью, проверен ли он, а если проверен — то принял его ревьюер или вернул на доработку.

Telegram-bot :
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленного на ревью проекта;
- при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
- логирует свою работу и сообщает о важных проблемах сообщением в Telegram.


## Используемые технологии

- python 3.9.6;
 
 
## Особенности реализации

- функция main(): основная логика работы программы. Все остальные функции должны запускаться из неё. Последовательность действий в общем виде:
    1) сделать запрос к API;
    2) проверить ответ;
    3) если есть обновления — получить статус работы из обновления и отправить сообщение в Telegram;
    4) подождать некоторое время и вернуться в пункт 1.

- функция check_tokens(): проверяет доступность переменных окружения, которые необходимы для работы программы. Если отсутствует хотя бы одна переменная окружения — продолжать работу бота нет смысла;

- функция get_api_answer(): делает запрос к единственному эндпоинту API-сервиса. В качестве параметра в функцию передается временная метка. В случае успешного запроса должна вернуть ответ API, приведя его из формата JSON к типам данных Python;

- функция check_response(): проверяет ответ API на соответствие документации из урока API сервиса Практикум.Домашка. В качестве параметра функция получает ответ API, приведенный к типам данных Python;

- функция parse_status(): извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_VERDICTS;

- функция send_message(): отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.


## Для запуска проекта

- склонировать репозиторий:

```bash
git clone git@github.com:ekblb/homework_bot.git
```

- установить и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```

- установить зависимости:
```bash
pip install -r requirements.txt
```

- создать файл со следующими данными:
```bash
PRACTICUM_TOKEN = example
TELEGRAM_TOKEN = example
TELEGRAM_CHAT_ID = example
```

- применить команду запуска:
```bash
python homework.py
```


Екатерина Балабаева
balabaeva.e.yu@yandex.ru