from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QMenu,
    QMessageBox
)

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from core.models import ConversionTask


class TaskTable(QWidget):
    """
    Таблица задач конвертации.
    """

    task_removed = Signal(int)

    def __init__(self):
        super().__init__()

        self.tasks = {}

        self.setup_ui()

    def setup_ui(self):
        """
        Создание интерфейса таблицы.
        """

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "Файл",
            "Формат",
            "Статус",
            "Прогресс",
            "Размер",
            "Выходной файл"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.table.customContextMenuRequested.connect(
            self.show_context_menu
        )

        layout.addWidget(self.table)

    # =====================================================
    # ДОБАВЛЕНИЕ ЗАДАЧИ
    # =====================================================

    def add_task(self, task: ConversionTask):
        """
        Добавление задачи в таблицу.
        """

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.tasks[task.id] = row

        # ==========================
        # Имя файла
        # ==========================

        file_name = (
            task.input_file
            .split("/")[-1]
        )

        file_item = QTableWidgetItem(
            file_name
        )

        # ==========================
        # Формат
        # ==========================

        output_format = "-"

        if (
            task.output_file
            and "." in task.output_file
        ):
            output_format = (
                task.output_file
                .split(".")[-1]
                .upper()
            )

        format_item = QTableWidgetItem(
            output_format
        )

        # ==========================
        # Статус
        # ==========================

        STATUS_TEXT = {
            "pending": "Ожидание",
            "running": "Выполняется",
            "completed": "Завершено",
            "failed": "Ошибка",
            "cancelled": "Отменено"
        }
        
        status_item = QTableWidgetItem(
            STATUS_TEXT.get(task.status.value,
                            task.status.value)
        )

        # ==========================
        # Размер
        # ==========================

        try:
            file_size = Path(
                task.input_file
            ).stat().st_size
        except Exception:
            file_size = 0

        size_item = (
            QTableWidgetItem(
                self.format_size(file_size)
            )
        )

        # ==========================
        # Выходной путь
        # ==========================

        output_item = (
            QTableWidgetItem(
                Path(task.output_file).name
            )
        )

        # ==========================
        # Progress Bar
        # ==========================

        progress_bar = (
            QProgressBar()
        )

        progress_bar.setValue(
            task.progress
        )

        progress_bar.setAlignment(
            Qt.AlignCenter
        )

        # ==========================
        # Заполнение строки
        # ==========================

        self.table.setItem(
            row, 0, file_item
        )

        self.table.setItem(
            row, 1, format_item
        )

        self.table.setItem(
            row, 2, status_item
        )

        self.table.setCellWidget(
            row, 3, progress_bar
        )

        self.table.setItem(
            row, 4, size_item
        )

        self.table.setItem(
            row, 5, output_item
        )

        file_item.setData(
            Qt.UserRole,
            task.id
        )

    # =====================================================
    # ОБНОВЛЕНИЕ СТАТУСА
    # =====================================================

    def update_task_status(
            self,
            task_id: int,
            status: str
    ):
        """
        Обновление статуса задачи.
        """

        if task_id not in self.tasks:
            return

        row = self.tasks[task_id]

        status_item = self.table.item(row, 2)

        if status_item:
            status_item.setText(status)

        self.apply_status_color(row, status)

    # =====================================================
    # ОБНОВЛЕНИЕ ПРОГРЕССА
    # =====================================================

    def update_progress(
            self,
            task_id: int,
            progress: int
    ):
        """
        Обновление прогресса.
        """

        if task_id not in self.tasks:
            return

        row = self.tasks[task_id]

        progress_widget = self.table.cellWidget(row, 3)

        if isinstance(progress_widget, QProgressBar):
            progress_widget.setValue(progress)

    # =====================================================
    # ОБНОВЛЕНИЕ ВЫХОДНОГО ФАЙЛА
    # =====================================================

    def update_output_file(
            self,
            task_id: int,
            output_path: str
    ):
        """
        Обновление пути результата.
        """

        if task_id not in self.tasks:
            return

        row = self.tasks[task_id]

        item = self.table.item(row, 5)

        if item:
            item.setText(output_path)

    # =====================================================
    # ПОЛУЧЕНИЕ ВЫБРАННОЙ ЗАДАЧИ
    # =====================================================

    def get_selected_task_id(self):
        """
        Возвращает ID выбранной задачи.
        """

        row = self.table.currentRow()

        if row == -1:
            return None

        file_item = self.table.item(row, 0)

        if file_item:
            return file_item.data(Qt.UserRole)

        return None

    # =====================================================
    # УДАЛЕНИЕ ЗАДАЧИ
    # =====================================================

    def remove_task(self, task_id: int):
        """
        Удаление задачи.
        """

        if task_id not in self.tasks:
            return

        row = self.tasks[task_id]

        self.table.removeRow(row)

        del self.tasks[task_id]

        self.rebuild_indexes()

    # =====================================================
    # ОЧИСТКА
    # =====================================================

    def clear_tasks(self):
        """
        Полная очистка таблицы.
        """

        self.table.setRowCount(0)
        self.tasks.clear()

    # =====================================================
    # ПЕРЕСТРОЕНИЕ ИНДЕКСОВ
    # =====================================================

    def rebuild_indexes(self):
        """
        Пересоздание индексов строк.
        """

        new_mapping = {}

        for row in range(self.table.rowCount()):

            item = self.table.item(row, 0)

            if item:
                task_id = item.data(Qt.UserRole)

                new_mapping[task_id] = row

        self.tasks = new_mapping

    # =====================================================
    # ЦВЕТ СТАТУСОВ
    # =====================================================

    def apply_status_color(
            self,
            row: int,
            status: str
    ):
        """
        Цветовое оформление статуса.
        """

        colors = {
            "pending": "#E0E0E0",
            "waiting": "#E0E0E0",
            "running": "#FFF59D",
            "completed": "#A5D6A7",
            "failed": "#EF9A9A",
            "cancelled": "#BDBDBD"
        }

        color = colors.get(status, "#FFFFFF")

        for col in range(self.table.columnCount()):

            item = self.table.item(row, col)

            if item:
                item.setBackground(color)

    # =====================================================
    # КОНТЕКСТНОЕ МЕНЮ
    # =====================================================

    def show_context_menu(self, position):
        """
        Контекстное меню таблицы.
        """

        row = self.table.rowAt(position.y())

        if row < 0:
            return

        menu = QMenu()

        remove_action = QAction(
            "Удалить задачу",
            self
        )

        remove_action.triggered.connect(
            self.remove_selected_task
        )

        menu.addAction(remove_action)

        menu.exec(
            self.table.viewport().mapToGlobal(position)
        )

    def remove_selected_task(self):
        """
        Удаление выбранной задачи.
        """

        task_id = self.get_selected_task_id()

        if task_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранную задачу?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            self.task_removed.emit(task_id)

            self.remove_task(task_id)

    # =====================================================
    # УТИЛИТЫ
    # =====================================================

    @staticmethod
    def format_size(size_bytes):
        """
        Красивое отображение размера файла.
        """

        if size_bytes is None:
            return "-"

        mb = size_bytes / (1024 * 1024)

        if mb < 1024:
            return f"{mb:.2f} MB"

        gb = mb / 1024

        return f"{gb:.2f} GB"