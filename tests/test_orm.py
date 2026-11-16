"""ПР9: перенос без потерь, связи, CRUD и ORM-сценарии веб-приложения."""
from datetime import date
from html import unescape
import re
import shutil
import sqlite3
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models.deletion import ProtectedError
import pytest

from db.transfer_to_orm import transfer_to_orm
from requests.models import StudyRequest
from requests.queries import (
    get_requests, popular_subjects, request_rows, request_totals, subject_statistics,
    users_without_requests_for_date,
)
from subjects.models import Subject
from users.models import User


def test_transferred_values_ids_dates_and_relationships():
    counts = (User.objects.count(), Subject.objects.count(), StudyRequest.objects.count())
    assert counts == (4, 3, 5)
    item = StudyRequest.objects.get(pk=3)
    assert item.user_id == 3 and item.user.name == "Дмитрий"
    assert item.subject_id == 1 and item.subject.name == "Математика"
    assert item.study_date == date(2026, 9, 18) and not item.is_closed
    assert item.date == "18.09.2026" and item.study_day == item.study_date
    assert item.user.group == "ЭФБО-18-22"
    assert set(item.user.study_requests.values_list("pk", flat=True)) == {3}
    assert set(item.subject.study_requests.values_list("pk", flat=True)) == {1, 3, 5}


def test_transfer_is_idempotent_and_existing_edits_are_not_overwritten(isolated_sqlite):
    report = transfer_to_orm(isolated_sqlite)
    assert sum(report["created"].values()) == 0
    assert sum(report["existing"].values()) == 12
    item = StudyRequest.objects.get(pk=1)
    item.close()
    assert "skipped" in transfer_to_orm(isolated_sqlite, only_if_empty=True)
    with pytest.raises(ValueError, match="Конфликт"):
        transfer_to_orm(isolated_sqlite)
    assert StudyRequest.objects.get(pk=1).is_closed


def test_failed_transfer_rolls_back_parents_and_children(isolated_sqlite, tmp_path):
    source = tmp_path / "oversized.sqlite"
    shutil.copy2(isolated_sqlite, source)
    with sqlite3.connect(source) as connection:
        connection.execute("UPDATE subjects SET name=? WHERE id=3", ("Я" * 121,))
    StudyRequest.objects.all().delete()
    User.objects.all().delete()
    Subject.objects.all().delete()
    with pytest.raises(ValidationError):
        transfer_to_orm(source)
    assert User.objects.count() == Subject.objects.count() == StudyRequest.objects.count() == 0


def test_missing_transfer_source_does_not_create_file(tmp_path):
    source = tmp_path / "missing.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        transfer_to_orm(source)
    assert not source.exists()


def test_create_update_close_and_delete_via_orm():
    user = User.objects.create(name="Тестовый участник")
    subject = Subject.objects.create(name="Тестовый предмет")
    item = StudyRequest.objects.create(user=user, subject=subject, format="онлайн",
                                       study_date=date(2026, 11, 16))
    assert user.pk > 4 and subject.pk > 3 and item.pk > 5
    assert user.group_name is None and not item.is_closed
    item.format = "офлайн"
    item.save(update_fields=["format"])
    item.refresh_from_db()
    assert item.format == "офлайн"
    item.close()
    assert StudyRequest.objects.get(pk=item.pk).is_closed
    item.delete()
    assert not StudyRequest.objects.filter(user=user).exists()
    user.delete()
    subject.delete()


@pytest.mark.parametrize("model,pk", [(User, 1), (Subject, 1)])
def test_deleting_parent_is_protected(model, pk):
    with pytest.raises(ProtectedError):
        model.objects.get(pk=pk).delete()
    assert model.objects.filter(pk=pk).exists() and StudyRequest.objects.count() == 5


@pytest.mark.parametrize("fields", [
    {"format": "гибрид"}, {"study_date": "31.02.2026"},
    {"user_id": 999}, {"subject_id": 999},
])
def test_model_validation_rejects_bad_values(fields):
    values = {"user_id": 1, "subject_id": 1, "format": "онлайн",
              "study_date": date(2026, 11, 16), **fields}
    with pytest.raises(ValidationError):
        StudyRequest(**values).full_clean()


@pytest.mark.parametrize("model", [User, Subject])
def test_whitespace_names_are_rejected(model):
    with pytest.raises(ValidationError):
        model(name="   ").full_clean()


def test_database_constraint_rejects_invalid_format():
    with pytest.raises(IntegrityError), transaction.atomic():
        StudyRequest.objects.create(
            user_id=1, subject_id=1, format="гибрид", study_date=date(2026, 11, 16),
        )


def test_get_distinguishes_missing_and_multiple_records():
    with pytest.raises(StudyRequest.DoesNotExist):
        StudyRequest.objects.get(pk=999)
    with pytest.raises(StudyRequest.MultipleObjectsReturned):
        StudyRequest.objects.get(subject_id=1)


