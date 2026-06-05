import sqlite3
from typing import List, Dict, Any, Optional
from tkinter import messagebox
import os

class DatabaseManager:
    def __init__(self, db_path: str = "database.db", 
                 sql_file: str = "database_structure.sql",
                 test_data_file: str = "database_test_data.sql",
                 load_test_data: bool = True):
        """
        Args:
            db_path: путь к файлу базы данных
            sql_file: путь к файлу со структурой БД (CREATE TABLE)
            test_data_file: путь к файлу с тестовыми данными (INSERT)
            load_test_data: загружать ли тестовые данные (для продакшена может быть False)
        """
        self.db_path = os.path.abspath(db_path)
        self.sql_file = sql_file
        self.test_data_file = test_data_file
        self.load_test_data = load_test_data
        
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._execute_sql_file(self.sql_file, "структуры БД")
        if self.load_test_data:
            self._execute_sql_file(self.test_data_file, "тестовых данных")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute_sql_file(self, file_path: str, description: str = ""):
        """Выполняет SQL-скрипт из файла"""
        if not os.path.exists(file_path):
            # Для тестовых данных это не ошибка, просто предупреждение
            if description == "тестовых данных":
                print(f"Предупреждение: Файл {file_path} не найден. Тестовые данные не загружены.")
                return
            else:
                messagebox.showwarning("Предупреждение",
                                     f"Файл {file_path} не найден. {description} не будет создана.")
                return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Проверяем, что скрипт не пустой
            if not sql_script.strip():
                return
                
            self.conn.executescript(sql_script)
            self.conn.commit()
        except Exception as e:
            if description == "тестовых данных":
                print(f"Предупреждение: Не удалось загрузить тестовые данные: {e}")
            else:
                messagebox.showerror("Ошибка SQL", f"Не удалось выполнить скрипт {description}:\n{e}")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(query, params)

    def fetch_all(self, query: str, params: tuple = ()) -> List[tuple]:
        return self.execute(query, params).fetchall()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[tuple]:
        return self.execute(query, params).fetchone()

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cur = self.execute(query, tuple(data.values()))
        self.conn.commit()
        return cur.lastrowid

    def update(self, table: str, pk_column: str, pk_value: Any, data: Dict[str, Any]):
        set_clause = ", ".join(f"{col} = ?" for col in data)
        query = f"UPDATE {table} SET {set_clause} WHERE {pk_column} = ?"
        self.execute(query, tuple(data.values()) + (pk_value,))
        self.conn.commit()

    def delete(self, table: str, pk_column: str, pk_value: Any):
        query = f"DELETE FROM {table} WHERE {pk_column} = ?"
        self.execute(query, (pk_value,))
        self.conn.commit()

    def get_all(self, table: str, pk_column: str) -> List[tuple]:
        if pk_column == "rowid":
            return self.fetch_all(f"SELECT rowid, * FROM {table}")
        else:
            return self.fetch_all(f"SELECT * FROM {table}")

    def get_employee_list(self):
        return self.fetch_all("SELECT employee_id, full_name FROM employees ORDER BY full_name")

    def update_vacation_status(self, request_id: int, new_status: str):
        self.update("vacation_requests", "request_id", request_id, {"status": new_status})

    def get_employee_vacations(self, employee_id: int) -> List[tuple]:
        return self.fetch_all(
            "SELECT request_id, employee_id, full_name, start_date, end_date, status FROM vacation_requests WHERE employee_id = ?",
            (employee_id,))