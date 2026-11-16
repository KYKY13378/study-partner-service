# Сервис поиска партнеров для учебы

Индивидуальная тема: поиск партнеров по предмету, дате и формату занятий.
Текущее состояние — **ПР9: Django ORM, модели, связи и операции с данными**.
Продолжен прежний проект ПР1–ПР7; исходные JSON, SQL и база ПР7 сохранены.
Яндекс Практикум отложен по поручению пользователя.

Автор: Ким Артём Юрьевич, группа ЭФБО-18-24, РТУ МИРЭА.
Дисциплина: «Технологии разработки приложений на базе фреймворков».

## Быстрый запуск (PowerShell из корня проекта)

Для новой установки:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py import_pr7
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8009
```

При следующих запусках достаточно последней команды. В учебной папке есть
`Запустить_ПР9.cmd`: он применяет миграции, импортирует ПР7 только при пустых таблицах
и запускает порт 8009 с локальной Django Debug Toolbar.
После переноса проекта venv нужно пересоздать. Зависимости: Django 5.2,
pytest, pytest-django, flake8, django-debug-toolbar; конкретные диапазоны в requirements.txt.

## Модели и связи

| Приложение / модель | Поля | Назначение |
|---|---|---|
| users.User | id BigAutoField PK; name CharField(100); group_name CharField(32, blank=True, null=True, default=None) | Участник сервиса, без авторизации |
| subjects.Subject | id BigAutoField PK; name CharField(120) | Учебный предмет |
| requests.StudyRequest | id BigAutoField PK; user FK; subject FK; format CharField(6, choices); study_date DateField; is_closed BooleanField(default=False) | Учебный запрос |

Первичные ключи добавляются Django по DEFAULT_AUTO_FIELD. Поля name обязательны;
CHECK запрещает пустую строку, clean() также отклоняет имя из пробелов.
У StudyRequest два ForeignKey с `on_delete=PROTECT` и `related_name="study_requests"`.
Поэтому `item.user`, `item.subject` дают связанные модели, `item.user_id` и
`item.subject_id` — числовые ключи. Обратные связи: `user.study_requests.all()`
и `subject.study_requests.all()`. PROTECT на уровне ORM запрещает удалять родителя,
пока на него ссылаются запросы. На уровне SQLite есть внешние ключи.
Формат ограничен онлайн/офлайн, статус — 0/1; CHECK-ограничения включены в миграции.
Индексы: дата, (subject,is_closed), (user,study_date,is_closed).

`users.User` — участник предметной области, это отдельная модель от
`django.contrib.auth.models.User`, используемой административной авторизацией.
Веб-авторизация участников, переписка, отклики и создание пары не реализованы.
CRUD доступен через Django Shell, зарегистрированные модели admin и демонстрационную
команду; пользовательские формы создания/редактирования — следующий этап.

Модели имеют __str__. StudyRequest.close() сохраняет статус через
save(update_fields=["is_closed"]). Свойства User.group, StudyRequest.study_day и
StudyRequest.date поддерживают прежние карточки ПР6. В ORM дата — объект date,
в отображении используется прежний фильтр шаблона date.
save()/objects.create() сами по себе не вызывают full_clean(): для проверки введенных
полей вызывайте full_clean() явно; ModelForm в admin делает это при валидации.

## Миграции и стратегия перехода

Выбрана новая база **data/study_partner_orm.sqlite3**, управляемая Django.
Файл не включен в Git, база воспроизводится миграциями и импортом.
Путь можно переопределить переменной DJANGO_DATABASE_PATH (например для проверки
запуска с чистой БД). Прежняя data/study_partner.sqlite открывается импортером
только с mode=ro и остается источником ПР7. Служебный старый db.sqlite3 тоже сохранен;
ПР9 его не использует. Не применяйте ORM-миграции к исходной базе ПР7.

Созданы initial-миграции users, subjects, requests. Миграция запросов зависит от
обоих родителей. Для проверки структуры:

```powershell
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py showmigrations
.\venv\Scripts\python.exe manage.py sqlmigrate requests 0001
```

`db/inspect_source_db.py` проверяет целостность, таблицы, столбцы, PK/FK и counts.
`db/transfer_to_orm.py` и команда `import_pr7` читают пользователей, предметы, затем
запросы. Даты ISO преобразуются в date, 0/1 — в bool, ID и внешние ключи сохраняются.
Все вставки через ORM, с full_clean(), в одной transaction.atomic().
При ошибке ранее вставленные в этой транзакции родители/дети откатываются.
Повторный импорт одинаковых записей ничего не добавляет. Если существующий ID имеет
другие поля, команда завершается ошибкой без перезаписи. Флаг --only-if-empty
используется запускателем: если хотя бы одна таблица уже заполнена, импорт пропускается.
Это защищает последующие ORM-изменения от повторного импорта при каждом запуске.
Сравнение с источником: 4 участника, 3 предмета, 5 запросов; все ID и связи совпадают.

```powershell
.\venv\Scripts\python.exe -m db.inspect_source_db
.\venv\Scripts\python.exe manage.py import_pr7 --only-if-empty
```

## Страницы и параметры

| Адрес | Результат |
|---|---|
| `/` | предметы, агрегаты и три последних запроса |
| `/subjects/` | предметы с числом активных запросов; `?q=математика` — поиск по названию |
| `/subjects/1/` | предмет и связанные активные запросы |
| `/requests/` | каталог, по умолчанию все статусы |
| `/requests/3/` | запрос с автором/предметом одним запросом SELECT JOIN |
| `/requests/search/` | тот же поиск, по умолчанию только активные |
| `/requests/statistics/` | COUNT, условные подсчеты, GROUP BY, HAVING, MIN/MAX |

Имена URL и namespaces ПР6–ПР7 сохранены. Детальные страницы используют
get_object_or_404; Http404 обрабатывается локально, чтобы сохранить оформленную
страницу с сообщением при DEBUG=True. Неизвестный маршрут при DEBUG=False
попадает в общий handler404.

Параметры каталога и поиска:

| GET | Допустимые значения / поведение |
|---|---|
| q | до 100 символов, буквальный поиск по предмету, имени и группе |
| date | календарная дата строго YYYY-MM-DD |
| subject, user | положительный целый ID; несуществующий ID дает пустую выборку |
| format | пусто, онлайн, офлайн |
| status | all, active, closed |
| sort | date, date_desc, subject, author; неизвестное значение →date |
| per_page | 2, 5, 10, 20; по умолчанию 2 |
| view | cards, table; по умолчанию cards |
| page | номер страницы; нечисловой → первая, выход за диапазон (в т.ч. 0/-1) → последняя |

Вход проверяется Django Form. Ошибочные фильтры дают HTTP400 с пояснением,
пустой корректный результат — HTTP200. order_by выбирается из фиксированного
словаря SORT_FIELDS, произвольное имя поля от пользователя не передается.
Фильтрация → сортировка → Paginator → context → template.
У сортировок есть стабильный дополнительный ключ pk. Новый поиск сбрасывает page,
ссылки {% querystring page=number %} сохраняют остальные параметры.
Карточки и таблица переключаются без потери условий, переход вида начинает страницу 1.
Быстрый JavaScript-фильтр ПР6 сохранен и явно действует на текущую страницу;
глобальный поиск через GET работает без JavaScript.

Для кириллицы применяется стандартный ORM lookup iregex с re.escape ввода:
пользователь задает буквальный текст, а не регулярное выражение. Это сохраняет
регистронезависимый поиск в SQLite, где обычный LIKE/icontains ограничен для
не-ASCII символов. SQL по-прежнему генерирует ORM, значения связывает Django.

## Рабочие ORM-выражения

Реализация — requests/queries.py, views.py приложений и Paginator в requests/views.py.
Каталог ниже содержит больше 15 различных выражений. Один составной QuerySet
считается одним выражением; повтор одной статистики на двух страницах не увеличивает число.

| № | Выражение / функция | Использование |
|---|---|---|
| 1 | Subject.objects.all() | главная, выбор предмета |
| 2 | get_object_or_404(Subject, pk=...) | детальная страница предмета |
| 3 | get_object_or_404(StudyRequest.objects.select_related(...), pk=...) | карточка запроса |
| 4 | StudyRequest.objects.select_related("user","subject") | общий каталог |
| 5 | ...filter(is_closed=False) | активные запросы |
| 6 | ...filter(is_closed=True) | закрытые запросы |
| 7 | filter_requests: filter(**conditions) | дата+предмет+автор+формат |
| 8 | filter_requests: Q(subject__name__iregex=...) \| Q(user__name__iregex=...) \| Q(user__group_name__iregex=...) | поиск по связанным полям |
| 9 | get_subject_cards: filter(name__iregex=...) | поиск по одному строковому полю |
| 10 | order_by("-study_date","-pk") | сортировка по убыванию даты |
| 11 | order_by("subject__name","study_date","pk") | сортировка по связанному полю и дате |
| 12 | subject.study_requests.filter(is_closed=False).select_related(...) | обратная связь на странице предмета |
| 13 | ...order_by("-pk")[:3] | недавние запросы главной |
| 14 | aggregate(total=Count(...),active=Count(...filter=Q(...)),closed=...) | сводные показатели |
| 15 | User.objects.count() | число участников |
| 16 | Subject.objects.count() | число предметов |
| 17 | Subject.objects.annotate(active_count=Count(...filter=Q(...))) | предметы, включая объекты без запросов |
| 18 | User.objects.annotate(total=...,active=...,closed=...) | статистика участников |
| 19 | ...filter(active_count__gte=minimum).order_by("-active_count","pk") | популярные предметы, HAVING |
| 20 | values("format").annotate(total=Count(...),active=...) | группировка по формату |
| 21 | aggregate(first_date=Min(...),last_date=Max(...)) | диапазон дат |
| 22 | User.objects.exclude(pk__in=StudyRequest.objects.filter(...).values_list("user_id",flat=True)) | участники без активного запроса на дату |
| 23 | values_list("format",flat=True).distinct() | варианты формата в форме |
| 24 | annotate(user_name=F("user__name"),subject_name=F("subject__name"),user_group=F(...)).values(...) | табличный вид каталога |
| 25 | User.objects.values("id","name","group_name").order_by("name","pk") | список авторов формы |
| 26 | Paginator(queryset, page_size).get_page(page) | LIMIT/OFFSET и счетчик страниц |

Минимумы соблюдены: базовое получение ≥ 2, фильтрация ≥ 4, поиск ≥ 2, сортировка ≥ 2,
связи ≥ 2, агрегирование/аннотирование ≥ 2, пагинация 1. Выражения реализуют функции сайта,
а не добавлены только для демонстрации в Shell. Создание/обновление/удаление дополнительно
показаны в admin и команде orm_demo.
`exclude` использует подзапрос: закрытый запрос на выбранную дату не исключает участника,
даже если у него есть активный запрос на другую дату. «Без запроса» не означает,
что участник подтвердил свободное время; пояснение отображается на сайте.

## CRUD и демонстрация

```powershell
.\venv\Scripts\python.exe manage.py orm_demo
.\venv\Scripts\python.exe manage.py shell
```

orm_demo печатает рабочие выражения, SQL, результаты, Paginator и CRUD. Специально
созданные тестовые данные всегда отменяются transaction.set_rollback(True).
Исходные пользовательские записи не редактируются этой демонстрацией.
Для ручной работы в Shell:

```python
from requests.models import StudyRequest
from subjects.models import Subject
from users.models import User
item = StudyRequest.objects.select_related("user", "subject").get(pk=3)
item.user, item.subject, item.user_id, item.subject_id
list(item.subject.study_requests.values_list("pk", flat=True))
```

Для создания: model(...), full_clean(), save() либо objects.create(...), учитывая,
что create не вызывает full_clean. Для обновления: присвоить поле и save(update_fields=[...]).
Для удаления: delete() специально созданной тестовой записи. Удаление связанного
родителя вызывает ProtectedError. Команда orm_demo выполняет весь цикл воспроизводимо.

## Django Debug Toolbar

Для отдельного ручного запуска:

```powershell
$env:DJANGO_DEBUG_TOOLBAR='1'
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8009
```

Панель работает только при DEBUG=True и с локального IP. Нажать DJDT справа → SQL.
На /requests/3/ — один SELECT с JOIN users_user и subjects_subject.
В табличном каталоге SQL показывает только поля values(), включая F-алиасы.
Для обычного запуска выключить переменную или задать 0. При DJANGO_DEBUG=0 панель
не подключается даже с DJANGO_DEBUG_TOOLBAR=1. Настройки production отдельно не настраивались.

Документация: [Django 5.2 QuerySet](https://docs.djangoproject.com/en/5.2/ref/models/querysets/),
[Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/installation.html).

## Проверки

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py showmigrations
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe -m pytest -v
.\venv\Scripts\python.exe -m flake8 . --extend-exclude=venv
```

