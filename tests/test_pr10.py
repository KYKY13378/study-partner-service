"""ПР10: миграционная семантика, статусы, Admin, права, inline и вычисления БД."""
from datetime import date
from io import StringIO

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse
import pytest

from requests.models import StudyRequest
from requests.queries import (
    get_requests, request_rows, request_totals, users_without_requests_for_date,
)
from subjects.models import Subject
from users.models import User


@pytest.fixture
def admin_client(client):
    account = get_user_model().objects.create_superuser("test_admin", password="test-only-password")
    client.force_login(account)
    return client


def test_original_completed_status_is_preserved():
    assert StudyRequest.objects.completed().get().pk == 5
    assert set(StudyRequest.objects.active().values_list("pk", flat=True)) == {1, 2, 3, 4}
    assert not StudyRequest.objects.cancelled().exists()


@pytest.mark.parametrize("status", StudyRequest.Status.values)
def test_status_controls_availability_and_counts(client, status):
    item = StudyRequest.objects.get(pk=3)
    item.status = status
    item.save(update_fields=["status"])
    ids = users_without_requests_for_date(item.study_date).values_list("pk", flat=True)
    assert (3 in ids) is (status != StudyRequest.Status.ACTIVE)
    response = client.get("/requests/", {"status": status, "date": item.study_date.isoformat()})
    assert [row.pk for row in response.context["study_requests"]] == [3]
    assert item.get_status_display() in response.content.decode()
    totals = request_totals()
    assert totals[status] == (4 if status == StudyRequest.Status.ACTIVE else
                              2 if status == StudyRequest.Status.COMPLETED else 1)
    assert totals["total"] == totals["active"] + totals["cancelled"] + totals["completed"]


def test_queryset_methods_chain_and_stay_lazy(django_assert_num_queries):
    with django_assert_num_queries(0):
        items = StudyRequest.objects.active().for_date(date(2026, 9, 18)).filter(subject_id=1)
    with django_assert_num_queries(1):
        assert list(items.values_list("pk", flat=True)) == [3]


def test_invalid_status_rejected_by_database():
    with pytest.raises(IntegrityError), transaction.atomic():
        StudyRequest.objects.filter(pk=1).update(status="unknown")


def test_queryset_cancelled_and_completed_do_not_block_other_dates():
    StudyRequest.objects.filter(pk=3).update(status=StudyRequest.Status.CANCELLED)
    assert 3 in users_without_requests_for_date(date(2026, 9, 18)).values_list("pk", flat=True)
    assert 2 in users_without_requests_for_date(date(2026, 10, 1)).values_list("pk", flat=True)


def test_values_status_label_slug_and_relations_are_one_query(django_assert_num_queries):
    with django_assert_num_queries(1):
        rows = list(request_rows(get_requests("completed")))
    assert rows[0]["status_label"] == "Завершён" and rows[0]["is_closed"]
    assert rows[0]["subject_slug"].isascii()


def test_subject_slug_is_unique_ascii_stable_and_public(client):
    first = Subject.objects.create(name="Математика")
    second = Subject.objects.create(name="Математика")
    assert first.slug != second.slug and first.slug.isascii()
    assert first.slug.startswith("matematika-")
    original = first.slug
    first.name = "Алгебра"
    first.save()
    first.refresh_from_db()
    assert first.slug == original
    assert reverse("subjects:detail_slug", kwargs={"slug": first.slug}) == first.get_absolute_url()
    assert client.get(first.get_absolute_url()).status_code == 200
    assert client.get(f"/subjects/{first.pk}/").status_code == 200
    assert client.get("/subjects/missing-slug/").status_code == 404


def test_explicit_duplicate_slug_rejected():
    subject = Subject.objects.first()
    with pytest.raises(IntegrityError), transaction.atomic():
        Subject.objects.create(name="Другой предмет", slug=subject.slug)


def test_generated_display_name_recomputed_by_database():
    user = User.objects.get(pk=1)
    assert user.display_name == "Алексей · ЭФБО-18-24"
    User.objects.filter(pk=user.pk).update(name="Алексей Новый", group_name="Новая группа")
    user.refresh_from_db()
    assert user.display_name == "Алексей Новый · Новая группа"
    user.group_name = None
    user.save(update_fields=["group_name"])
    user.refresh_from_db()
    assert user.display_name == "Алексей Новый"


def test_shared_context_updates_and_is_used_on_different_pages(client):
    Subject.objects.create(name="Дополнительный")
    for url in ("/", "/requests/3/", "/subjects/"):
        response = client.get(url)
        assert response.context["site_name"] == "Учимся вместе"
        assert response.context["site_subject_count"] == 4
        assert "Предметов в каталоге: 4" in response.content.decode()


@pytest.mark.parametrize("url", ["/admin/", "/admin/requests/studyrequest/"])
def test_anonymous_cannot_access_admin(client, url):
    assert client.get(url).status_code == 302


def test_non_staff_cannot_access_admin(client):
    account = get_user_model().objects.create_user("member", password="test-only-password")
    client.force_login(account)
    assert client.get("/admin/").status_code == 302


