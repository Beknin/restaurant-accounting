import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple


TABLE_CONFIG = {
    "positions": {
        "columns": ["position_name", "hourly_wage"],
        "headers": ["Должность", "Почасовая ставка"],
        "types": [str, float],
        "pk": "position_id",
        "tab_name": "Должности"
    },
    "employees": {
        "columns": ["full_name", "position_id"],
        "headers": ["ФИО", "ID должности"],
        "types": [str, int],
        "pk": "employee_id",
        "tab_name": "Сотрудники"
    },
    "vacation_requests": {
        "columns": ["employee_id", "full_name", "start_date", "end_date", "status"],
        "headers": ["ID сотрудника", "ФИО", "Дата начала", "Дата окончания", "Статус"],
        "types": [int, str, str, str, str],
        "pk": "request_id",
        "tab_name": "Заявки на отпуск"
    },
    "schedule_5_2": {
        "columns": ["employee_id", "full_name", "date", "shift_type", "planned_hours"],
        "headers": ["ID сотрудника", "ФИО", "Дата", "Тип смены", "Часов по плану"],
        "types": [int, str, str, str, int],
        "pk": "id",                     
        "tab_name": "График 5/2"
    },
    "worked_hours": {
        "columns": ["employee_id", "full_name", "date", "planned_hours", "actual_hours",
                    "overtime_hours", "attended", "month", "week_num"],
        "headers": ["ID сотрудника", "ФИО", "Дата", "План часов", "Факт часов",
                    "Переработка", "Явка", "Месяц", "Неделя"],
        "types": [int, str, str, int, int, int, str, str, int],
        "pk": "record_id",
        "tab_name": "Отработанные часы"
    },
    "employee_rating": {
        "columns": ["employee_id", "full_name", "month", "missed_days",
                    "quality", "missed_penalty", "overtime_bonus",
                    "quality_bonus", "final_rating"],
        "headers": ["ID сотрудника", "ФИО", "Месяц", "Пропущено дней",
                    "Качество", "Штраф за пропуски", "Бонус за переработку",
                    "Бонус за качество", "Итоговый рейтинг"],
        "types": [int, str, str, int, float, int, int, float, float],
        "pk": "id",                     
        "tab_name": "Рейтинг сотрудников"
    },
    "final_salaries": {
        "columns": ["employee_id", "full_name", "month", "actual_hours",
                    "hourly_wage", "base_pay", "final_rating",
                    "rating_multiplier", "bonus", "final_salary"],
        "headers": ["ID сотрудника", "ФИО", "Месяц", "Отработано часов",
                    "Почасовая ставка", "Базовая оплата", "Итоговый рейтинг",
                    "Множитель рейтинга", "Бонус", "Итоговая зарплата"],
        "types": [int, str, str, int, float, float, float, float, float, float],
        "pk": "id",                     
        "tab_name": "Итоговые зарплаты"
    }
}



class DatabaseManager:
    def __init__(self, db_path: str = "database.db", sql_file: str = "restaurant_accounting.sql"):
        self.db_path = db_path
        self.sql_file = sql_file
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



class LoginWindow(tk.Tk):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.title("Вход в систему учёта ресторана")
        self.geometry("400x250")
        self.resizable(False, False)

        ttk.Label(self, text="Выберите роль", font=("Arial", 14)).pack(pady=10)

        self.role_var = tk.StringVar(value="hr")
        ttk.Radiobutton(self, text="HR-сотрудник", variable=self.role_var, value="hr").pack(anchor=tk.W, padx=20, pady=5)
        ttk.Radiobutton(self, text="Работник", variable=self.role_var, value="employee").pack(anchor=tk.W, padx=20,
                                                                                              pady=5)

        self.emp_frame = ttk.Frame(self)
        self.emp_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(self.emp_frame, text="Сотрудник:").pack(side=tk.LEFT)
        self.employee_cb = ttk.Combobox(self.emp_frame, state="readonly", width=30)
        self.employee_cb.pack(side=tk.LEFT, padx=5)

        try:
            employees = self.db.get_employee_list()
            self.employee_dict = {f"{emp[1]} (ID: {emp[0]})": emp[0] for emp in employees}
            self.employee_cb['values'] = list(self.employee_dict.keys())
            if self.employee_dict:
                self.employee_cb.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список сотрудников:\n{e}")
            self.employee_dict = {}

        self.role_var.trace_add("write", self.toggle_employee_choice)
        self.toggle_employee_choice()

        ttk.Button(self, text="Войти", command=self.login).pack(pady=20)
        self.main_window = None

    def toggle_employee_choice(self, *args):
        if self.role_var.get() == "hr":
            self.employee_cb.configure(state="disabled")
        else:
            self.employee_cb.configure(state="readonly")

    def login(self):
        role = self.role_var.get()
        if role == "hr":
            self.withdraw()
            HRMainWindow(self, self.db)
        else:
            if not self.employee_dict:
                messagebox.showwarning("Ошибка", "Нет сотрудников в базе.")
                return
            emp_name = self.employee_cb.get()
            if emp_name not in self.employee_dict:
                messagebox.showwarning("Ошибка", "Выберите сотрудника из списка.")
                return
            employee_id = self.employee_dict[emp_name]
            self.withdraw()
            EmployeeMainWindow(self, self.db, employee_id)

    def return_to_login(self, child_window):
        child_window.destroy()
        self.deiconify()



