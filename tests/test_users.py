# tests/test_users.py
from src.users import User, add_user, find_user_by_id


def test_user_creation():
    user = User(1, "Иван", "ЭФБО-18-24")
    assert user.id == 1
    assert user.name == "Иван"
    assert user.group == "ЭФБО-18-24"


def test_user_str():
    user = User(1, "Иван", "ЭФБО-18-24")
    assert str(user) == "Иван (группа ЭФБО-18-24)"


def test_user_from_data():
    data = {"id": 2, "name": "Мария", "group": "ЭФБО-18-24"}
    user = User.from_data(data)
    assert user.id == 2
    assert user.name == "Мария"


def test_add_user():
    users = []
    user = add_user(users, "Иван", "ЭФБО-18-24")
    assert len(users) == 1
    assert users[0] is user


def test_find_user_by_id():
    users = []
    add_user(users, "Иван", "ЭФБО-18-24")
    found = find_user_by_id(users, 1)
    assert found is not None
    assert found.name == "Иван"
    assert find_user_by_id(users, 99) is None
