"""Статусы: перенос завершенности до удаления старого булева поля."""
from django.db import migrations, models


def forward_statuses(apps, schema_editor):
    Request = apps.get_model("requests", "StudyRequest")
    items = Request.objects.using(schema_editor.connection.alias)
    items.filter(is_closed=True).update(status="completed")
    items.filter(is_closed=False).update(status="active")


def reverse_statuses(apps, schema_editor):
    Request = apps.get_model("requests", "StudyRequest")
    items = Request.objects.using(schema_editor.connection.alias)
    items.filter(status="active").update(is_closed=False)
    items.exclude(status="active").update(is_closed=True)


class Migration(migrations.Migration):
    dependencies = [("requests", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="studyrequest", name="status",
            field=models.CharField(choices=[("active", "Активен"), ("cancelled", "Отменён"),
                                            ("completed", "Завершён")],
                                   default="active", max_length=12, verbose_name="Статус"),
        ),
        migrations.RunPython(forward_statuses, reverse_statuses),
        migrations.RemoveConstraint(model_name="studyrequest", name="request_closed_boolean"),
        migrations.RemoveIndex(model_name="studyrequest", name="req_subject_status_idx"),
        migrations.RemoveIndex(model_name="studyrequest", name="req_user_date_idx"),
        migrations.RemoveField(model_name="studyrequest", name="is_closed"),
        migrations.AddIndex(model_name="studyrequest", index=models.Index(
            fields=["subject", "status"], name="req_subject_state_idx")),
        migrations.AddIndex(model_name="studyrequest", index=models.Index(
            fields=["user", "study_date", "status"], name="req_user_day_state_idx")),
        migrations.AddConstraint(model_name="studyrequest", constraint=models.CheckConstraint(
            condition=models.Q(status__in=["active", "cancelled", "completed"]),
            name="request_status_valid")),
    ]