140 тестов: прежние классы/JSON/SQL, перенос и откат, модели/связи/PROTECT, CRUD,
контроль числа запросов, кириллица, whitelist сортировки, пагинация/GET, 200/400/404.
pytest-django использует отдельную тестовую БД, SQL-тесты ПР7 — отдельный временный файл.
Рабочие базы и JSON не изменяются тестами. Чистая установка отдельно проверяется
миграциями и импортом в новую БД. Журналы и скриншоты — в учебной папке отчет/ПР9.

## Структура проекта

| Каталог / файл | Назначение |
|---|---|
| study_partner/ | настройки Django, маршруты и обработчики ошибок |
| homepage/ | главная страница, общий CSS, JavaScript и шаблоны |
| users/ | модель и административный интерфейс участников |
| subjects/ | модель, список и детальная страница предмета |
| requests/ | модель запросов, ORM-выборки, формы фильтров, страницы, команды |
| users/migrations/, subjects/migrations/, requests/migrations/ | структура новой базы |
| db/ | прежний SQL-слой, инспектор и перенос ПР7 в ORM |
| data/ | исходные JSON/SQLite ПР7; локальная ORM-база исключена из Git |
| sql/ | схема и запросы предыдущего SQL-этапа |
| tests/ | тесты консольного приложения, SQL, ORM и веб-страниц |
| main.py, src/ | прежняя консольная версия, классы сущностей и хранение JSON |

## Сохраненные версии

| Этап | Коммит / состояние | Запуск в учебной папке |
|---|---|---|
| ПР5 | 98621f5, версии/PR5 | Запустить_ПР5.cmd, порт 8005 |
| ПР6 | 50c4e42, версии/PR6 | Запустить_ПР6.cmd, порт 8006 |
| ПР7 | df6af10, версии/PR7 | Запустить_ПР7.cmd, порт 8007 |
| ПР9 | текущий основной проект, коммит PR9: | Запустить_ПР9.cmd, порт 8009 |

Исходные SQL-модули db/database.py, db/repository.py, sql/ сохранены для истории ПР7.
Веб-представления ПР9 их не вызывают; прямой sqlite3 используется только в инспекторе
и чтении исходной базы для переноса. Консольный main.py по-прежнему использует JSON;
его изменения автоматически не синхронизируются с ORM-базой.
Для тестов старых сохраненных версий общим venv отключить новый плагин:
`python -m pytest -p no:django -v` из нужной папки версии. Это не требуется для запуска серверов.
