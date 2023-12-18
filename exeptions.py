class BadResponse(Exception):
    """Исключение для кодов отличных от 200."""

    pass


class FailSendMessage(Exception):
    """Исключение для ошибки при отправке сообщения."""

    pass