class ReadOnlyTableTab(ttk.Frame):
    def __init__(self, parent, db: DatabaseManager, table_name: str, config: dict,
                 custom_query: str = None, query_params: tuple = ()):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.config = config
        self.pk = config["pk"]
        self.columns = config["columns"]
        self.headers = config["headers"]
        self.custom_query = custom_query
        self.query_params = query_params

        
        if self.pk == "rowid":
            self.display_columns = ("rowid", *self.columns)
            self.column_headers = ["ID", *self.headers]
        else:
            
            
            self.display_columns = (self.pk, *self.columns)
            self.column_headers = ["ID", *self.headers]

        self.tree = ttk.Treeview(self, columns=self.display_columns, show="headings", selectmode="browse")
        for col, hdr in zip(self.display_columns, self.column_headers):
            self.tree.heading(col, text=hdr)
            width = 40 if col in ("rowid", self.pk) else 120
            anchor = tk.CENTER if col in ("rowid", self.pk) else tk.W
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if self.custom_query:
            rows = self.db.fetch_all(self.custom_query, self.query_params)
        else:
            rows = self.db.get_all(self.table_name, self.pk)
        for row in rows:
            self.tree.insert("", tk.END, values=row)


class EmployeeVacationTab(ttk.Frame):
    def __init__(self, parent, db: DatabaseManager, employee_id: int, full_name: str):
        super().__init__(parent)
        self.db = db
        self.employee_id = employee_id
        self.full_name = full_name

        self.tree = ttk.Treeview(self, columns=("request_id", "employee_id", "full_name",
                                                "start_date", "end_date", "status"),
                                 show="headings", selectmode="browse")
        headers = ["ID заявки", "ID сотр.", "ФИО", "Начало", "Конец", "Статус"]
        for col, hdr in zip(self.tree["columns"], headers):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=100, anchor=tk.W)
        self.tree.column("request_id", width=60, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")
        scrollbar.grid(row=0, column=2, sticky="ns")

        ttk.Button(self, text="Подать заявку на отпуск", command=self.new_request).grid(
            row=1, column=0, pady=10, padx=5, sticky=tk.W)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            requests = self.db.get_employee_vacations(self.employee_id)
            for req in requests:
                self.tree.insert("", tk.END, values=req)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заявки: {e}")

    def new_request(self):
        dialog = tk.Toplevel(self)
        dialog.title("Новая заявка на отпуск")
        dialog.geometry("300x200")
        dialog.grab_set()

        ttk.Label(dialog, text="Дата начала (ГГГГ-ММ-ДД):").pack(pady=5)
        start_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=start_var).pack(pady=5)

        ttk.Label(dialog, text="Дата окончания (ГГГГ-ММ-ДД):").pack(pady=5)
        end_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=end_var).pack(pady=5)

        def submit():
            start = start_var.get().strip()
            end = end_var.get().strip()
            if not start or not end:
                messagebox.showwarning("Проверка", "Заполните обе даты.")
                return
            try:
                data = {
                    "employee_id": self.employee_id,
                    "full_name": self.full_name,
                    "start_date": start,
                    "end_date": end,
                    "status": "pending"
                }
                self.db.insert("vacation_requests", data)
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Успех", "Заявка подана.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать заявку: {e}")

        ttk.Button(dialog, text="Отправить", command=submit).pack(pady=20)
        dialog.wait_window()



