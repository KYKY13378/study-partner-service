# src/partners.py


def add_partner(partners: list[dict], name: str, subject: str,
                format_type: str, study_date: str) -> None:
    """Добавить новый запрос на поиск партнера в список.

    Args:
        partners: Список текущих запросов (словарей).
        name: Имя пользователя.
        subject: Предмет для изучения.
        format_type: Формат занятий (онлайн/офлайн).
        study_date: Желаемая дата в формате ДД.ММ.ГГГГ.
    """
    new_partner = {
        "id": len(partners) + 1,
        "name": name,
        "subject": subject,
        "format": format_type,
        "date": study_date,
    }
    partners.append(new_partner)


def find_partners_by_subject(partners: list[dict], subject: str) -> list[dict]:
    """Найти партнеров по названию предмета.

    Args:
        partners: Список всех запросов.
        subject: Искомый предмет.

    Returns:
        Список найденных партнеров.
    """
    return [p for p in partners
            if p["subject"].lower() == subject.lower()]


def filter_partners_by_format(partners: list[dict], format_type: str) -> list[dict]:
    """Отфильтровать партнеров по формату занятий.

    Args:
        partners: Список запросов.
        format_type: Формат (онлайн/офлайн).

    Returns:
        Отфильтрованный список.
    """
    result = []
    for p in partners:
        if p["format"].lower() == format_type.lower():
            result.append(p)
    return result


def get_partner_status(is_found: bool) -> str:
    """Вернуть текстовый статус поиска.

    Args:
        is_found: Флаг, найден ли партнер.

    Returns:
        Строка со статусом.
    """
    if is_found:
        return "Партнер найден! Можно связаться."
    return "Подходящий партнер не найден. Попробуйте изменить критерии."
