import pytest
import sqlite3
import tempfile
from pathlib import Path
from packages.core.management import DatabaseManager

# Пути к SQL-файлам
PROJECT_ROOT = Path(__file__).parent.parent.parent
SQL_STRUCTURE = PROJECT_ROOT / "infra" / "db" / "database_structure.sql"

class TestDatabaseManager:
    def test_connect_creates_tables(self):
        """Проверка, что при подключении создаются все таблицы"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False  # Не загружаем тестовые данные
            )
            db.connect()
            
            tables = db.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            table_names = [t[0] for t in tables]
            
            expected = ["positions", "employees", "vacation_requests", 
                       "schedule_5_2", "worked_hours", "employee_rating", 
                       "final_salaries"]
            for table in expected:
                assert table in table_names
    
    def test_insert_and_get(self):
        """Проверка вставки и получения записи"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False
            )
            db.connect()
            
            data = {"position_name": "Повар", "hourly_wage": 250.0}
            position_id = db.insert("positions", data)
            
            result = db.fetch_one(
                "SELECT position_name, hourly_wage FROM positions WHERE position_id = ?",
                (position_id,)
            )
            assert result[0] == "Повар"
            assert result[1] == 250.0
    
    def test_update_record(self):
        """Проверка обновления записи"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False
            )
            db.connect()
            
            data = {"position_name": "Официант", "hourly_wage": 200.0}
            pos_id = db.insert("positions", data)
            
            db.update("positions", "position_id", pos_id, {"hourly_wage": 220.0})
            
            result = db.fetch_one(
                "SELECT hourly_wage FROM positions WHERE position_id = ?",
                (pos_id,)
            )
            assert result[0] == 220.0
    
    def test_delete_record(self):
        """Проверка удаления записи"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False
            )
            db.connect()
            
            data = {"position_name": "Уборщик", "hourly_wage": 150.0}
            pos_id = db.insert("positions", data)
            
            db.delete("positions", "position_id", pos_id)
            
            result = db.fetch_one(
                "SELECT * FROM positions WHERE position_id = ?",
                (pos_id,)
            )
            assert result is None
    
    def test_get_employee_list(self):
        """Проверка получения списка сотрудников"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False
            )
            db.connect()
            
            pos_id = db.insert("positions", {"position_name": "Шеф", "hourly_wage": 500.0})
            
            db.insert("employees", {"full_name": "Иванов Иван", "position_id": pos_id})
            db.insert("employees", {"full_name": "Петров Петр", "position_id": pos_id})
            
            employees = db.get_employee_list()
            assert len(employees) == 2
    
    def test_update_vacation_status(self):
        """Проверка изменения статуса заявки на отпуск"""
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
            db = DatabaseManager(
                db_path=tmp.name, 
                sql_file=str(SQL_STRUCTURE),
                load_test_data=False
            )
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
            assert result[0] == "approved"