class HRMainWindow(tk.Toplevel):
    def __init__(self, login_window, db: DatabaseManager):
        super().__init__()
        self.login_window = login_window
        self.db = db
        self.title("HR-панель управления персоналом")
        self.geometry("1200x700")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выйти в меню входа", command=self.on_close)
        menubar.add_cascade(label="Файл", menu=file_menu)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        for table, cfg in TABLE_CONFIG.items():
            if table == "vacation_requests":
                tab = HRVacationTab(self.notebook, self.db, cfg)
            else:
                tab = FullCRUDTab(self.notebook, self.db, table, cfg)
            self.notebook.add(tab, text=cfg["tab_name"])

        report_tab = ReportTab(self.notebook, self.db)
        self.notebook.add(report_tab, text="Отчёты")

    def on_close(self):
        self.login_window.return_to_login(self)


class FullCRUDTab(ttk.Frame):
    def __init__(self, parent, db: DatabaseManager, table_name: str, config: dict):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.config = config
        self.pk = config["pk"]
        self.columns = config["columns"]
        self.headers = config["headers"]
        self.types = config["types"]

        if self.pk == "rowid":
            self.display_columns = ("rowid", *self.columns)
            self.column_headers = ["ID", *self.headers]
        else:
            self.display_columns = (self.pk, *self.columns)
            self.column_headers = ["ID", *self.headers]

        self.tree = ttk.Treeview(self, columns=self.display_columns, show="headings", selectmode="browse")
        for col, hdr in zip(self.display_columns, self.column_headers):
            self.tree.heading(col, text=hdr)
            width = 40 if col in ("rowid", self.pk) else 120
            anchor = tk.CENTER if col in ("rowid", self.pk) else tk.W
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_panel = ttk.Frame(self)
        btn_panel.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(btn_panel, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_panel, text="Добавить", command=self.add_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_panel, text="Изменить", command=self.edit_record).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_panel, text="Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=2)

        self.tree.bind("<Double-1>", lambda e: self.edit_record())
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            rows = self.db.get_all(self.table_name, self.pk)
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def get_selected_pk(self) -> Optional[Any]:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Выбор", "Сначала выберите запись.")
            return None
        return self.tree.item(sel[0], "values")[0]

    def add_record(self):
        fields = [(col, hdr, t) for col, hdr, t in zip(self.columns, self.headers, self.types)]
        dlg = RecordDialog(self, f"Добавить запись в {self.config['tab_name']}", fields)
        if dlg.result:
            try:
                self.db.insert(self.table_name, dlg.result)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def edit_record(self):
        pk_val = self.get_selected_pk()
        if pk_val is None:
            return
        
        if self.pk == "rowid":
            row_data = self.db.fetch_one(f"SELECT * FROM {self.table_name} WHERE rowid = ?", (pk_val,))
        else:
            row_data = self.db.fetch_one(f"SELECT * FROM {self.table_name} WHERE {self.pk} = ?", (pk_val,))
        if not row_data:
            messagebox.showerror("Ошибка", "Запись не найдена.")
            return
        
        
        
        
        if self.pk == "rowid":
            
            initial = {col: val for col, val in zip(self.columns, row_data)}
        else:
            
            initial = {col: val for col, val in zip(self.columns, row_data[1:])}
        fields = [(col, hdr, t) for col, hdr, t in zip(self.columns, self.headers, self.types)]
        dlg = RecordDialog(self, f"Редактировать запись ID={pk_val}", fields, initial)
        if dlg.result:
            try:
                pk_col = "rowid" if self.pk == "rowid" else self.pk
                self.db.update(self.table_name, pk_col, pk_val, dlg.result)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_record(self):
        pk_val = self.get_selected_pk()
        if pk_val is None:
            return
        if messagebox.askyesno("Подтверждение", f"Удалить запись с ID={pk_val}?"):
            try:
                pk_col = "rowid" if self.pk == "rowid" else self.pk
                self.db.delete(self.table_name, pk_col, pk_val)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))


