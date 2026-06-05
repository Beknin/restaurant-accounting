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