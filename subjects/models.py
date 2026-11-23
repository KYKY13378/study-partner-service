"""Предмет и обратная связь с учебными запросами."""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode
from uuid import uuid4


class Subject(models.Model):
    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("URL-идентификатор", max_length=180, unique=True, editable=False)

    class Meta:
        ordering = ["pk"]
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        constraints = [models.CheckConstraint(condition=~models.Q(name=""),
                                              name="subject_name_not_empty")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(unidecode(self.name))[:140] or "subject"
            # UUID доступен до INSERT; промежуточная пустая уникальная строка не нужна.
            suffix = str(self.pk) if self.pk else uuid4().hex
            self.slug = f"{base}-{suffix}"
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"slug"}
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("subjects:detail_slug", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Укажите название предмета."})
