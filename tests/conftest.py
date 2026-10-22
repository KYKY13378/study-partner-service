"""Настройка Django для pytest с отдельной временной SQLite для каждого теста."""
import os

import django
import pytest
from django.test import Client, override_settings
from django.test.utils import setup_test_environment, teardown_test_environment


def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "study_partner.settings")
    django.setup()
    setup_test_environment()


def pytest_unconfigure():
    teardown_test_environment()


@pytest.fixture
def client():
    with override_settings(ALLOWED_HOSTS=["testserver"]):
        yield Client()


@pytest.fixture(autouse=True)
def isolated_sqlite(tmp_path, monkeypatch):
    from db import database
    from db.import_json import import_json

    path = tmp_path / "test.sqlite"
    monkeypatch.setattr(database, "DATABASE_FILE", path)
    import_json(path)
    yield path
