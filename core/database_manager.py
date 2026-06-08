import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any


DATABASE_PATH = "database/app.db"


class DatabaseManager:
    """
    Менеджер базы данных приложения.

    Отвечает за:
    - создание структуры БД;
    - хранение истории конвертации;
    - хранение настроек;
    - получение данных.
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

        Path("database").mkdir(exist_ok=True)

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

    # ==========================================================
    # ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
    # ==========================================================

    def initialize_database(self):
        """
        Создание таблиц базы данных.
        """

        self.create_tasks_table()
        self.create_settings_table()

        self.connection.commit()

    def create_tasks_table(self):
        """
        Таблица задач конвертации.
        """

        query = """
        CREATE TABLE IF NOT EXISTS conversion_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            input_file TEXT NOT NULL,
            output_file TEXT NOT NULL,

            output_format TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'pending',

            progress INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP,

            file_size_mb REAL DEFAULT 0,

            error_message TEXT
        );
        """

        self.cursor.execute(query)

    def create_settings_table(self):
        """
        Таблица настроек программы.
        """

        query = """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """

        self.cursor.execute(query)

    # ==========================================================
    # РАБОТА С ЗАДАЧАМИ
    # ==========================================================

    def add_task(self, task):
        """
        Сохранение задачи в БД.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO conversion_tasks (
                input_file,
                output_file,
                status,
                progress
            )
            VALUES (?, ?, ?, ?)
        """, (
            task.input_file,
            task.output_file,
            str(task.status),
            task.progress
        ))

        self.connection.commit()

        task.id = cursor.lastrowid

    def add_conversion_task(
        self,
        input_file: str,
        output_file: str,
        output_format: str
    ) -> int:
        """
        Добавление задачи конвертации.
        """

        query = """
        INSERT INTO conversion_tasks (
            input_file,
            output_file,
            output_format,
            status
        )
        VALUES (?, ?, ?, ?)
        """

        self.cursor.execute(
            query,
            (
                input_file,
                output_file,
                output_format,
                "pending"
            )
        )

        self.connection.commit()

        return self.cursor.lastrowid

    def update_task_status(
        self,
        task_id,
        status
    ):
        """
        Обновление статуса задачи.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE conversion_tasks
            SET status = ?
            WHERE id = ?
        """, (
            status,
            task_id
        ))

        self.connection.commit()

    def update_task_progress(
        self,
        task_id: int,
        progress: int
    ):
        """
        Обновление прогресса задачи.
        """

        query = """
        UPDATE conversion_tasks
        SET progress = ?
        WHERE id = ?
        """

        self.cursor.execute(
            query,
            (progress, task_id)
        )

        self.connection.commit()

    def complete_task(
        self,
        task_id: int
    ):
        """
        Завершение задачи.
        """

        query = """
        UPDATE conversion_tasks
        SET
            status = 'completed',
            progress = 100,
            finished_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """

        self.cursor.execute(query, (task_id,))
        self.connection.commit()

    def fail_task(
        self,
        task_id: int,
        error_message: str
    ):
        """
        Отметка задачи как завершённой с ошибкой.
        """

        query = """
        UPDATE conversion_tasks
        SET
            status = 'failed',
            error_message = ?,
            finished_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """

        self.cursor.execute(
            query,
            (
                error_message,
                task_id
            )
        )

        self.connection.commit()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Получение списка задач.
        """

        query = """
        SELECT *
        FROM conversion_tasks
        ORDER BY created_at DESC
        """

        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_task_by_id(
        self,
        task_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получение задачи по ID.
        """

        query = """
        SELECT *
        FROM conversion_tasks
        WHERE id = ?
        """

        self.cursor.execute(query, (task_id,))

        row = self.cursor.fetchone()

        return dict(row) if row else None

    def delete_task(
        self,
        task_id: int
    ):
        """
        Удаление задачи.
        """

        query = """
        DELETE FROM conversion_tasks
        WHERE id = ?
        """

        self.cursor.execute(query, (task_id,))
        self.connection.commit()

    def clear_history(self):
        """
        Очистка истории задач.
        """

        query = """
        DELETE FROM conversion_tasks
        """

        self.cursor.execute(query)
        self.connection.commit()

    # ==========================================================
    # РАБОТА С НАСТРОЙКАМИ
    # ==========================================================

    def save_setting(
        self,
        key: str,
        value: str
    ):
        """
        Сохранение настройки.
        """

        query = """
        INSERT OR REPLACE INTO settings (
            key,
            value
        )
        VALUES (?, ?)
        """

        self.cursor.execute(
            query,
            (
                key,
                value
            )
        )

        self.connection.commit()

    def get_setting(
        self,
        key: str,
        default: Optional[str] = None
    ) -> Optional[str]:
        """
        Получение настройки.
        """

        query = """
        SELECT value
        FROM settings
        WHERE key = ?
        """

        self.cursor.execute(query, (key,))

        row = self.cursor.fetchone()

        if row:
            return row["value"]

        return default

    def delete_setting(self, key: str):
        """
        Удаление настройки.
        """

        query = """
        DELETE FROM settings
        WHERE key = ?
        """

        self.cursor.execute(query, (key,))
        self.connection.commit()

    # ==========================================================
    # СЛУЖЕБНЫЕ МЕТОДЫ
    # ==========================================================

    def vacuum_database(self):
        """
        Оптимизация БД.
        """

        self.cursor.execute("VACUUM")
        self.connection.commit()

    def close(self):
        """
        Закрытие соединения.
        """

        if self.connection:
            self.connection.close()

    def __del__(self):
        """
        Автоматическое закрытие.
        """

        try:
            self.close()
        except Exception:
            pass