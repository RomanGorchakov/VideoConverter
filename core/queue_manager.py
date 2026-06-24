from typing import List

from PySide6.QtCore import QObject, Signal

from core.converter_service import ConverterService
from core.models import (
    ConversionTask,
    TaskStatus
)


class QueueManager(QObject):
    """
    Менеджер очереди задач конвертации.
    """

    task_added = Signal(object)
    task_removed = Signal(object)

    task_started = Signal(object)
    task_progress = Signal(object, int)
    task_finished = Signal(object)
    task_failed = Signal(object, str)

    queue_updated = Signal()
    queue_finished = Signal()

    def __init__(self, database_manager=None):
        super().__init__()

        self.database_manager = database_manager

        self.tasks: List[ConversionTask] = []

        self.current_task = None
        self.converter = None

        self.is_running = False
        self.is_paused = False

    # ==========================
    # TASK MANAGEMENT
    # ==========================

    def add_task(
        self,
        task: ConversionTask
    ):
        """
        Добавление задачи.
        """

        task.status = (
            TaskStatus.PENDING
        )

        self.tasks.append(task)

        if self.database_manager:
            try:
                self.database_manager.add_task(
                    task
                )
            except Exception as e:
                print(
                    f"Ошибка БД: {e}"
                )

        self.task_added.emit(task)
        self.queue_updated.emit()

    def add_tasks(
        self,
        tasks: List[ConversionTask]
    ):
        """
        Массовое добавление.
        """

        for task in tasks:
            self.add_task(task)

    def remove_task(
        self,
        task: ConversionTask
    ):
        """
        Удаление задачи.
        """

        if task in self.tasks:

            if (
                task.status
                ==
                TaskStatus.RUNNING
            ):
                return

            self.tasks.remove(task)

            self.task_removed.emit(
                task
            )

            self.queue_updated.emit()

    def clear_queue(self):
        """
        Очистка очереди.
        """

        removable_tasks = [
            task
            for task in self.tasks
            if task.status !=
            TaskStatus.RUNNING
        ]

        for task in removable_tasks:
            self.tasks.remove(task)

        self.queue_updated.emit()

    # ==========================
    # QUEUE CONTROL
    # ==========================

    def start_queue(self):
        """
        Запуск очереди.
        """

        if self.is_running:
            return

        self.is_running = True
        self.is_paused = False

        self._process_next()

    def pause_queue(self):
        """
        Пауза.
        """

        self.is_paused = True

    def resume_queue(self):
        """
        Продолжение.
        """

        self.is_paused = False

        if (
            self.is_running
            and
            self.current_task is None
        ):
            self._process_next()

    def stop_queue(self):
        """
        Остановка.
        """

        self.is_running = False
        self.is_paused = False

        if self.converter:
            self.converter.cancel_current_task()

        if self.current_task:
            self.current_task.status = (
                TaskStatus.CANCELLED
            )

        self.current_task = None

        self.queue_updated.emit()

    # ==========================
    # INTERNAL
    # ==========================

    def _process_next(self):
        """
        Следующая задача.
        """

        if not self.is_running:
            return

        if self.is_paused:
            return

        pending_task = next(
            (
                task
                for task in self.tasks
                if task.status
                ==
                TaskStatus.PENDING
            ),
            None
        )

        if pending_task is None:

            self.is_running = False
            self.current_task = None

            self.queue_finished.emit()

            return

        self.current_task = (
            pending_task
        )

        pending_task.status = (
            TaskStatus.RUNNING
        )

        self.task_started.emit(
            pending_task
        )

        self.converter = ConverterService()

        self.converter.task_progress.connect(
            lambda task, progress:
            self._on_progress(progress)
        )

        self.converter.task_finished.connect(
            lambda task:
            self._on_finished()
        )

        self.converter.task_failed.connect(
            lambda task, error:
            self._on_error(error)
        )

        self.converter.start_conversion(self.current_task)

    # ==========================
    # CALLBACKS
    # ==========================

    def _on_progress(
        self,
        progress: int
    ):
        """
        Прогресс.
        """

        if not self.current_task:
            return

        self.current_task.progress = (
            progress
        )

        self.task_progress.emit(
            self.current_task,
            progress
        )

        self.queue_updated.emit()

    def _on_finished(self):
        """
        Успешное завершение.
        """

        if not self.current_task:
            return

        self.current_task.status = (
            TaskStatus.COMPLETED
        )

        self.current_task.progress = 100

        if self.database_manager:
            try:
                self.database_manager.update_task_status(
                    self.current_task.id,
                    "completed"
                )
                self.database_manager.update_task_progress(
                    self.current_task.id,
                    100
                )
            except Exception as e:
                print(
                    f"Ошибка БД: {e}"
                )

        self.task_finished.emit(
            self.current_task
        )

        self.current_task = None

        self._process_next()

    def _on_error(
        self,
        error_message: str
    ):
        """
        Ошибка конвертации.
        """

        if not self.current_task:
            return

        self.current_task.status = (
            TaskStatus.FAILED
        )

        self.task_failed.emit(
            self.current_task,
            error_message
        )

        self.current_task = None

        self._process_next()

    # ==========================
    # HELPERS
    # ==========================

    def get_tasks(
        self
    ) -> List[ConversionTask]:
        """
        Список задач.
        """

        return self.tasks

    def has_running_task(
        self
    ) -> bool:
        """
        Есть ли активная задача.
        """

        return (
            self.current_task
            is not None
        )