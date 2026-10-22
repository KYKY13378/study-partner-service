# src/subjects.py
from src.entities import Entity


class Subject(Entity):
    """Учебная дисциплина, по которой ищется партнер."""

    def __init__(self, subject_id: int, name: str) -> None:
        """Создать объект предмета.

        Args:
            subject_id: Идентификатор предмета.
            name: Название предмета.
        """
        super().__init__(subject_id)
        self.name = name

    def __str__(self) -> str:
        """Вернуть строковое представление предмета."""
        return self.name

    @classmethod
    def from_data(cls, data: dict) -> "Subject":
        """Создать объект Subject из словаря данных JSON.

        Args:
            data: Словарь с ключами id, name.

        Returns:
            Новый объект Subject.
        """
        return cls(subject_id=data["id"], name=data["name"])


def add_subject(subjects: list[Subject], name: str) -> Subject:
    """Создать предмет и добавить его в коллекцию.

    Args:
        subjects: Список предметов.
        name: Название предмета.

    Returns:
        Созданный объект Subject.
    """
    subject_id = max((subject.id for subject in subjects), default=0) + 1
    subject = Subject(subject_id=subject_id, name=name)
    subjects.append(subject)
    return subject


def find_subject_by_id(subjects: list[Subject], subject_id: int) -> Subject | None:
    """Найти предмет по идентификатору.

    Args:
        subjects: Список предметов.
        subject_id: Искомый идентификатор.

    Returns:
        Объект Subject или None, если не найден.
    """
    for subject in subjects:
        if subject.id == subject_id:
            return subject
    return None


def find_subject_by_name(subjects: list[Subject], name: str) -> Subject | None:
    """Найти предмет по названию без учета регистра.

    Args:
        subjects: Список предметов.
        name: Искомое название.

    Returns:
        Объект Subject или None, если не найден.
    """
    for subject in subjects:
        if subject.name.lower() == name.lower():
            return subject
    return None
