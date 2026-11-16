"""Предмет и обратная связь с учебными запросами."""
from django.core.exceptions import ValidationError
from django.db import models


class Subject(models.Model):
    name = models.CharField("Название", max_length=120)

    class Meta:
        ordering = ["pk"]
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        constraints = [models.CheckConstraint(condition=~models.Q(name=""),
                                              name="subject_name_not_empty")]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Укажите название предмета."})
