"""Настройка Django для pytest без подключения тестовой базы данных."""
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
