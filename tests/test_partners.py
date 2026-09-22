# tests/test_partners.py
from src.partners import (
    add_partner,
    filter_partners_by_format,
    find_partners_by_subject,
    get_partner_status,
)


def test_add_partner():
    partners = []
    add_partner(partners, "Иван", "Физика", "онлайн", "01.10.2026")
    assert len(partners) == 1
    assert partners[0]["name"] == "Иван"


def test_find_partners_by_subject():
    partners = []
    add_partner(partners, "Иван", "Физика", "онлайн", "01.10.2026")
    add_partner(partners, "Мария", "Математика", "офлайн", "02.10.2026")
    found = find_partners_by_subject(partners, "математика")
    assert len(found) == 1
    assert found[0]["name"] == "Мария"


def test_filter_partners_by_format():
    partners = []
    add_partner(partners, "Иван", "Физика", "онлайн", "01.10.2026")
    add_partner(partners, "Мария", "Математика", "офлайн", "02.10.2026")
    filtered = filter_partners_by_format(partners, "онлайн")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "Иван"


def test_get_partner_status_found():
    status = get_partner_status(True)
    assert "найден" in status.lower()


def test_get_partner_status_not_found():
    status = get_partner_status(False)
    assert "не найден" in status.lower()