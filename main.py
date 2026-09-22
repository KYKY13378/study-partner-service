# main.py
from src.partners import (
    add_partner,
    filter_partners_by_format,
    find_partners_by_subject,
    get_partner_status,
)
from src.storage import load_data, save_data
from src.utils import input_date, input_int

DATA_FILE = "data/partners.json"


def show_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Сервис поиска партнеров для учебы ===")
    print("1. Показать всех партнеров")
    print("2. Найти партнера по предмету")
    print("3. Отфильтровать по формату (онлайн/офлайн)")
    print("4. Добавить нового партнера")
    print("5. Показать статус поиска")
    print("0. Выход")


def show_all_partners(partners: list[dict]) -> None:
    """Вывести список всех партнеров."""
    if not partners:
        print("Список партнеров пуст.")
        return

    print("\n--- Все партнеры ---")
    for p in partners:
        print(f"ID: {p['id']}, Имя: {p['name']}, "
              f"Предмет: {p['subject']}, "
              f"Формат: {p['format']}, Дата: {p['date']}")


def find_partner_menu(partners: list[dict]) -> None:
    """Меню поиска партнера по предмету."""
    subject = input("Введите предмет для поиска: ")
    found = find_partners_by_subject(partners, subject)

    if found:
        print(f"\nНайдено партнеров: {len(found)}")
        for p in found:
            print(f"  - {p['name']} ({p['format']}, дата: {p['date']})")
    else:
        print(f"\nПартнеры по предмету '{subject}' не найдены.")


def filter_by_format_menu(partners: list[dict]) -> None:
    """Меню фильтрации по формату."""
    format_type = input("Введите формат (онлайн/офлайн): ")
    filtered = filter_partners_by_format(partners, format_type)

    if filtered:
        print(f"\nПартнеров с форматом '{format_type}': {len(filtered)}")
        for p in filtered:
            print(f"  - {p['name']} ({p['subject']}, дата: {p['date']})")
    else:
        print(f"\nПартнеры с форматом '{format_type}' не найдены.")


def add_partner_menu(partners: list[dict]) -> None:
    """Меню добавления нового партнера."""
    print("\n--- Добавление нового партнера ---")
    name = input("Введите имя: ")
    subject = input("Введите предмет: ")
    format_type = input("Введите формат (онлайн/офлайн): ")
    study_date = input_date("Введите дату (ДД.ММ.ГГГГ): ")

    add_partner(partners, name, subject, format_type,
                study_date.strftime("%d.%m.%Y"))
    save_data(DATA_FILE, partners)
    print("Партнер успешно добавлен и сохранен!")


def show_status_menu() -> None:
    """Меню показа статуса поиска."""
    answer = input("Партнер найден? (да/нет): ").lower()
    print(get_partner_status(answer == "да"))


def main() -> None:
    """Точка запуска приложения."""
    partners = load_data(DATA_FILE)
    if not partners:
        print("Загружены пустые данные. Начинаем с чистого списка.")

    while True:
        show_menu()
        choice = input_int("\nВыберите действие: ")

        if choice == 1:
            show_all_partners(partners)
        elif choice == 2:
            find_partner_menu(partners)
        elif choice == 3:
            filter_by_format_menu(partners)
        elif choice == 4:
            add_partner_menu(partners)
        elif choice == 5:
            show_status_menu()
        elif choice == 0:
            save_data(DATA_FILE, partners)
            print("Данные сохранены. До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
