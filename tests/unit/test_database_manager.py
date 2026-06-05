# tests/unit/test_database_manager.py
import pytest
import sqlite3
import tempfile
from pathlib import Path
from packages.core.management import DatabaseManager

PROJECT_ROOT = Path(__file__).parent.parent.parent
SQL_STRUCTURE = PROJECT_ROOT / "infra" / "db" / "database_structure.sql"

class TestDatabaseManager:
    # ===== POSITIVE TESTS =====
    
    def test_connect_creates_all_required_tables(self):
        """При подключении создаются все 7 таблиц для учёта ресторана"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [t[0] for t in tables]
            
            expected = ["positions", "employees", "vacation_requests", 
                       "schedule_5_2", "worked_hours", "employee_rating", 
                       "final_salaries"]
            for table in expected:
                assert table in table_names, f"Таблица {table} должна быть создана"
    
    def test_insert_returns_new_record_id(self):
        """Вставка возвращает ID новой записи, увеличенный на 1"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            data = {"position_name": "Повар", "hourly_wage": 250.0}
            position_id = db.insert("positions", data)
            
            result = db.fetch_one(
                "SELECT position_name, hourly_wage FROM positions WHERE position_id = ?",
                (position_id,)
            )
            assert result[0] == "Повар"
            assert result[1] == 250.0
    
    def test_update_changes_only_specified_fields(self):
        """Обновление меняет только указанные поля, остальные остаются без изменений"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            data = {"position_name": "Официант", "hourly_wage": 200.0}
            pos_id = db.insert("positions", data)
            
            db.update("positions", "position_id", pos_id, {"hourly_wage": 220.0})
            
            result = db.fetch_one(
                "SELECT position_name, hourly_wage FROM positions WHERE position_id = ?",
                (pos_id,)
            )
            assert result[0] == "Официант"  # Имя не изменилось
            assert result[1] == 220.0       # Ставка обновилась
    
    def test_delete_removes_record_completely(self):
        """После удаления запись не находится ни по одному полю"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            data = {"position_name": "Уборщик", "hourly_wage": 150.0}
            pos_id = db.insert("positions", data)
            
            db.delete("positions", "position_id", pos_id)
            
            result = db.fetch_one(
                "SELECT * FROM positions WHERE position_id = ?",
                (pos_id,)
            )
            assert result is None, "Удалённая запись не должна находиться"
    
    def test_get_employee_list_returns_only_added_employees(self):
        """Список сотрудников содержит только добавленных, без лишних записей"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            pos_id = db.insert("positions", {"position_name": "Шеф", "hourly_wage": 500.0})
            db.insert("employees", {"full_name": "Иванов Иван", "position_id": pos_id})
            db.insert("employees", {"full_name": "Петров Петр", "position_id": pos_id})
            
            employees = db.get_employee_list()
            assert len(employees) == 2, "Должно быть ровно 2 сотрудника"
            names = [emp[1] for emp in employees]
            assert "Иванов Иван" in names
            assert "Петров Петр" in names
    
    def test_update_vacation_status_changes_pending_to_approved(self):
        """Статус заявки меняется с 'pending' на 'approved'"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            pos_id = db.insert("positions", {"position_name": "Повар", "hourly_wage": 300.0})
            emp_id = db.insert("employees", {"full_name": "Сидоров Сидор", "position_id": pos_id})
            
            req_id = db.insert("vacation_requests", {
                "employee_id": emp_id,
                "full_name": "Сидоров Сидор",
                "start_date": "2026-07-01",
                "end_date": "2026-07-14",
                "status": "pending"
            })
            
            db.update_vacation_status(req_id, "approved")
            
            result = db.fetch_one(
                "SELECT status FROM vacation_requests WHERE request_id = ?",
                (req_id,)
            )
            assert result[0] == "approved", "Статус должен измениться на approved"
    
    # ===== NEGATIVE TESTS =====
    
    def test_insert_to_nonexistent_table_raises_error(self):
        """Попытка вставки в несуществующую таблицу вызывает OperationalError"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            with pytest.raises(sqlite3.OperationalError) as exc_info:
                db.insert("nonexistent_table", {"field": "value"})
            assert "no such table" in str(exc_info.value).lower(), \
                "Ошибка должна указывать на отсутствие таблицы"
    
    def test_insert_without_required_field_raises_error(self):
        """Вставка без обязательного поля вызывает IntegrityError из-за NOT NULL"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            with pytest.raises(sqlite3.IntegrityError) as exc_info:
                db.insert("positions", {"position_name": "Тест"})  # Нет hourly_wage
            assert "NOT NULL" in str(exc_info.value), \
                "Ошибка должна указывать на ограничение NOT NULL"
    
    def test_foreign_key_violation_raises_error(self):
        """Вставка сотрудника с несуществующей должностью нарушает внешний ключ"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            with pytest.raises(sqlite3.IntegrityError) as exc_info:
                db.insert("employees", {
                    "full_name": "Тестов Тест", 
                    "position_id": 9999  # Несуществующая должность
                })
            assert "FOREIGN KEY" in str(exc_info.value), \
                "Ошибка должна указывать на нарушение внешнего ключа"
    
    def test_delete_parent_record_with_children_raises_error(self):
        """Удаление должности с привязанными сотрудниками вызывает IntegrityError"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            pos_id = db.insert("positions", {"position_name": "Тест", "hourly_wage": 100.0})
            db.insert("employees", {"full_name": "Тестов Тест", "position_id": pos_id})
            
            with pytest.raises(sqlite3.IntegrityError) as exc_info:
                db.delete("positions", "position_id", pos_id)
            assert "FOREIGN KEY" in str(exc_info.value), \
                "Нельзя удалить должность с привязанными сотрудниками"
    
    def test_close_connection_prevents_further_queries(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            db.close()
            
            # После close() conn = None, поэтому будет AttributeError
            with pytest.raises(AttributeError) as exc_info:
                db.fetch_all("SELECT * FROM positions")
            assert "NoneType" in str(exc_info.value), \
                "Соединение должно быть None после закрытия"
    
    def test_update_nonexistent_record_does_nothing(self):
        """Обновление несуществующей записи не вызывает ошибку, но ничего не меняет"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            # Не должно вызывать исключений
            db.update("positions", "position_id", 9999, {"position_name": "Невидимка"})
            
            # Проверяем, что запись не появилась
            result = db.fetch_one("SELECT * FROM positions WHERE position_id = 9999")
            assert result is None, "Несуществующая запись не должна появиться после update"
    
    def test_get_employee_vacations_for_nonexistent_employee_returns_empty(self):
        """Запрос отпусков для несуществующего сотрудника возвращает пустой список"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(db_path=tmp.name, sql_file=str(SQL_STRUCTURE), load_test_data=False)
            db.connect()
            
            vacations = db.get_employee_vacations(9999)
            assert vacations == [], "Для несуществующего сотрудника должен быть пустой список"
            assert isinstance(vacations, list), "Результат должен быть списком"
    
    def test_sql_file_not_found_shows_warning(self):
        """Отсутствие SQL-файла не вызывает падения, а показывает предупреждение"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file="nonexistent_file.sql",
                load_test_data=False
            )
            # Не должно вызывать исключений при connect
            db.connect()
            # Таблицы не созданы
            tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
            assert len(tables) == 0, "Без SQL-файла таблицы не должны создаваться"