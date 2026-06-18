from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Optional


class TaskStatus(Enum):
    """
    Статусы задачи конвертации.
    """

    PENDING = "pending"
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ConversionSettings:
    """
    Настройки конвертации видео.
    """

    output_format: str = "mp4"

    video_codec: str = "libx264"
    audio_codec: str = "aac"

    bitrate: str = "5000k"

    resolution: str = "original"

    fps: Optional[int] = None

    preset: str = "medium"

    overwrite: bool = True


@dataclass
class ConversionTask:
    """
    Модель задачи конвертации.
    """

    input_file: str
    output_file: str

    settings: ConversionSettings

    id: Optional[int] = None

    status: TaskStatus = TaskStatus.PENDING

    progress: int = 0

    created_at: datetime = field(
        default_factory=datetime.now
    )

    finished_at: Optional[datetime] = None

    error_message: Optional[str] = None

    process_id: Optional[int] = None

    # =====================================================
    # ИНФОРМАЦИЯ О ФАЙЛЕ
    # =====================================================

    @property
    def input_filename(self) -> str:
        """
        Имя входного файла.
        """

        return Path(self.input_file).name

    @property
    def output_filename(self) -> str:
        """
        Имя выходного файла.
        """

        return Path(self.output_file).name

    @property
    def input_exists(self) -> bool:
        """
        Существует ли входной файл.
        """

        return Path(self.input_file).exists()

    @property
    def input_size_mb(self) -> float:
        """
        Размер входного файла (MB).
        """

        try:
            size_bytes = Path(
                self.input_file
            ).stat().st_size

            return round(
                size_bytes / (1024 * 1024),
                2
            )

        except Exception:
            return 0.0

    @property
    def output_extension(self) -> str:
        """
        Расширение выходного файла.
        """

        return Path(
            self.output_file
        ).suffix

    # =====================================================
    # СОСТОЯНИЕ ЗАДАЧИ
    # =====================================================

    def set_running(self):
        """
        Запуск задачи.
        """

        self.status = TaskStatus.RUNNING

    def set_progress(
        self,
        progress: int
    ):
        """
        Изменение прогресса.
        """

        self.progress = max(
            0,
            min(100, progress)
        )

    def set_completed(self):
        """
        Завершение задачи.
        """

        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.finished_at = datetime.now()

    def set_failed(
        self,
        error_message: str
    ):
        """
        Ошибка задачи.
        """

        self.status = TaskStatus.FAILED
        self.error_message = error_message
        self.finished_at = datetime.now()

    def set_cancelled(self):
        """
        Отмена задачи.
        """

        self.status = TaskStatus.CANCELLED
        self.finished_at = datetime.now()

    # =====================================================
    # ВАЛИДАЦИЯ
    # =====================================================

    def validate(self) -> tuple[bool, str]:
        """
        Проверка корректности задачи.
        """

        if not self.input_file:
            return False, "Не выбран входной файл."

        if not self.output_file:
            return False, "Не указан выходной файл."

        if not self.input_exists:
            return False, (
                "Входной файл не существует."
            )

        if self.input_file == self.output_file:
            return False, (
                "Входной и выходной файл "
                "не могут совпадать."
            )

        supported_formats = [
            "mp4",
            "avi",
            "mkv",
            "mov",
            "wmv",
            "flv",
            "webm"
        ]

        if (
            self.settings.output_format
            not in supported_formats
        ):
            return (
                False,
                "Неподдерживаемый формат."
            )

        return True, ""

    # =====================================================
    # СЕРИАЛИЗАЦИЯ
    # =====================================================

    def to_dict(self) -> dict:
        """
        Преобразование в словарь.
        """

        return {
            "id": self.id,

            "input_file": self.input_file,
            "output_file": self.output_file,

            "status": self.status.value,

            "progress": self.progress,

            "created_at":
                self.created_at.isoformat(),

            "finished_at":
                self.finished_at.isoformat()
                if self.finished_at
                else None,

            "error_message":
                self.error_message,

            "output_format":
                self.settings.output_format,

            "video_codec":
                self.settings.video_codec,

            "audio_codec":
                self.settings.audio_codec,

            "bitrate":
                self.settings.bitrate,

            "resolution":
                self.settings.resolution,

            "fps":
                self.settings.fps,

            "preset":
                self.settings.preset
        }

    @classmethod
    def from_dict(
        cls,
        data: dict
    ) -> "ConversionTask":
        """
        Создание объекта из словаря.
        """

        settings = ConversionSettings(
            output_format=data.get(
                "output_format",
                "mp4"
            ),

            video_codec=data.get(
                "video_codec",
                "libx264"
            ),

            audio_codec=data.get(
                "audio_codec",
                "aac"
            ),

            bitrate=data.get(
                "bitrate",
                "5000k"
            ),

            resolution=data.get(
                "resolution",
                "original"
            ),

            fps=data.get("fps"),

            preset=data.get(
                "preset",
                "medium"
            )
        )

        task = cls(
            id=data.get("id"),

            input_file=data[
                "input_file"
            ],

            output_file=data[
                "output_file"
            ],

            settings=settings
        )

        status = data.get(
            "status",
            "pending"
        )

        task.status = TaskStatus(status)

        task.progress = data.get(
            "progress",
            0
        )

        task.error_message = data.get(
            "error_message"
        )

        return task