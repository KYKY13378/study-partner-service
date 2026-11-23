"""Учебный запрос с двумя связями многие-к-одному."""
from django.db import models


class StudyRequestQuerySet(models.QuerySet):
    """Повторно используемые условия возвращают ленивые QuerySet."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, day):
        return self.filter(study_date=day)


class StudyRequestManager(models.Manager.from_queryset(StudyRequestQuerySet)):
    pass


class StudyRequest(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        CANCELLED = "cancelled", "Отменён"
        COMPLETED = "completed", "Завершён"

    class Format(models.TextChoices):
        ONLINE = "онлайн", "Онлайн"
        OFFLINE = "офлайн", "Офлайн"

    user = models.ForeignKey("users.User", on_delete=models.PROTECT,
                             related_name="study_requests", verbose_name="Автор")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.PROTECT,
                                related_name="study_requests", verbose_name="Предмет")
    format = models.CharField("Формат занятий", max_length=6, choices=Format.choices)
    study_date = models.DateField("Дата занятия", db_index=True)
    status = models.CharField("Статус", max_length=12, choices=Status.choices,
                              default=Status.ACTIVE)

    objects = StudyRequestManager()

    class Meta:
        ordering = ["study_date", "pk"]
        verbose_name = "Учебный запрос"
        verbose_name_plural = "Учебные запросы"
        indexes = [
            models.Index(fields=["subject", "status"], name="req_subject_state_idx"),
            models.Index(fields=["user", "study_date", "status"], name="req_user_day_state_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(format__in=["онлайн", "офлайн"]),
                                   name="request_format_valid"),
            models.CheckConstraint(
                condition=models.Q(status__in=["active", "cancelled", "completed"]),
                name="request_status_valid"),
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

    @property
    def is_closed(self):
        """Совместимость чтения ПР6; единственный источник состояния — status."""
        return self.status != self.Status.ACTIVE

    @property
    def status_label(self):
        return self.get_status_display()

    def close(self):
        """Закрыть поиск и сохранить изменение через ORM."""
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])
