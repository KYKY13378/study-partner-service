"""Транзакционный перенос ПР7 в новые таблицы Django с сохранением ID."""
from datetime import date
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import connection, transaction

from db.inspect_source_db import SOURCE_DB, read_source
from requests.models import StudyRequest
from subjects.models import Subject
from users.models import User


def transfer_to_orm(source=SOURCE_DB, *, only_if_empty=False):
    """Не перезаписывать ORM-данные: конфликт ID с иными полями — ошибка."""
    if Path(source).resolve() == Path(str(connection.settings_dict["NAME"])).resolve():
        raise ValueError("Источник ПР7 и база ORM должны быть разными файлами.")
    with transaction.atomic():
        if only_if_empty and any(model.objects.exists() for model in (User, Subject, StudyRequest)):
            return {"skipped": "ORM-база уже содержит данные; автоматический импорт пропущен."}
        source_data = read_source(source)
        created, existing = {}, {}

        def copy(model, records):
            created[model._meta.label] = 0
            existing[model._meta.label] = 0
            for pk, fields in records:
                old = model.objects.filter(pk=pk).first()
                if old is not None:
                    if any(getattr(old, name) != value for name, value in fields.items()):
                        raise ValueError(f"Конфликт {model._meta.label} id={pk}: "
                                         "поля отличаются. Существующие данные не перезаписаны.")
                    existing[model._meta.label] += 1
                    continue
                item = model(pk=pk, **fields)
                item.full_clean()
                item.save(force_insert=True)
                created[model._meta.label] += 1

        copy(User, [(row["id"], {"name": row["name"], "group_name": row["group_name"] or None})
                    for row in source_data["users"]])
        copy(Subject, [(row["id"], {"name": row["name"]}) for row in source_data["subjects"]])
        requests = []
        for row in source_data["study_requests"]:
            if row["is_closed"] not in (0, 1):
                raise ValidationError("Некорректный статус запроса в исходной базе.")
            requests.append((row["id"], {
                "user_id": row["user_id"], "subject_id": row["subject_id"],
                "format": row["format"], "study_date": date.fromisoformat(row["study_date"]),
                "status": (StudyRequest.Status.COMPLETED if row["is_closed"]
                           else StudyRequest.Status.ACTIVE),
            }))
        copy(StudyRequest, requests)
        return {"created": created, "existing": existing}
