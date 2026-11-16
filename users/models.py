"""Участник сервиса; отдельная сущность от пользователя авторизации Django."""
from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    name = models.CharField("Имя", max_length=100)
    group_name = models.CharField("Учебная группа", max_length=32,
                                  blank=True, null=True, default=None)

    class Meta:
        ordering = ["pk"]
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        constraints = [models.CheckConstraint(condition=~models.Q(name=""),
                                              name="participant_name_not_empty")]

    def __str__(self):
        return f"{self.name} ({self.group_name or 'группа не указана'})"

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        self.group_name = self.group_name.strip() or None if self.group_name else None
        if not self.name:
            raise ValidationError({"name": "Укажите имя участника."})

    @property
    def group(self):
        """Совместимость с карточками ПР6, использующими user.group."""
        return self.group_name or ""
