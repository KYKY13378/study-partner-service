-- ПР7. При повторном выполнении существующие данные сохраняются.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    group_name TEXT
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS study_requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    format TEXT NOT NULL CHECK (format IN ('онлайн', 'офлайн')),
    study_date TEXT NOT NULL CHECK (
        length(study_date) = 10
        AND date(study_date, '+0 days') IS NOT NULL
        AND date(study_date, '+0 days') = study_date
    ),
    is_closed INTEGER NOT NULL DEFAULT 0 CHECK (is_closed IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_requests_subject_status
    ON study_requests(subject_id, is_closed);
CREATE INDEX IF NOT EXISTS idx_requests_user_date
    ON study_requests(user_id, study_date, is_closed);
CREATE INDEX IF NOT EXISTS idx_requests_date ON study_requests(study_date);
