import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from core.database_manager import DatabaseManager


APP_NAME = "Video Converter GUI"
APP_VERSION = "1.0"


def create_required_folders():
    """
    Создание необходимых папок проекта.
    """

    folders = [
        "database",
        "logs",
        "assets",
        "assets/icons",
        "assets/themes"
    ]

    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)


def initialize_database():
    """
    Инициализация базы данных.
    """

    try:
        db = DatabaseManager()
        db.initialize_database()
        return db

    except Exception as error:
        QMessageBox.critical(
            None,
            "Ошибка базы данных",
            f"Не удалось инициализировать БД:\n{error}"
        )
        sys.exit(1)


def check_ffmpeg():
    """
    Проверка наличия FFmpeg в системе.
    """

    import subprocess

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


def show_ffmpeg_warning():
    """
    Предупреждение об отсутствии FFmpeg.
    """

    message = QMessageBox()
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle("FFmpeg не найден")

    message.setText(
        "FFmpeg не найден в системе.\n\n"
        "Конвертация видео будет недоступна.\n\n"
        "Установите FFmpeg и добавьте его в PATH."
    )

    message.exec()


def configure_application(app):
    """
    Глобальная настройка приложения.
    """

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("DiplomaProject")

    app.setStyle("Fusion")

    icon_path = "assets/icons/app_icon.ico"

    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))


def main():
    """
    Точка входа в программу.
    """

    create_required_folders()

    app = QApplication(sys.argv)

    configure_application(app)

    db_manager = initialize_database()

    ffmpeg_exists = check_ffmpeg()

    if not ffmpeg_exists:
        show_ffmpeg_warning()

    try:
        window = MainWindow(
            database_manager=db_manager,
            ffmpeg_available=ffmpeg_exists
        )

        window.show()

        sys.exit(app.exec())

    except Exception as error:
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Произошла ошибка запуска:\n{error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()