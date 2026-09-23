# tests/test_subjects.py
from src.subjects import (
    Subject,
    add_subject,
    find_subject_by_id,
    find_subject_by_name,
)


def test_subject_creation():
    subject = Subject(1, "Математика")
    assert subject.id == 1
    assert subject.name == "Математика"


def test_subject_str():
    subject = Subject(1, "Математика")
    assert str(subject) == "Математика"


def test_subject_from_data():
    subject = Subject.from_data({"id": 2, "name": "Физика"})
    assert subject.id == 2
    assert subject.name == "Физика"


def test_add_subject():
    subjects = []
    subject = add_subject(subjects, "Математика")
    assert len(subjects) == 1
    assert subjects[0] is subject


def test_find_subject_by_name():
    subjects = []
    add_subject(subjects, "Математика")
    found = find_subject_by_name(subjects, "математика")
    assert found is not None
    assert found.id == 1
    assert find_subject_by_name(subjects, "Физика") is None


def test_find_subject_by_id():
    subjects = []
    add_subject(subjects, "Математика")
    assert find_subject_by_id(subjects, 1) is subjects[0]
