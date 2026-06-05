import sqlite3
from typing import List, Dict, Any, Optional
from tkinter import messagebox
import os

class DatabaseManager:
    def __init__(self, db_path: str = "database.db", sql_file: str = "restaurant_accounting.sql"):
        self.db_path = os.path.abspath(db_path)
        self.sql_file = sql_file
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._execute_sql_file()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute_sql_file(self):
        if not os.path.exists(self.sql_file):
            messagebox.showwarning("Предупреждение",
                                   f"Файл {self.sql_file} не найден. Структура БД не будет создана.")
            return
        try:
            with open(self.sql_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            self.conn.executescript(sql_script)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Ошибка SQL", f"Не удалось выполнить скрипт:\n{e}")

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