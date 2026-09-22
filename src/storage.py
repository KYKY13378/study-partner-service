# src/storage.py
import json
import os


def load_data(filename: str) -> list | dict:
    """Загрузить данные из JSON-файла.

    Args:
        filename: Путь к файлу.

    Returns:
        Данные из файла (список или словарь). Если файл не найден
        или поврежден, возвращает пустой список.
    """
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f"Ошибка: файл {filename} поврежден.")
        return []


def save_data(filename: str, data: list | dict) -> None:
    """Сохранить данные в JSON-файл.

    Args:
        filename: Путь к файлу.
        data: Данные для сохранения (список или словарь).
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка записи в файл {filename}: {e}")
