import os

from PySide6.QtWidgets import QFileDialog


class FilePicker:
    """
    Утилита выбора файлов и директорий.
    """

    VIDEO_FILTER = (
        "Видео файлы (*.mp4 *.avi *.mkv *.mov *.wmv "
        "*.flv *.webm *.mpeg *.mpg *.m4v *.ts);;"
        "Все файлы (*.*)"
    )

    SUPPORTED_EXTENSIONS = {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".mpeg",
        ".mpg",
        ".m4v",
        ".ts"
    }

    # =====================================================
    # ВЫБОР НЕСКОЛЬКИХ ФАЙЛОВ
    # =====================================================

    @staticmethod
    def pick_video_files(parent=None):
        """
        Выбор нескольких видеофайлов.
        """

        files, _ = QFileDialog.getOpenFileNames(
            parent,
            "Выберите видеофайлы",
            "",
            FilePicker.VIDEO_FILTER
        )

        return files

    # =====================================================
    # ВЫБОР ОДНОГО ФАЙЛА
    # =====================================================

    @staticmethod
    def pick_single_video(parent=None):
        """
        Выбор одного видеофайла.
        """

        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Выберите видеофайл",
            "",
            FilePicker.VIDEO_FILTER
        )

        return file_path

    # =====================================================
    # ВЫБОР ПАПКИ
    # =====================================================

    @staticmethod
    def pick_output_directory(parent=None):
        """
        Выбор папки сохранения.
        """

        directory = QFileDialog.getExistingDirectory(
            parent,
            "Выберите папку сохранения"
        )

        return directory

    # =====================================================
    # ПРОВЕРКА ФОРМАТА
    # =====================================================

    @staticmethod
    def is_supported_video(file_path):
        """
        Проверка поддержки видеоформата.
        """

        _, ext = os.path.splitext(file_path)

        return (
            ext.lower()
            in FilePicker.SUPPORTED_EXTENSIONS
        )

    # =====================================================
    # ФИЛЬТРАЦИЯ СПИСКА
    # =====================================================

    @staticmethod
    def filter_supported_files(files):
        """
        Удаляет неподдерживаемые файлы.
        """

        return [
            file
            for file in files
            if FilePicker.is_supported_video(file)
        ]

    # =====================================================
    # СОЗДАНИЕ ВЫХОДНОГО ИМЕНИ
    # =====================================================

    @staticmethod
    def generate_output_path(
            input_file: str,
            output_folder: str,
            output_format: str
    ):
        """
        Генерация имени выходного файла.
        """

        file_name = os.path.basename(input_file)

        name_without_ext = os.path.splitext(
            file_name
        )[0]

        output_name = (
            f"{name_without_ext}"
            f"_converted."
            f"{output_format.lower()}"
        )

        return os.path.join(
            output_folder,
            output_name
        )

    # =====================================================
    # ПОЛУЧЕНИЕ ИМЕНИ ФАЙЛА
    # =====================================================

    @staticmethod
    def get_file_name(file_path):
        """
        Получить имя файла.
        """

        return os.path.basename(file_path)

    # =====================================================
    # ПОЛУЧЕНИЕ РАЗМЕРА
    # =====================================================

    @staticmethod
    def get_file_size(file_path):
        """
        Получить размер файла.
        """

        try:
            return os.path.getsize(file_path)

        except Exception:
            return 0

    # =====================================================
    # ПРОВЕРКА СУЩЕСТВОВАНИЯ
    # =====================================================

    @staticmethod
    def exists(file_path):
        """
        Проверка существования файла.
        """

        return os.path.exists(file_path)

    # =====================================================
    # ПРОВЕРКА ПАПКИ
    # =====================================================

    @staticmethod
    def ensure_directory(path):
        """
        Создание папки при отсутствии.
        """

        if not os.path.exists(path):
            os.makedirs(path)

    # =====================================================
    # ДОСТУПНЫЕ ФОРМАТЫ
    # =====================================================

    @staticmethod
    def get_output_formats():
        """
        Список поддерживаемых форматов.
        """

        return [
            "mp4",
            "avi",
            "mkv",
            "mov",
            "webm",
            "flv",
            "wmv",
            "mpeg"
        ]