class HRVacationTab(ttk.Frame):
    def __init__(self, parent, db: DatabaseManager, config: dict):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.columns = config["columns"]
        self.headers = config["headers"]

        self.tree = ttk.Treeview(self, columns=("request_id", *self.columns), show="headings", selectmode="browse")
        all_headers = ["ID заявки"] + self.headers
        all_cols = ("request_id", *self.columns)
        for col, hdr in zip(all_cols, all_headers):
            self.tree.heading(col, text=hdr)
            width = 60 if col == "request_id" else 120
            self.tree.column(col, width=width, anchor=tk.W)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, columnspan=3, sticky="nsew")
        scrollbar.grid(row=0, column=3, sticky="ns")

        btn_panel = ttk.Frame(self)
        btn_panel.grid(row=1, column=0, columnspan=4, pady=5)
        ttk.Button(btn_panel, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_panel, text="Одобрить", command=lambda: self.change_status("approved")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_panel, text="Отклонить", command=lambda: self.change_status("rejected")).pack(side=tk.LEFT, padx=2)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            rows = self.db.get_all("vacation_requests", "request_id")
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def get_selected_request_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Выбор", "Выберите заявку.")
            return None
        return self.tree.item(sel[0], "values")[0]

    def change_status(self, new_status):
        req_id = self.get_selected_request_id()
        if req_id is None:
            return
        try:
            self.db.update_vacation_status(req_id, new_status)
            self.load_data()
            messagebox.showinfo("Успех", f"Статус заявки изменён на '{new_status}'.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class ReportTab(ttk.Frame):
    def __init__(self, parent, db: DatabaseManager):
        super().__init__(parent)
        self.db = db

        ttk.Label(self, text="Отчёты", font=("Arial", 14)).pack(pady=10)

        ttk.Button(self, text="Сводка по зарплатам за месяц", command=self.salary_summary).pack(pady=5)
        ttk.Button(self, text="Рейтинг сотрудников (последние записи)", command=self.rating_report).pack(pady=5)
        ttk.Button(self, text="Отработанные часы по сотрудникам", command=self.hours_report).pack(pady=5)

        self.result_frame = ttk.Frame(self)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.result_tree = None

    def clear_result(self):
        
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.result_tree = None

    def show_query_result(self, columns, headers, rows):
        self.clear_result()
        tree = ttk.Treeview(self.result_frame, columns=columns, show="headings")
        for col, hdr in zip(columns, headers):
            tree.heading(col, text=hdr)
            tree.column(col, width=100, anchor=tk.W)
        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for row in rows:
            tree.insert("", tk.END, values=row)
        self.result_tree = tree

    def salary_summary(self):
        try:
            query = """
                SELECT month, employee_id, full_name, final_salary
                FROM final_salaries
                ORDER BY month DESC, employee_id
            """
            rows = self.db.fetch_all(query)
            self.show_query_result(
                ["month", "employee_id", "full_name", "final_salary"],
                ["Месяц", "ID сотр.", "ФИО", "Итоговая зарплата"],
                rows)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def rating_report(self):
        try:
            query = """
                SELECT er.employee_id, er.full_name, er.month, er.final_rating,
                       er.quality, er.overtime_bonus, er.missed_days
                FROM employee_rating er
                INNER JOIN (
                    SELECT employee_id, MAX(month) AS max_month
                    FROM employee_rating
                    GROUP BY employee_id
                ) latest ON er.employee_id = latest.employee_id AND er.month = latest.max_month
                ORDER BY er.final_rating DESC
            """
            rows = self.db.fetch_all(query)
            self.show_query_result(
                ["employee_id", "full_name", "month", "final_rating", "quality",
                 "overtime_bonus", "missed_days"],
                ["ID сотр.", "ФИО", "Месяц", "Рейтинг", "Качество",
                 "Бонус за переработку", "Пропуски"],
                rows)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def hours_report(self):
        try:
            query = """
                SELECT employee_id, full_name, month, SUM(actual_hours) AS total_actual,
                       SUM(planned_hours) AS total_planned,
                       SUM(overtime_hours) AS total_overtime
                FROM worked_hours
                GROUP BY employee_id, month
                ORDER BY month DESC, employee_id
            """
            rows = self.db.fetch_all(query)
            self.show_query_result(
                ["employee_id", "full_name", "month", "total_actual",
                 "total_planned", "total_overtime"],
                ["ID сотр.", "ФИО", "Месяц", "Факт часы", "План часы", "Переработка"],
                rows)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class EmployeeMainWindow(tk.Toplevel):
    def __init__(self, login_window, db: DatabaseManager, employee_id: int):
        super().__init__()
        self.login_window = login_window
        self.db = db
        self.employee_id = employee_id

        emp = self.db.fetch_one("SELECT full_name FROM employees WHERE employee_id = ?", (employee_id,))
        self.full_name = emp[0] if emp else "Неизвестный"

        self.title(f"Личный кабинет – {self.full_name}")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выйти в меню входа", command=self.on_close)
        menubar.add_cascade(label="Файл", menu=file_menu)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        info_tab = self._create_info_tab()
        self.notebook.add(info_tab, text="Мои данные")

        
        schedule_tab = ReadOnlyTableTab(
            self.notebook, self.db, "schedule_5_2", TABLE_CONFIG["schedule_5_2"],
            custom_query="SELECT * FROM schedule_5_2 WHERE employee_id = ?",
            query_params=(employee_id,))
        self.notebook.add(schedule_tab, text="Мой график")

        
        hours_tab = ReadOnlyTableTab(
            self.notebook, self.db, "worked_hours", TABLE_CONFIG["worked_hours"],
            custom_query="SELECT * FROM worked_hours WHERE employee_id = ?",
            query_params=(employee_id,))
        self.notebook.add(hours_tab, text="Мои часы")

        
        vacation_tab = EmployeeVacationTab(self.notebook, self.db, employee_id, self.full_name)
        self.notebook.add(vacation_tab, text="Мои отпуска")

        
        rating_tab = ReadOnlyTableTab(
            self.notebook, self.db, "employee_rating", TABLE_CONFIG["employee_rating"],
            custom_query="SELECT * FROM employee_rating WHERE employee_id = ?",
            query_params=(employee_id,))
        self.notebook.add(rating_tab, text="Мой рейтинг")

        
        salary_tab = ReadOnlyTableTab(
            self.notebook, self.db, "final_salaries", TABLE_CONFIG["final_salaries"],
            custom_query="SELECT * FROM final_salaries WHERE employee_id = ?",
            query_params=(employee_id,))
        self.notebook.add(salary_tab, text="Мои зарплаты")

    def _create_info_tab(self):
        frame = ttk.Frame(self.notebook)
        emp = self.db.fetch_one("""
            SELECT e.employee_id, e.full_name, p.position_name, p.hourly_wage
            FROM employees e
            JOIN positions p ON e.position_id = p.position_id
            WHERE e.employee_id = ?
        """, (self.employee_id,))

        if emp:
            labels = [
                ("ID сотрудника:", emp[0]),
                ("ФИО:", emp[1]),
                ("Должность:", emp[2]),
                ("Почасовая ставка:", f"{emp[3]:.2f} руб.")
            ]
            for i, (name, value) in enumerate(labels):
                ttk.Label(frame, text=name, font=("Arial", 12, "bold")).grid(
                    row=i, column=0, sticky=tk.W, padx=20, pady=5)
                ttk.Label(frame, text=str(value), font=("Arial", 12)).grid(
                    row=i, column=1, sticky=tk.W, padx=20, pady=5)
        else:
            ttk.Label(frame, text="Информация о сотруднике не найдена.", font=("Arial", 12)).pack(pady=20)

        return frame

    def on_close(self):
        self.login_window.return_to_login(self)



class RecordDialog(tk.Toplevel):
    def __init__(self, parent, title: str, fields: List[Tuple[str, str, type]],
                 initial: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.entries = {}

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        for i, (field_name, header, field_type) in enumerate(fields):
            ttk.Label(frame, text=header).grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar()
            if initial and field_name in initial:
                var.set(str(initial[field_name]) if initial[field_name] is not None else "")
            entry = ttk.Entry(frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, pady=2, padx=5)
            self.entries[field_name] = (var, field_type)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Сохранить", command=self.on_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set()
        self.wait_window()

    def on_save(self):
        data = {}
        for name, (var, field_type) in self.entries.items():
            raw = var.get().strip()
            if raw == "":
                messagebox.showwarning("Проверка", f"Поле '{name}' не должно быть пустым.")
                return
            try:
                if field_type == int:
                    data[name] = int(raw)
                elif field_type == float:
                    data[name] = float(raw)
                else:
                    data[name] = raw
            except ValueError:
                messagebox.showwarning("Ошибка типа", f"Некорректное значение в поле '{name}'.")
                return
        self.result = data
        self.destroy()



if __name__ == "__main__":
    db = DatabaseManager()
    try:
        db.connect()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Не удалось подключиться к БД: {e}")
        exit(1)

    app = LoginWindow(db)
    app.mainloop()