@pytest.mark.parametrize("url", [
    "/admin/", "/admin/users/user/", "/admin/subjects/subject/",
    "/admin/requests/studyrequest/", "/admin/subjects/subject/1/change/",
    "/admin/users/user/2/change/", "/admin/requests/studyrequest/3/change/",
])
def test_admin_models_lists_and_inlines_open(admin_client, url):
    assert admin_client.get(url).status_code == 200


def test_admin_cyrillic_search_combines_words_filters_and_ordering(admin_client):
    response = admin_client.get("/admin/requests/studyrequest/", {
        "q": "МАТЕМАТИКА дмитрий", "status__exact": "active", "o": "-4",
    })
    assert [item.pk for item in response.context["cl"].queryset] == [3]
    response = admin_client.get("/admin/requests/studyrequest/", {"q": ".*"})
    assert not response.context["cl"].queryset.exists()


def test_admin_related_data_avoids_n_plus_one(admin_client, django_assert_num_queries):
    request = admin_client.get("/admin/").wsgi_request
    items = admin.site._registry[StudyRequest].get_queryset(request)
    items = items.select_related("user", "subject")
    with django_assert_num_queries(1):
        assert all(str(item.user) and str(item.subject) for item in items)


def test_admin_inline_can_update_related_status(admin_client):
    subject = Subject.objects.get(pk=1)
    items = list(subject.study_requests.order_by("study_date", "pk"))
    data = {"name": subject.name, "study_requests-TOTAL_FORMS": len(items),
            "study_requests-INITIAL_FORMS": len(items), "study_requests-MIN_NUM_FORMS": 0,
            "study_requests-MAX_NUM_FORMS": 1000, "_continue": "1"}
    for index, item in enumerate(items):
        prefix = f"study_requests-{index}-"
        data.update({prefix+"id": item.pk, prefix+"subject": subject.pk,
                     prefix+"user": item.user_id, prefix+"format": item.format,
                     prefix+"study_date": item.study_date.isoformat(),
                     prefix+"status": (StudyRequest.Status.CANCELLED
                                       if item.pk == 3 else item.status)})
    response = admin_client.post("/admin/subjects/subject/1/change/", data)
    assert response.status_code == 302, response.context
    assert StudyRequest.objects.get(pk=3).status == StudyRequest.Status.CANCELLED
    assert 3 in users_without_requests_for_date(date(2026, 9, 18)).values_list("pk", flat=True)


@pytest.mark.parametrize("action,status", [
    ("cancel_search", StudyRequest.Status.CANCELLED),
    ("complete_search", StudyRequest.Status.COMPLETED),
    ("reopen_search", StudyRequest.Status.ACTIVE),
])
def test_admin_actions_update_selected_only(admin_client, action, status):
    original = StudyRequest.objects.get(pk=2).status
    response = admin_client.post("/admin/requests/studyrequest/", {
        "action": action, "_selected_action": ["3"], "index": 0,
    })
    assert response.status_code == 302
    assert StudyRequest.objects.get(pk=3).status == status
    assert StudyRequest.objects.get(pk=2).status == original


def test_admin_rejects_bad_date_without_writing(admin_client):
    response = admin_client.post("/admin/requests/studyrequest/add/", {
        "user": 1, "subject": 1, "format": "онлайн", "study_date": "31.02.2026",
        "status": "active", "_save": "1",
    })
    assert response.status_code == 200
    assert response.context["adminform"].form.errors["study_date"]
    assert StudyRequest.objects.count() == 5


def test_roles_idempotent_and_observer_cannot_change_or_delete(client):
    for _ in range(2):
        call_command("setup_admin_roles", stdout=StringIO())
    group = Group.objects.get(name="Наблюдатели сервиса")
    assert group.permissions.count() == 3
    account = get_user_model().objects.create_user("observer", is_staff=True)
    account.groups.add(group)
    client.force_login(account)
    assert client.get("/admin/requests/studyrequest/").status_code == 200
    assert client.get("/admin/requests/studyrequest/3/change/").status_code == 200
    assert client.post("/admin/requests/studyrequest/3/change/", {}).status_code == 403
    assert client.get("/admin/requests/studyrequest/add/").status_code == 403
    assert client.get("/admin/requests/studyrequest/3/delete/").status_code == 403
    assert client.get("/admin/auth/user/").status_code == 403
    assert not Permission.objects.filter(group=group).exclude(codename__startswith="view_").exists()


def test_coordinator_has_domain_crud_without_delete_or_auth_permissions(client):
    call_command("setup_admin_roles", stdout=StringIO())
    group = Group.objects.get(name="Координаторы сервиса")
    assert group.permissions.count() == 9
    account = get_user_model().objects.create_user("coordinator", is_staff=True)
    account.groups.add(group)
    client.force_login(account)
    assert client.get("/admin/requests/studyrequest/add/").status_code == 200
    assert client.get("/admin/requests/studyrequest/3/delete/").status_code == 403
    assert client.get("/admin/auth/group/").status_code == 403


def test_admin_post_requires_csrf():
    protected_client = Client(enforce_csrf_checks=True)
    response = protected_client.post("/admin/login/", {"username": "no", "password": "no"})
    assert response.status_code == 403


@pytest.mark.parametrize("page_size", [2, 20])
def test_catalog_query_count_does_not_grow_with_page_size(
        client, django_assert_num_queries, page_size):
    with django_assert_num_queries(6):
        assert client.get("/requests/", {"view": "table", "per_page": page_size}).status_code == 200
