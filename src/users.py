# src/users.py
from src.entities import Entity


class User(Entity):
    """Студент — пользователь сервиса поиска партнеров."""

    def __init__(self, user_id: int, name: str, group: str) -> None:
        """Создать объект пользователя.

        Args:
            user_id: Идентификатор пользователя.
            name: Имя пользователя.
            group: Учебная группа.
        """
        super().__init__(user_id)
        self.name = name
        self.group = group

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"{self.name} (группа {self.group})"

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать объект User из словаря данных JSON.

        Args:
            data: Словарь с ключами id, name, group.

        Returns:
            Новый объект User.
        """
        return cls(user_id=data["id"], name=data["name"], group=data["group"])


def add_user(users: list[User], name: str, group: str) -> User:
    """Создать пользователя и добавить его в коллекцию.

    Args:
        users: Список пользователей.
        name: Имя пользователя.
        group: Учебная группа.

    Returns:
        Созданный объект User.
    """
    user = User(user_id=len(users) + 1, name=name, group=group)
    users.append(user)
    return user


def find_user_by_id(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по идентификатору.

    Args:
        users: Список пользователей.
        user_id: Искомый идентификатор.

    Returns:
        Объект User или None, если не найден.
    """
    for user in users:
        if user.id == user_id:
            return user
    return None
