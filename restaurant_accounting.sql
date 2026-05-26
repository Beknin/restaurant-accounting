CREATE TABLE IF NOT EXISTS `positions` (
	`position_id` INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
	`position` TEXT NOT NULL,
	`hourly_wage` REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS `employees` (
	`employee_id` INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
	`full_name` TEXT NOT NULL,
	`position_id` INTEGER NOT NULL,
	FOREIGN KEY (`position_id`) REFERENCES `positions`(`position_id`)
);
CREATE TABLE IF NOT EXISTS `vacation_requests` (
	`request_id` INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
	`employee_id` INTEGER NOT NULL,
	`full_name` TEXT NOT NULL,
	`start_date` TEXT NOT NULL,
	`end_date` TEXT NOT NULL,
	`status` TEXT NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
);
CREATE TABLE IF NOT EXISTS `schedule_5_2` (
	`employee_id` INTEGER NOT NULL,
	`full_name` TEXT NOT NULL,
	`date` TEXT NOT NULL,
	`shift_type` TEXT NOT NULL,
	`planned_hours` INTEGER NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
);
CREATE TABLE IF NOT EXISTS `worked_hours` (
	`record_id` INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
	`employee_id` INTEGER NOT NULL,
	`full_name` TEXT NOT NULL,
	`planned_hours` INTEGER NOT NULL,
	`actual_hours` INTEGER NOT NULL,
	`overtime` INTEGER NOT NULL,
	`attended` TEXT NOT NULL,
	`month` TEXT NOT NULL,
	`week_num` INTEGER NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
);
CREATE TABLE IF NOT EXISTS `employee_rating` (
	`employee_id` INTEGER NOT NULL,
	`full_name` TEXT NOT NULL,
	`month` TEXT NOT NULL,
	`missed_days` INTEGER NOT NULL,
	`total_overtime` INTEGER NOT NULL,
	`quality` REAL NOT NULL,
	`missed_penalty` INTEGER NOT NULL,
	`quality_bonus` REAL NOT NULL,
	`final_rating` REAL NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
);
CREATE TABLE IF NOT EXISTS `final_salaries` (
	`employee_id` INTEGER NOT NULL,
	`full_name` TEXT NOT NULL,
	`month` TEXT NOT NULL,
	`actual_hours` INTEGER NOT NULL,
	`hourly_wage` REAL NOT NULL,
	`base_pay` REAL NOT NULL,
	`final_rating` REAL NOT NULL,
	`rating_multiplier` REAL NOT NULL,
	`bonus` REAL NOT NULL,
	`final_salary` REAL NOT NULL,
	FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
);