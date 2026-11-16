"""Воспроизводимая демонстрация ORM и CRUD с обязательным откатом тестовых изменений."""
from datetime import date

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.deletion import ProtectedError

from requests import queries
from requests.models import StudyRequest
from subjects.models import Subject
from users.models import User


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        def show(title, queryset, fields=("pk",)):
            self.stdout.write(f"\n=== {title} ===")
            self.stdout.write(str(queryset.query))
            result = []
            for item in queryset:
                result.append({field: getattr(item, field) for field in fields}
                              if hasattr(item, "_meta") else item)
            self.stdout.write(str(result))

        show("Список предметов", queries.get_subjects(), ("pk", "name"))
        show("Авторы: values", queries.get_users())
        show("Все запросы и select_related", queries.get_requests())
        show("Один фильтр: активные", queries.get_requests("active"))
        show("Закрытые", queries.get_requests("closed"))
        show("Несколько условий", queries.filter_requests(queries.get_requests("active"), {
            "date": date(2026, 9, 18), "subject": 1, "format": "онлайн",
        }))
        show("Поиск через Q по связанным полям", queries.filter_requests(
            queries.get_requests(), {"q": "математика"}))
        for key in queries.SORT_FIELDS:
            show(f"Сортировка {key}", queries.sort_requests(queries.get_requests(), key))
        subject = Subject.objects.first()
        if subject:
            show("Обратная связь", queries.get_requests_for_subject(subject))
        show("Срез трёх последних", queries.get_recent_requests())
        self.stdout.write(f"\nАгрегаты: {queries.request_totals()}; {queries.catalog_totals()}")
        show("Статистика предметов, в том числе с нулём", queries.subject_statistics(),
             ("pk", "name", "active_count"))
        show("Статистика участников", queries.user_statistics(), ("pk", "name", "total", "active"))
        show("HAVING: минимум два активных", queries.popular_subjects(2),
             ("pk", "name", "active_count"))
        show("Группировка по формату", queries.format_statistics())
        self.stdout.write(f"\nMIN/MAX дат: {queries.date_range()}")
        show("exclude + подзапрос по дате",
             queries.users_without_requests_for_date(date(2026, 9, 18)))
        show("values_list + distinct", queries.distinct_formats())
        show("F + annotate + values", queries.request_rows(queries.get_requests()))
        page = Paginator(queries.get_requests(), 2).get_page(2)
        self.stdout.write(f"\nПагинация: страница {page.number}/{page.paginator.num_pages}; "
                          f"ID={[item.pk for item in page]}")
        try:
            StudyRequest.objects.get(pk=2147483647)
        except StudyRequest.DoesNotExist:
            self.stdout.write("get(): отсутствующий ID -> DoesNotExist")
        with transaction.atomic():
            user = User.objects.create(name="Демонстрационный участник")
            subject = Subject.objects.create(name="Демонстрационный предмет")
            item = StudyRequest(user=user, subject=subject, format="онлайн",
                                study_date=date(2026, 11, 16))
            item.full_clean()
            item.save()
            self.stdout.write(f"\nCREATE: запрос {item.pk}, автор {item.user.name}")
            item.format = "офлайн"
            item.save(update_fields=["format"])
            item.refresh_from_db()
            self.stdout.write(f"UPDATE: {item.format}")
            item.close()
            self.stdout.write(f"CLOSE: {StudyRequest.objects.get(pk=item.pk).is_closed}")
            try:
                subject.delete()
            except ProtectedError:
                self.stdout.write("PROTECT: удаление связанного предмета запрещено")
            key = item.pk
            item.delete()
            self.stdout.write(f"DELETE: exists={StudyRequest.objects.filter(pk=key).exists()}")
            transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS("Все тестовые изменения отменены (ROLLBACK)."))