def test_select_related_eliminates_extra_queries(django_assert_num_queries):
    with django_assert_num_queries(1):
        items = list(get_requests())
        assert all(item.user.name and item.subject.name for item in items)


def test_detail_has_one_query_with_related_data(client, django_assert_num_queries):
    with django_assert_num_queries(1):
        response = client.get("/requests/3/")
        assert "Дмитрий" in response.content.decode()


def test_values_and_f_annotations_are_displayed(client):
    row = request_rows(get_requests().filter(pk=3)).get()
    assert row["user_name"] == "Дмитрий" and row["subject_name"] == "Математика"
    assert row["user_group"] == "ЭФБО-18-22"
    assert "user" not in row
    response = client.get("/requests/", {"view": "table", "per_page": 20})
    html = response.content.decode()
    assert "<table>" in html and "Дмитрий" in html and "Математика" in html
    assert all(isinstance(row, dict) for row in response.context["study_requests"])


@pytest.mark.parametrize("sort,expected", [
    ("date", [1, 3, 2, 4, 5]), ("date_desc", [5, 4, 2, 3, 1]),
    ("subject", [1, 3, 5, 2, 4]), ("author", [1, 4, 3, 2, 5]),
    ("user__password", [1, 3, 2, 4, 5]),
])
def test_allowed_sort_orders_and_safe_fallback(client, sort, expected):
    response = client.get("/requests/", {"sort": sort, "per_page": 20})
    assert response.status_code == 200
    assert [item.pk for item in response.context["study_requests"]] == expected


@pytest.mark.parametrize("q,ids", [
    ("математика", {1, 3, 5}), ("ДМИТРИЙ", {3}), ("эфбо-18-24", {1, 2, 4, 5}),
    (".*", set()), ("' OR 1=1 --", set()),
])
def test_literal_unicode_search_across_related_fields(client, q, ids):
    response = client.get("/requests/", {"q": q, "per_page": 20})
    assert response.status_code == 200
    assert {item.pk for item in response.context["study_requests"]} == ids


def test_subject_search_is_case_insensitive_for_cyrillic(client):
    response = client.get("/subjects/", {"q": "МАТЕ"})
    assert [card["subject"].pk for card in response.context["subject_cards"]] == [1]


def test_pagination_preserves_filters_sort_and_layout(client):
    parameters = {"subject": "1", "status": "all", "sort": "date_desc",
                  "per_page": "2", "q": "математика", "view": "table"}
    response = client.get("/requests/", parameters)
    assert [item["id"] for item in response.context["study_requests"]] == [5, 3]
    html = response.content.decode()
    next_url = unescape(re.search(r'href="([^"]+)" rel="next"', html).group(1))
    values = parse_qs(urlsplit(next_url).query)
    assert all(values[key] == [value] for key, value in parameters.items())
    assert values["page"] == ["2"]
    response = client.get("/requests/" + next_url)
    assert [item["id"] for item in response.context["study_requests"]] == [1]
    assert not response.context["page_obj"].has_next()


@pytest.mark.parametrize("page,expected", [("abc", 1), ("999", 3), ("0", 3), ("-1", 3)])
def test_paginator_handles_bad_or_out_of_range_page(client, page, expected):
    response = client.get("/requests/", {"page": page})
    assert response.status_code == 200 and response.context["page_obj"].number == expected


@pytest.mark.parametrize("parameters", [
    {"per_page": "0"}, {"per_page": "999"}, {"view": "unsafe"},
    {"q": "я" * 101}, {"date": "2026-9-18"},
])
def test_invalid_catalog_parameters_are_explained(client, parameters):
    response = client.get("/requests/", parameters)
    assert response.status_code == 400 and response.context["error"]


def test_groups_include_parents_without_requests_and_empty_counts():
    subject = Subject.objects.create(name="Без запросов")
    assert subject_statistics().get(pk=subject.pk).active_count == 0
    StudyRequest.objects.all().delete()
    assert request_totals() == {"total": 0, "active": 0, "closed": 0}
    assert not popular_subjects(1).exists()


def test_exclude_checks_status_and_date_on_same_request():
    # У Дмитрия есть активный запрос 18.09; закрытый 01.10 не делает его занятым 01.10.
    StudyRequest.objects.create(
        user_id=3, subject_id=1, format="онлайн", study_date=date(2026, 10, 1), is_closed=True,
    )
    assert 3 in users_without_requests_for_date(date(2026, 10, 1)).values_list("pk", flat=True)
    assert 3 not in users_without_requests_for_date(date(2026, 9, 18)).values_list("pk", flat=True)


def test_database_error_is_not_reported_as_empty_search(client):
    with patch("requests.views.get_requests", side_effect=DatabaseError("DB failure")):
        with pytest.raises(DatabaseError):
            client.get("/requests/search/")
