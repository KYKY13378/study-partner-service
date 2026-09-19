# Сервис поиска партнеров для учебы
# Начальный сценарий (ПР1)

from datetime import date

print("=" * 50)
print("  СЕРВИС ПОИСКА ПАРТНЕРОВ ДЛЯ УЧЕБЫ")
print("=" * 50)

# --- СЦЕНАРИЙ 1: Регистрация пользователя ---
print("\n[1] РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")
user_name = input("Введите ваше имя: ")
user_group = input("Введите вашу группу: ")
user_course = int(input("Введите ваш курс (числом): "))

print(f"\nПользователь зарегистрирован:")
print(f"  Имя: {user_name}")
print(f"  Группа: {user_group}")
print(f"  Курс: {user_course}")

# --- СЦЕНАРИЙ 2: Публикация запроса на поиск партнера ---
print("\n[2] ПУБЛИКАЦИЯ ЗАПРОСА НА ПОИСК ПАРТНЕРА")
subject = input("Введите предмет для изучения: ")
format_type = input("Формат занятий (онлайн/офлайн): ")
study_date_str = input("Желаемая дата занятия (ДД.ММ.ГГГГ): ")

# Преобразование строки в дату


day, month, year = study_date_str.split(".")
study_date = date(int(year), int(month), int(day)) 

print(f"\nЗапрос опубликован:")
print(f"  Предмет: {subject}")
print(f"  Формат: {format_type}")
print(f"  Дата: {study_date}")

# --- СЦЕНАРИЙ 3: Поиск партнера по предмету ---
print("\n[3] ПОИСК ПАРТНЕРА ПО ПРЕДМЕТУ")
search_subject = input("Введите предмет для поиска партнера: ")

# Простая имитация поиска (на ПР2 заменим на реальную базу данных)
available_partners = [
    {"name": "Алексей", "subject": "Математика", "format": "офлайн"},
    {"name": "Мария", "subject": "Программирование", "format": "онлайн"},
    {"name": "Дмитрий", "subject": "Физика", "format": "офлайн"},
]

found = False
for partner in available_partners:
    if partner["subject"].lower() == search_subject.lower():
        print(f"\nНайден партнер: {partner['name']}")
        print(f"  Предмет: {partner['subject']}")
        print(f"  Формат: {partner['format']}")
        found = True
        break

if not found:
    print(f"\nПартнер по предмету '{search_subject}' не найден.")

print("\n" + "=" * 50)
print("  Работа сервиса завершена")
print("=" * 50)