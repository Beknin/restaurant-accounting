# test_smoke.py
import pytest
import sqlite3
import os
import sys
import tempfile
from tkinter import messagebox
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from packages.core.management import DatabaseManager
from packages.core.db_structure import TABLE_CONFIG

# ----------------------------------------------------------------------
# Фикстуры
# ----------------------------------------------------------------------

@pytest.fixture
def temp_db_path():
    """Создаёт временный файл БД и удаляет его после теста."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def db_empty(temp_db_path):
    """DatabaseManager без выполнения SQL-файла (пустая БД)."""
    db = DatabaseManager(db_path=temp_db_path)
    db.conn = sqlite3.connect(temp_db_path)
    db.conn.execute("PRAGMA foreign_keys = ON")
    return db


@pytest.fixture
def db_with_tables(temp_db_path):
    """DatabaseManager с созданными вручную таблицами (как в SQL-файле)."""
    db = DatabaseManager(db_path=temp_db_path)
    db.conn = sqlite3.connect(temp_db_path)
    db.conn.execute("PRAGMA foreign_keys = ON")

    # Создаём все таблицы из конфигурации (без выполнения внешнего файла)
    create_sql = """
    CREATE TABLE IF NOT EXISTS positions (
        position_id INTEGER PRIMARY KEY AUTOINCREMENT,
        position_name TEXT NOT NULL,
        hourly_wage REAL NOT NULL
    );
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        position_id INTEGER NOT NULL,
        FOREIGN KEY (position_id) REFERENCES positions(position_id)
    );
    CREATE TABLE IF NOT EXISTS vacation_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    CREATE TABLE IF NOT EXISTS schedule_5_2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        date TEXT NOT NULL,
        shift_type TEXT NOT NULL,
        planned_hours INTEGER NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    CREATE TABLE IF NOT EXISTS worked_hours (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        date TEXT NOT NULL,
        planned_hours INTEGER NOT NULL,
        actual_hours INTEGER NOT NULL,
        overtime_hours INTEGER NOT NULL,
        attended TEXT NOT NULL,
        month TEXT NOT NULL,
        week_num INTEGER NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    CREATE TABLE IF NOT EXISTS employee_rating (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        month TEXT NOT NULL,
        missed_days INTEGER NOT NULL,
        quality REAL NOT NULL,
        missed_penalty INTEGER NOT NULL,
        overtime_bonus INTEGER NOT NULL,
        quality_bonus REAL NOT NULL,
        final_rating REAL NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    CREATE TABLE IF NOT EXISTS final_salaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        month TEXT NOT NULL,
        actual_hours INTEGER NOT NULL,
        hourly_wage REAL NOT NULL,
        base_pay REAL NOT NULL,
        final_rating REAL NOT NULL,
        rating_multiplier REAL NOT NULL,
        bonus REAL NOT NULL,
        final_salary REAL NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    """
    db.conn.executescript(create_sql)
    db.conn.commit()
    return db


# ----------------------------------------------------------------------
# Тесты инициализации и подключения
# ----------------------------------------------------------------------

def test_connect_creates_db_file(temp_db_path):
    """При подключении должен создаться файл БД, если его нет."""
    db = DatabaseManager(db_path=temp_db_path)
    # Патчим _execute_sql_file, чтобы не требовался внешний файл
    with patch.object(db, '_execute_sql_file'):
        db.connect()
    assert os.path.exists(temp_db_path)
    db.close()


def test_connect_without_sql_file_shows_warning(temp_db_path):
    """Если sql_file не существует, должно появляться предупреждение."""
    db = DatabaseManager(db_path=temp_db_path, sql_file="nonexistent.sql")
    with patch.object(messagebox, 'showwarning') as mock_warn:
        db.connect()
        mock_warn.assert_called_once()
    db.close()


# ----------------------------------------------------------------------
# CRUD для основной таблицы (на примере positions)
# ----------------------------------------------------------------------

def test_insert_and_fetch_position(db_with_tables):
    db = db_with_tables
    data = {"position_name": "Официант", "hourly_wage": 250.0}
    new_id = db.insert("positions", data)
    assert new_id > 0

    row = db.fetch_one("SELECT * FROM positions WHERE position_id = ?", (new_id,))
    assert row is not None
    assert row[1] == "Официант"
    assert row[2] == 250.0


def test_update_position(db_with_tables):
    db = db_with_tables
    db.insert("positions", {"position_name": "Повар", "hourly_wage": 300.0})
    db.update("positions", "position_id", 1, {"hourly_wage": 350.0})

    row = db.fetch_one("SELECT hourly_wage FROM positions WHERE position_id = ?", (1,))
    assert row[0] == 350.0


def test_delete_position(db_with_tables):
    db = db_with_tables
    db.insert("positions", {"position_name": "Уборщик", "hourly_wage": 200.0})
    db.delete("positions", "position_id", 1)

    row = db.fetch_one("SELECT * FROM positions WHERE position_id = ?", (1,))
    assert row is None


def test_get_all_positions(db_with_tables):
    db = db_with_tables
    db.insert("positions", {"position_name": "A", "hourly_wage": 100})
    db.insert("positions", {"position_name": "B", "hourly_wage": 200})
    rows = db.get_all("positions", "position_id")
    assert len(rows) == 2


# ----------------------------------------------------------------------
# Работа с сотрудниками и связями
# ----------------------------------------------------------------------

def test_employee_insert_requires_position(db_with_tables):
    db = db_with_tables
    # Сначала должна существовать должность
    pos_id = db.insert("positions", {"position_name": "Менеджер", "hourly_wage": 500})
    emp_id = db.insert("employees", {"full_name": "Иванов И.И.", "position_id": pos_id})
    assert emp_id > 0

    row = db.fetch_one("SELECT full_name, position_id FROM employees WHERE employee_id = ?", (emp_id,))
    assert row[0] == "Иванов И.И."
    assert row[1] == pos_id


def test_get_employee_list(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "Кассир", "hourly_wage": 300})
    db.insert("employees", {"full_name": "Петров", "position_id": pos_id})
    db.insert("employees", {"full_name": "Сидоров", "position_id": pos_id})
    emps = db.get_employee_list()
    assert len(emps) == 2
    assert emps[0] == (1, "Петров")  # сортировка по full_name
    assert emps[1] == (2, "Сидоров")


# ----------------------------------------------------------------------
# Отпуска
# ----------------------------------------------------------------------

def test_vacation_request_lifecycle(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "Тест", "hourly_wage": 100})
    emp_id = db.insert("employees", {"full_name": "Тестовый", "position_id": pos_id})

    # Подача заявки
    req_id = db.insert("vacation_requests", {
        "employee_id": emp_id,
        "full_name": "Тестовый",
        "start_date": "2026-07-01",
        "end_date": "2026-07-10",
        "status": "pending"
    })
    assert req_id > 0

    # Получение заявок сотрудника
    requests = db.get_employee_vacations(emp_id)
    assert len(requests) == 1
    assert requests[0][5] == "pending"

    # Изменение статуса HR-ом
    db.update_vacation_status(req_id, "approved")
    req = db.fetch_one("SELECT status FROM vacation_requests WHERE request_id = ?", (req_id,))
    assert req[0] == "approved"

    # Проверка через get_employee_vacations
    requests = db.get_employee_vacations(emp_id)
    assert requests[0][5] == "approved"


# ----------------------------------------------------------------------
# Остальные таблицы (дымовая проверка вставки)
# ----------------------------------------------------------------------

def test_schedule_5_2_operations(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "X", "hourly_wage": 200})
    emp_id = db.insert("employees", {"full_name": "Работник Х", "position_id": pos_id})

    s_id = db.insert("schedule_5_2", {
        "employee_id": emp_id,
        "full_name": "Работник Х",
        "date": "2026-06-04",
        "shift_type": "day",
        "planned_hours": 8
    })
    assert s_id > 0

    row = db.fetch_one("SELECT shift_type FROM schedule_5_2 WHERE id = ?", (s_id,))
    assert row[0] == "day"


def test_worked_hours_operations(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "Y", "hourly_wage": 300})
    emp_id = db.insert("employees", {"full_name": "Работник Y", "position_id": pos_id})

    rec_id = db.insert("worked_hours", {
        "employee_id": emp_id,
        "full_name": "Работник Y",
        "date": "2026-06-04",
        "planned_hours": 8,
        "actual_hours": 7,
        "overtime_hours": 0,
        "attended": "yes",
        "month": "2026-06",
        "week_num": 23
    })
    assert rec_id > 0

    # Проверка агрегации (SUM) через raw query
    db.insert("worked_hours", {
        "employee_id": emp_id,
        "full_name": "Работник Y",
        "date": "2026-06-05",
        "planned_hours": 8,
        "actual_hours": 9,
        "overtime_hours": 1,
        "attended": "yes",
        "month": "2026-06",
        "week_num": 23
    })
    total = db.fetch_one("SELECT SUM(actual_hours) FROM worked_hours WHERE employee_id = ?", (emp_id,))
    assert total[0] == 16


def test_employee_rating(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "Z", "hourly_wage": 400})
    emp_id = db.insert("employees", {"full_name": "Рейтинговый", "position_id": pos_id})

    r_id = db.insert("employee_rating", {
        "employee_id": emp_id,
        "full_name": "Рейтинговый",
        "month": "2026-06",
        "missed_days": 1,
        "quality": 4.5,
        "missed_penalty": -10,
        "overtime_bonus": 5,
        "quality_bonus": 20.0,
        "final_rating": 85.0
    })
    assert r_id > 0


def test_final_salaries(db_with_tables):
    db = db_with_tables
    pos_id = db.insert("positions", {"position_name": "W", "hourly_wage": 500})
    emp_id = db.insert("employees", {"full_name": "Зарплатный", "position_id": pos_id})

    sal_id = db.insert("final_salaries", {
        "employee_id": emp_id,
        "full_name": "Зарплатный",
        "month": "2026-06",
        "actual_hours": 160,
        "hourly_wage": 500,
        "base_pay": 80000,
        "final_rating": 90,
        "rating_multiplier": 1.1,
        "bonus": 8000,
        "final_salary": 88000
    })
    assert sal_id > 0

# ----------------------------------------------------------------------
# Проверка обработки ошибок (негативные сценарии)
# ----------------------------------------------------------------------

def test_insert_missing_required_field(db_with_tables):
    db = db_with_tables
    with pytest.raises(sqlite3.IntegrityError):
        db.insert("positions", {"position_name": "NoWage"})


def test_delete_nonexistent_record(db_with_tables):
    db = db_with_tables
    # Удаление несуществующей записи не должно вызывать исключений
    db.delete("positions", "position_id", 999)
    # Проверяем, что ничего не упало

