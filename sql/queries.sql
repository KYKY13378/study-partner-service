-- ПР7. Этот файл исполняется сайтом через db.database.query.
-- ?1... — позиционные параметры sqlite3; NULL отключает необязательный фильтр.

-- name: list_subjects
-- SELECT: главная и список предметов в форме поиска
SELECT id, name FROM subjects ORDER BY id;

-- name: list_users
-- SELECT: список авторов в форме поиска
SELECT id, name, group_name FROM users ORDER BY id;

-- name: subject_by_id
-- WHERE: /subjects/<id>/
SELECT id, name FROM subjects WHERE id = ?1;

-- name: active_requests
-- WHERE + JOIN: /requests/?status=active
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
WHERE r.is_closed = 0 ORDER BY r.id;

-- name: closed_requests
-- WHERE + JOIN: /requests/?status=closed
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
WHERE r.is_closed = 1 ORDER BY r.id;

-- name: all_requests
-- JOIN: /requests/
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
ORDER BY r.id;

-- name: request_by_id
-- JOIN + WHERE: /requests/<id>/
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
WHERE r.id = ?1;

-- name: requests_for_subject
-- JOIN + WHERE: активные запросы предмета
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
WHERE r.subject_id = ?1 AND r.is_closed = 0 ORDER BY r.id;

-- name: search_requests
-- JOIN + WHERE: /requests/search/, параметры date,subject,format,user,status
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
WHERE (?1 IS NULL OR r.study_date = ?1)
  AND (?2 IS NULL OR r.subject_id = ?2)
  AND (?3 IS NULL OR r.format = ?3)
  AND (?4 IS NULL OR r.user_id = ?4)
  AND (?5 IS NULL OR r.is_closed = ?5)
ORDER BY r.study_date, r.id;

-- name: request_totals
-- Агрегаты: главная и статистика; SUM без строк заменяется нулем
SELECT COUNT(*) AS total,
       COALESCE(SUM(CASE WHEN is_closed = 0 THEN 1 ELSE 0 END), 0) AS active,
       COALESCE(SUM(CASE WHEN is_closed = 1 THEN 1 ELSE 0 END), 0) AS closed
FROM study_requests;

-- name: catalog_totals
-- Агрегаты: главная и статистика
SELECT (SELECT COUNT(*) FROM users) AS users,
       (SELECT COUNT(*) FROM subjects) AS subjects;

-- name: subjects_statistics
-- GROUP BY + LEFT JOIN: /subjects/ и статистика; учитывает пустые предметы
SELECT s.id, s.name, COUNT(r.id) AS active_count
FROM subjects AS s
LEFT JOIN study_requests AS r ON r.subject_id = s.id AND r.is_closed = 0
GROUP BY s.id, s.name
ORDER BY s.id;

-- name: users_statistics
-- GROUP BY + LEFT JOIN: статистика по участникам
SELECT u.id, u.name, u.group_name, COUNT(r.id) AS total,
       COALESCE(SUM(CASE WHEN r.is_closed = 0 THEN 1 ELSE 0 END), 0) AS active,
       COALESCE(SUM(CASE WHEN r.is_closed = 1 THEN 1 ELSE 0 END), 0) AS closed
FROM users AS u
LEFT JOIN study_requests AS r ON r.user_id = u.id
GROUP BY u.id, u.name, u.group_name
ORDER BY u.id;

-- name: popular_subjects
-- GROUP BY + HAVING: статистика, изменяемый порог min_count
SELECT s.id, s.name, COUNT(r.id) AS active_count
FROM subjects AS s
JOIN study_requests AS r ON r.subject_id = s.id
WHERE r.is_closed = 0
GROUP BY s.id, s.name
HAVING COUNT(r.id) >= ?1
ORDER BY active_count DESC, s.id;

-- name: format_statistics
-- GROUP BY: статистика по форматам занятий
SELECT format, COUNT(*) AS total,
       SUM(CASE WHEN is_closed = 0 THEN 1 ELSE 0 END) AS active
FROM study_requests
GROUP BY format ORDER BY format;

-- name: date_range
-- Агрегаты MIN/MAX: период запросов на странице статистики
SELECT MIN(study_date) AS first_date, MAX(study_date) AS last_date FROM study_requests;

-- name: users_without_requests_for_date
-- NOT EXISTS: поиск, участники без активных запросов на дату
SELECT u.id, u.name, u.group_name
FROM users AS u
WHERE NOT EXISTS (
    SELECT 1 FROM study_requests AS r
    WHERE r.user_id = u.id AND r.study_date = ?1 AND r.is_closed = 0
)
ORDER BY u.id;

-- name: recent_requests
-- JOIN: три недавних запроса на главной
SELECT r.id, r.user_id, u.name AS user_name, u.group_name,
       r.subject_id, s.name AS subject_name, r.format, r.study_date, r.is_closed
FROM study_requests AS r
JOIN users AS u ON u.id = r.user_id
JOIN subjects AS s ON s.id = r.subject_id
ORDER BY r.id DESC LIMIT ?1;

-- name: distinct_formats
-- SELECT DISTINCT: форматы из базы в форме поиска
SELECT DISTINCT format FROM study_requests ORDER BY format;
