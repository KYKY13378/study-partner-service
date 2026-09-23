# src/entities.py
class Entity:
    """Базовый класс сущностей проекта с идентификатором."""

    def __init__(self, entity_id: int) -> None:
        """Сохранить идентификатор сущности.

        Args:
            entity_id: Уникальный идентификатор сущности.
        """
        self.id = entity_id

    def __str__(self) -> str:
        """Вернуть базовое строковое представление сущности."""
        return f"{self.__class__.__name__} №{self.id}"

    @classmethod
    def from_data(cls, data: dict) -> "Entity":
        """Создать объект из словаря с ключом id.

        Args:
            data: Словарь с данными сущности.

        Returns:
            Новый объект вызванного класса.
        """
        return cls(entity_id=data["id"])
