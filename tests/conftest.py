"""Изолированные базы ORM и прежнего SQL-слоя; рабочие файлы не изменяются."""
import pytest
from django.test import Client, override_settings


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


@pytest.fixture(autouse=True)
def seeded_orm(db, isolated_sqlite):
    from db.transfer_to_orm import transfer_to_orm

    transfer_to_orm(isolated_sqlite)
