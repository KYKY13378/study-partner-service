# src/requests.py
from src.entities import Entity
from src.subjects import Subject
from src.users import User


class StudyRequest(Entity):
    """Запрос студента на поиск партнера для учебы."""

    def __init__(
            self,
            request_id: int,
            user: User,
            subject: Subject,
            format_type: str,
            study_date: str,
    ) -> None:
        """Создать объект запроса на партнёрство.

        Args:
            request_id: Идентификатор запроса.
            user: Объект User — автор запроса.
            subject: Объект Subject — предмет изучения.
            format_type: Формат занятий (онлайн/офлайн).
            study_date: Желаемая дата в формате ДД.ММ.ГГГГ.
        """
        super().__init__(request_id)
        self.user = user
        self.subject = subject
        self.format = format_type
        self.date = study_date
        self.is_closed = False

    def close(self) -> None:
        """Закрыть запрос: партнер найден, поиск завершен."""
        self.is_closed = True

    def matches(
            self,
            subject_name: str = "",
            format_type: str = "",
    ) -> bool:
        """Проверить соответствие запроса критериям поиска.

        Args:
            subject_name: Название предмета (пусто — критерий не важен).
            format_type: Формат занятий (пусто — критерий не важен).

        Returns:
            True, если запрос подходит под заданные критерии.
        """
        if subject_name and self.subject.name.lower() != subject_name.lower():
            return False
        if format_type and self.format.lower() != format_type.lower():
            return False
        return True

    def __str__(self) -> str:
        """Вернуть строковое представление запроса."""
        status = "закрыт" if self.is_closed else "активен"
        return (f"Запрос №{self.id}: {self.user.name} ищет партнера "
                f"по предмету '{self.subject.name}' "
                f"({self.format}, {self.date}) — {status}")


def add_request(
        requests: list[StudyRequest],
        user: User,
        subject: Subject,
        format_type: str,
        study_date: str,
) -> StudyRequest:
    """Создать запрос и добавить его в коллекцию.

    Args:
        requests: Список запросов.
        user: Автор запроса.
        subject: Предмет изучения.
        format_type: Формат занятий.
        study_date: Желаемая дата.

    Returns:
        Созданный объект StudyRequest.
    """
    request = StudyRequest(
        request_id=len(requests) + 1,
        user=user,
        subject=subject,
        format_type=format_type,
        study_date=study_date,
    )
    requests.append(request)
    return request


def find_requests_by_subject(
        requests: list[StudyRequest],
        subject_name: str,
) -> list[StudyRequest]:
    """Найти запросы по названию предмета.

    Args:
        requests: Список запросов.
        subject_name: Искомый предмет.

    Returns:
        Список подходящих запросов.
    """
    return [r for r in requests if r.matches(subject_name=subject_name)]


def filter_requests_by_format(
        requests: list[StudyRequest],
        format_type: str,
) -> list[StudyRequest]:
    """Отфильтровать запросы по формату занятий.

    Args:
        requests: Список запросов.
        format_type: Формат (онлайн/офлайн).

    Returns:
        Список подходящих запросов.
    """
    return [r for r in requests if r.matches(format_type=format_type)]


def close_request(requests: list[StudyRequest], request_id: int) -> bool:
    """Найти запрос по идентификатору и закрыть его.

    Args:
        requests: Список запросов.
        request_id: Идентификатор запроса.

    Returns:
        True, если запрос найден и закрыт.
    """
    for request in requests:
        if request.id == request_id:
            request.close()
            return True
    return False


def get_partner_status(is_found: bool) -> str:
    """Вернуть текстовый статус поиска (функция из ПР1).

    Args:
        is_found: Флаг, найден ли партнер.

    Returns:
        Строка со статусом.
    """
    if is_found:
        return "Партнер найден! Можно связаться."
    return "Подходящий партнер не найден. Попробуйте изменить критерии."
