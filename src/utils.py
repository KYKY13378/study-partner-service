# src/utils.py
from datetime import date


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    Args:
        prompt: Текст приглашения к вводу.

    Returns:
        Введённое целое число.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите корректное целое число.")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ДД.ММ.ГГГГ.

    Args:
        prompt: Текст приглашения к вводу.

    Returns:
        Объект date.
    """
    while True:
        try:
            date_str = input(prompt)
            day, month, year = map(int, date_str.split("."))
            return date(year, month, day)
        except (ValueError, IndexError):
            print("Ошибка: введите дату в формате ДД.ММ.ГГГГ.")
