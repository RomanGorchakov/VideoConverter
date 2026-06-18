import json
import subprocess
from pathlib import Path
from typing import Optional

import ffmpeg

from core.models import ConversionTask


class FFmpegUtils:
    """
    Утилиты для работы с FFmpeg.

    Отвечает за:
    - проверку FFmpeg;
    - получение информации о видео;
    - генерацию команды конвертации;
    - вычисление прогресса.
    """

    SUPPORTED_FORMATS = [
        "mp4",
        "avi",
        "mkv",
        "mov",
        "wmv",
        "flv",
        "webm"
    ]

    @staticmethod
    def is_ffmpeg_installed() -> bool:
        """
        Проверка установлен ли FFmpeg.
        """

        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            return True

        except Exception:
            return False

    @staticmethod
    def is_ffprobe_installed() -> bool:
        """
        Проверка ffprobe.
        """

        try:
            subprocess.run(
                ["ffprobe", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            return True

        except Exception:
            return False

    @staticmethod
    def get_video_duration(
        file_path: str
    ) -> float:
        """
        Получение длительности видео в секундах.
        """

        try:
            probe = ffmpeg.probe(file_path)

            duration = float(
                probe["format"]["duration"]
            )

            return duration

        except Exception:
            return 0.0

    @staticmethod
    def get_video_resolution(
        file_path: str
    ) -> Optional[str]:
        """
        Получение разрешения видео.
        """

        try:
            probe = ffmpeg.probe(file_path)

            video_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "video"
                ),
                None
            )

            if not video_stream:
                return None

            width = video_stream.get("width")
            height = video_stream.get("height")

            return f"{width}x{height}"

        except Exception:
            return None

    @staticmethod
    def get_file_size_mb(
        file_path: str
    ) -> float:
        """
        Размер файла в мегабайтах.
        """

        try:
            size = Path(file_path).stat().st_size

            return round(
                size / (1024 * 1024),
                2
            )

        except Exception:
            return 0.0

    @staticmethod
    def build_ffmpeg_command(
        task: ConversionTask
    ) -> list[str]:
        """
        Формирование команды FFmpeg.
        """

        settings = task.settings

        command = [
            "ffmpeg"
        ]

        if settings.overwrite:
            command.append("-y")
        else:
            command.append("-n")

        command.extend([
            "-i",
            task.input_file
        ])

        # ======================
        # Видеокодек
        # ======================

        if settings.video_codec:
            command.extend([
                "-c:v",
                settings.video_codec
            ])

        # ======================
        # Аудиокодек
        # ======================

        if settings.audio_codec:
            command.extend([
                "-c:a",
                settings.audio_codec
            ])

        # ======================
        # Битрейт
        # ======================

        if settings.bitrate:
            command.extend([
                "-b:v",
                settings.bitrate
            ])

        # ======================
        # Разрешение
        # ======================

        if (
            settings.resolution
            and settings.resolution
            != "original"
        ):
            command.extend([
                "-s",
                settings.resolution
            ])

        # ======================
        # FPS
        # ======================

        if settings.fps:
            command.extend([
                "-r",
                str(settings.fps)
            ])

        # ======================
        # Preset
        # ======================

        if settings.preset:
            command.extend([
                "-preset",
                settings.preset
            ])

        # ======================
        # Прогресс
        # ======================

        command.extend([
            "-progress",
            "pipe:1",
            "-nostats"
        ])

        command.append(
            task.output_file
        )

        return command

    @staticmethod
    def parse_ffmpeg_progress(
        line: str,
        duration_seconds: float
    ) -> int:
        """
        Получение прогресса конвертации.
        """

        try:
            if "out_time_ms=" not in line:
                return -1

            out_time_ms = int(
                line.strip().split("=")[1]
            )

            current_seconds = (
                out_time_ms / 1_000_000
            )

            if duration_seconds <= 0:
                return 0

            progress = int(
                (
                    current_seconds
                    / duration_seconds
                ) * 100
            )

            progress = max(
                0,
                min(100, progress)
            )

            return progress

        except Exception:
            return -1

    @staticmethod
    def validate_output_format(
        output_format: str
    ) -> bool:
        """
        Проверка поддерживаемого формата.
        """

        return (
            output_format.lower()
            in FFmpegUtils.SUPPORTED_FORMATS
        )

    @staticmethod
    def generate_output_path(
        input_file: str,
        output_format: str
    ) -> str:
        """
        Автоматическая генерация
        имени выходного файла.
        """

        path = Path(input_file)

        new_name = (
            f"{path.stem}"
            f"_converted."
            f"{output_format}"
        )

        return str(
            path.parent / new_name
        )

    @staticmethod
    def get_video_info(
        file_path: str
    ) -> dict:
        """
        Получение информации о видео.
        """

        try:
            probe = ffmpeg.probe(file_path)

            format_info = probe.get(
                "format",
                {}
            )

            video_stream = next(
                (
                    stream
                    for stream
                    in probe["streams"]
                    if stream.get(
                        "codec_type"
                    ) == "video"
                ),
                {}
            )

            return {
                "duration":
                    float(
                        format_info.get(
                            "duration",
                            0
                        )
                    ),

                "size_mb":
                    FFmpegUtils.get_file_size_mb(
                        file_path
                    ),

                "codec":
                    video_stream.get(
                        "codec_name",
                        "unknown"
                    ),

                "width":
                    video_stream.get(
                        "width",
                        0
                    ),

                "height":
                    video_stream.get(
                        "height",
                        0
                    ),

                "fps":
                    video_stream.get(
                        "avg_frame_rate",
                        "unknown"
                    )
            }

        except Exception:
            return {}

    @staticmethod
    def cancel_process(
        process: subprocess.Popen
    ):
        """
        Безопасная остановка процесса.
        """

        try:
            if process.poll() is None:
                process.kill()

        except Exception:
            pass