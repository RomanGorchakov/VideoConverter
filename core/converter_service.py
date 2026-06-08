import subprocess
from typing import Optional

from PySide6.QtCore import (
    QObject,
    Signal,
    QThread
)

from core.models import (
    ConversionTask,
    TaskStatus
)

from core.ffmpeg_utils import (
    FFmpegUtils
)


class ConversionWorker(QObject):
    """
    Worker конвертации.

    Выполняет:
    - запуск FFmpeg;
    - отслеживание прогресса;
    - обработку ошибок;
    - уведомление GUI.
    """

    progress_changed = Signal(int)
    conversion_finished = Signal()
    conversion_failed = Signal(str)

    def __init__(
        self,
        task: ConversionTask
    ):
        super().__init__()

        self.task = task
        self.process = None
        self._cancelled = False

    def run(self):
        """
        Запуск процесса конвертации.
        """

        try:
            self.task.status = (
                TaskStatus.IN_PROGRESS
            )

            duration = (
                FFmpegUtils.get_video_duration(
                    self.task.input_file
                )
            )

            command = (
                FFmpegUtils
                .build_ffmpeg_command(
                    self.task
                )
            )

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )

            while True:

                if self._cancelled:
                    self.cancel()
                    return

                line = (
                    self.process.stdout.readline()
                )

                if not line:
                    break

                progress = (
                    FFmpegUtils
                    .parse_ffmpeg_progress(
                        line,
                        duration
                    )
                )

                if progress >= 0:
                    self.task.progress = (
                        progress
                    )

                    self.progress_changed.emit(
                        progress
                    )

            self.process.wait()

            if self.process.returncode == 0:
                self.task.progress = 100

                self.task.status = (
                    TaskStatus.COMPLETED
                )

                self.progress_changed.emit(
                    100
                )

                self.conversion_finished.emit()

            else:
                error_text = (
                    self.process.stderr.read()
                )

                self.task.status = (
                    TaskStatus.FAILED
                )

                self.conversion_failed.emit(
                    error_text
                )

        except Exception as error:

            self.task.status = (
                TaskStatus.FAILED
            )

            self.conversion_failed.emit(
                str(error)
            )

    def cancel(self):
        """
        Отмена конвертации.
        """

        self._cancelled = True

        try:
            if self.process:
                FFmpegUtils.cancel_process(
                    self.process
                )

            self.task.status = (
                TaskStatus.CANCELLED
            )

        except Exception:
            pass


class ConverterService(QObject):
    """
    Сервис конвертации.

    Управляет:
    - запуском задач;
    - worker потоками;
    - отменой задач;
    - отправкой событий в GUI.
    """

    task_started = Signal(object)
    task_progress = Signal(object, int)
    task_finished = Signal(object)
    task_failed = Signal(object, str)

    def __init__(self):
        super().__init__()

        self.thread: Optional[
            QThread
        ] = None

        self.worker: Optional[
            ConversionWorker
        ] = None

        self.current_task: Optional[
            ConversionTask
        ] = None

    def start_conversion(
        self,
        task: ConversionTask
    ):
        """
        Запуск задачи конвертации.
        """

        if (
            self.thread
            and self.thread.isRunning()
        ):
            raise RuntimeError(
                "Конвертация уже выполняется."
            )

        self.current_task = task

        self.thread = QThread()

        self.worker = (
            ConversionWorker(task)
        )

        self.worker.moveToThread(
            self.thread
        )

        # ====================
        # SIGNALS
        # ====================

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.progress_changed.connect(
            lambda progress:
            self.task_progress.emit(
                task,
                progress
            )
        )

        self.worker.conversion_finished.connect(
            lambda:
            self._on_finished(task)
        )

        self.worker.conversion_failed.connect(
            lambda error:
            self._on_failed(
                task,
                error
            )
        )

        self.task_started.emit(task)

        self.thread.start()

    def cancel_current_task(self):
        """
        Отмена текущей задачи.
        """

        if self.worker:
            self.worker.cancel()

    def is_busy(self) -> bool:
        """
        Проверка активности.
        """

        return (
            self.thread is not None
            and
            self.thread.isRunning()
        )

    def _on_finished(
        self,
        task: ConversionTask
    ):
        """
        Успешное завершение.
        """

        self.task_finished.emit(
            task
        )

        self._cleanup()

    def _on_failed(
        self,
        task: ConversionTask,
        error_message: str
    ):
        """
        Ошибка конвертации.
        """

        self.task_failed.emit(
            task,
            error_message
        )

        self._cleanup()

    def _cleanup(self):
        """
        Очистка ресурсов.
        """

        try:
            if self.thread:
                self.thread.quit()
                self.thread.wait()

            self.worker = None
            self.thread = None
            self.current_task = None

        except Exception:
            pass