"""Создать группы для просмотра и координации без прав удаления и управления auth."""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        for name, actions in (
            ("Наблюдатели сервиса", ("view",)),
            ("Координаторы сервиса", ("view", "add", "change")),
        ):
            group, _ = Group.objects.get_or_create(name=name)
            permissions = Permission.objects.filter(
                content_type__app_label__in=["users", "subjects", "requests"],
                codename__in=[f"{action}_{model}" for action in actions
                              for model in ("user", "subject", "studyrequest")],
            )
            group.permissions.set(permissions)
            self.stdout.write(f"{name}: {permissions.count()} разрешений.")
