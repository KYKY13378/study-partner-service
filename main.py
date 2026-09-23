# main.py
from src import StudyRequest, Subject, User
from src.requests import (
    add_request,
    close_request,
    filter_requests_by_format,
    find_requests_by_subject,
    get_partner_status,
)
from src.storage import (
    load_requests,
    load_subjects,
    load_users,
    save_requests,
    save_subjects,
    save_users,
)
from src.subjects import find_subject_by_id
from src.users import find_user_by_id
from src.utils import input_date, input_int


def show_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Сервис поиска партнеров для учебы ===")
    print("1. Показать все запросы")
    print("2. Найти запросы по предмету")
    print("3. Отфильтровать запросы по формату")
    print("4. Добавить новый запрос")
    print("5. Закрыть запрос")
    print("6. Показать статус поиска")
    print("0. Выход")


def show_requests(requests: list[StudyRequest]) -> None:
    """Вывести список всех запросов."""
    if not requests:
        print("Список запросов пуст.")
        return

    print("\n--- Все запросы ---")
    for request in requests:
        print(request)


def show_users(users: list[User]) -> None:
    """Вывести список пользователей."""
    print("\n--- Пользователи ---")
    for user in users:
        print(f"{user.id}. {user}")


def show_subjects(subjects: list[Subject]) -> None:
    """Вывести список предметов."""
    print("\n--- Предметы ---")
    for subject in subjects:
        print(f"{subject.id}. {subject}")


def find_by_subject_menu(requests: list[StudyRequest]) -> None:
    """Меню поиска запросов по предмету."""
    subject_name = input("Введите предмет для поиска: ")
    found = find_requests_by_subject(requests, subject_name)

    if found:
        print(f"\nНайдено запросов: {len(found)}")
        for request in found:
            print(request)
    else:
        print(f"\nЗапросы по предмету '{subject_name}' не найдены.")


def filter_by_format_menu(requests: list[StudyRequest]) -> None:
    """Меню фильтрации запросов по формату."""
    format_type = input("Введите формат (онлайн/офлайн): ")
    filtered = filter_requests_by_format(requests, format_type)

    if filtered:
        print(f"\nЗапросов с форматом '{format_type}': {len(filtered)}")
        for request in filtered:
            print(request)
    else:
        print(f"\nЗапросы с форматом '{format_type}' не найдены.")


def create_new_request(
        requests: list[StudyRequest],
        users: list[User],
        subjects: list[Subject],
) -> None:
    """Создать новый запрос по вводу пользователя.

    Args:
        requests: Коллекция запросов.
        users: Коллекция пользователей.
        subjects: Коллекция предметов.
    """
    print("\n--- Добавление нового запроса ---")
    show_users(users)
    user_id = input_int("Введите ID пользователя-автора: ")
    user = find_user_by_id(users, user_id)
    if user is None:
        print("Ошибка: пользователь с таким ID не найден.")
        return

    show_subjects(subjects)
    subject_id = input_int("Введите ID предмета: ")
    subject = find_subject_by_id(subjects, subject_id)
    if subject is None:
        print("Ошибка: предмет с таким ID не найден.")
        return

    format_type = input("Введите формат (онлайн/офлайн): ")
    study_date = input_date("Введите дату (ДД.ММ.ГГГГ): ")

    request = add_request(
        requests,
        user,
        subject,
        format_type,
        study_date.strftime("%d.%m.%Y"),
    )
    print("Запрос создан:")
    print(request)


def close_request_menu(requests: list[StudyRequest]) -> None:
    """Меню закрытия запроса."""
    show_requests(requests)
    request_id = input_int("Введите ID запроса для закрытия: ")
    if close_request(requests, request_id):
        print("Запрос закрыт.")
    else:
        print("Ошибка: запрос с таким ID не найден.")


def show_status_menu() -> None:
    """Меню показа статуса поиска."""
    answer = input("Партнер найден? (да/нет): ").lower()
    print(get_partner_status(answer == "да"))


def main() -> None:
    """Точка запуска приложения."""
    users = load_users()
    subjects = load_subjects()
    requests = load_requests(users, subjects)

    while True:
        show_menu()
        choice = input_int("\nВыберите действие: ")

        if choice == 1:
            show_requests(requests)
        elif choice == 2:
            find_by_subject_menu(requests)
        elif choice == 3:
            filter_by_format_menu(requests)
        elif choice == 4:
            create_new_request(requests, users, subjects)
        elif choice == 5:
            close_request_menu(requests)
        elif choice == 6:
            show_status_menu()
        elif choice == 0:
            save_users(users)
            save_subjects(subjects)
            save_requests(requests)
            print("Данные сохранены. До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
