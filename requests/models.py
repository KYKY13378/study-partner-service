"""Учебный запрос с двумя связями многие-к-одному."""
from django.db import models


class StudyRequest(models.Model):
    class Format(models.TextChoices):
        ONLINE = "онлайн", "Онлайн"
        OFFLINE = "офлайн", "Офлайн"

    user = models.ForeignKey("users.User", on_delete=models.PROTECT,
                             related_name="study_requests", verbose_name="Автор")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.PROTECT,
                                related_name="study_requests", verbose_name="Предмет")
    format = models.CharField("Формат занятий", max_length=6, choices=Format.choices)
    study_date = models.DateField("Дата занятия", db_index=True)
    is_closed = models.BooleanField("Поиск завершён", default=False)

    class Meta:
        ordering = ["study_date", "pk"]
        verbose_name = "Учебный запрос"
        verbose_name_plural = "Учебные запросы"
        indexes = [
            models.Index(fields=["subject", "is_closed"], name="req_subject_status_idx"),
            models.Index(fields=["user", "study_date", "is_closed"], name="req_user_date_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(format__in=["онлайн", "офлайн"]),
                                   name="request_format_valid"),
            models.CheckConstraint(condition=models.Q(is_closed__in=[True, False]),
                                   name="request_closed_boolean"),
        ]

    def __str__(self):
        return f"№{self.pk}: {self.subject} / {self.user.name} / {self.study_date}"

    @property
    def study_day(self):
        """DateField сразу возвращает date; фильтр шаблона ПР6 сохранён."""
        return self.study_date

    @property
    def date(self):
        """Прежнее представление даты для быстрого поиска в карточках ПР6."""
        return self.study_date.strftime("%d.%m.%Y")

    def close(self):
        """Закрыть поиск и сохранить изменение через ORM."""
        self.is_closed = True
        self.save(update_fields=["is_closed"])
