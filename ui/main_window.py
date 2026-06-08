from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QFrame,
    QStatusBar,
    QToolBar
)

from core.models import (
    ConversionTask,
    ConversionSettings,
    TaskStatus
)

from core.queue_manager import QueueManager
from core.ffmpeg_utils import FFmpegUtils

from ui.task_table import TaskTable
from ui.settings_dialog import SettingsDialog
from ui.file_picker import FilePicker


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    """

    def __init__(
        self,
        database_manager,
        ffmpeg_available=True
    ):
        super().__init__()

        self.database_manager = database_manager
        self.ffmpeg_available = ffmpeg_available

        self.queue_manager = QueueManager(
            database_manager=self.database_manager
        )

        self.selected_files = []

        self.setup_window()
        self.setup_ui()
        self.setup_toolbar()
        self.setup_statusbar()
        self.connect_signals()

        self.load_saved_tasks()

    # ==========================================================
    # НАСТРОЙКА ОКНА
    # ==========================================================

    def setup_window(self):
        self.setWindowTitle(
            "Video Converter GUI"
        )

        self.resize(1400, 850)

        self.setMinimumSize(
            1100,
            700
        )

    # ==========================================================
    # UI
    # ==========================================================

    def setup_ui(self):
        """
        Создание интерфейса.
        """

        central_widget = QWidget()
        self.setCentralWidget(
            central_widget
        )

        self.main_layout = QVBoxLayout(
            central_widget
        )

        splitter = QSplitter(
            Qt.Horizontal
        )

        splitter.addWidget(
            self.create_left_panel()
        )

        splitter.addWidget(
            self.create_right_panel()
        )

        splitter.setSizes(
            [500, 900]
        )

        self.main_layout.addWidget(
            splitter
        )

    # ==========================================================
    # ЛЕВАЯ ПАНЕЛЬ
    # ==========================================================

    def create_left_panel(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)

        # Заголовок
        title = QLabel(
            "Видеофайлы"
        )

        title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        layout.addWidget(title)

        # Список файлов
        self.file_list = QListWidget()

        layout.addWidget(
            self.file_list
        )

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton(
            "Добавить"
        )

        self.remove_button = QPushButton(
            "Удалить"
        )

        self.clear_button = QPushButton(
            "Очистить"
        )

        buttons_layout.addWidget(
            self.add_button
        )

        buttons_layout.addWidget(
            self.remove_button
        )

        buttons_layout.addWidget(
            self.clear_button
        )

        layout.addLayout(
            buttons_layout
        )

        return widget

    # ==========================================================
    # ПРАВАЯ ПАНЕЛЬ
    # ==========================================================

    def create_right_panel(self):
        widget = QWidget()

        layout = QVBoxLayout(widget)

        # --------------------------------
        # Параметры конвертации
        # --------------------------------

        settings_frame = QFrame()

        settings_frame.setFrameShape(
            QFrame.StyledPanel
        )

        settings_layout = QVBoxLayout(
            settings_frame
        )

        settings_title = QLabel(
            "Параметры конвертации"
        )

        settings_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        settings_layout.addWidget(
            settings_title
        )

        # Формат
        format_layout = QHBoxLayout()

        format_label = QLabel(
            "Формат:"
        )

        self.format_combo = QComboBox()

        self.format_combo.addItems(
            FFmpegUtils.SUPPORTED_FORMATS
        )

        format_layout.addWidget(
            format_label
        )

        format_layout.addWidget(
            self.format_combo
        )

        settings_layout.addLayout(
            format_layout
        )

        # Кодек
        codec_layout = QHBoxLayout()

        codec_label = QLabel(
            "Кодек:"
        )

        self.codec_combo = QComboBox()

        self.codec_combo.addItems(
            [
                "libx264",
                "libx265",
                "mpeg4"
            ]
        )

        codec_layout.addWidget(
            codec_label
        )

        codec_layout.addWidget(
            self.codec_combo
        )

        settings_layout.addLayout(
            codec_layout
        )

        # Разрешение
        resolution_layout = QHBoxLayout()

        resolution_label = QLabel(
            "Разрешение:"
        )

        self.resolution_combo = (
            QComboBox()
        )

        self.resolution_combo.addItems(
            [
                "original",
                "1920x1080",
                "1280x720",
                "854x480"
            ]
        )

        resolution_layout.addWidget(
            resolution_label
        )

        resolution_layout.addWidget(
            self.resolution_combo
        )

        settings_layout.addLayout(
            resolution_layout
        )

        layout.addWidget(
            settings_frame
        )

        # --------------------------------
        # Таблица задач
        # --------------------------------

        queue_title = QLabel(
            "Очередь задач"
        )

        queue_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            queue_title
        )

        self.task_table = TaskTable()

        layout.addWidget(
            self.task_table
        )

        # --------------------------------
        # Кнопки управления
        # --------------------------------

        controls_layout = QHBoxLayout()

        self.start_button = QPushButton(
            "Старт"
        )

        self.stop_button = QPushButton(
            "Стоп"
        )

        self.settings_button = (
            QPushButton(
                "Настройки"
            )
        )

        controls_layout.addWidget(
            self.start_button
        )

        controls_layout.addWidget(
            self.stop_button
        )

        controls_layout.addWidget(
            self.settings_button
        )

        layout.addLayout(
            controls_layout
        )

        # --------------------------------
        # Прогресс
        # --------------------------------

        progress_label = QLabel(
            "Прогресс"
        )

        layout.addWidget(
            progress_label
        )

        self.progress_bar = (
            QProgressBar()
        )

        self.progress_bar.setValue(
            0
        )

        layout.addWidget(
            self.progress_bar
        )

        return widget

    # ==========================================================
    # TOOLBAR
    # ==========================================================

    def setup_toolbar(self):
        toolbar = QToolBar()

        self.addToolBar(toolbar)

        add_action = QAction(
            "Добавить",
            self
        )

        start_action = QAction(
            "Старт",
            self
        )

        settings_action = QAction(
            "Настройки",
            self
        )

        toolbar.addAction(
            add_action
        )

        toolbar.addAction(
            start_action
        )

        toolbar.addAction(
            settings_action
        )

        add_action.triggered.connect(
            self.add_files
        )

        start_action.triggered.connect(
            self.start_conversion
        )

        settings_action.triggered.connect(
            self.open_settings
        )

    # ==========================================================
    # STATUS BAR
    # ==========================================================

    def setup_statusbar(self):
        self.status_bar = QStatusBar()

        self.setStatusBar(
            self.status_bar
        )

        if self.ffmpeg_available:
            self.status_bar.showMessage(
                "FFmpeg подключен"
            )
        else:
            self.status_bar.showMessage(
                "FFmpeg не найден"
            )

    # ==========================================================
    # SIGNALS
    # ==========================================================

    def connect_signals(self):
        self.add_button.clicked.connect(
            self.add_files
        )

        self.remove_button.clicked.connect(
            self.remove_selected_file
        )

        self.clear_button.clicked.connect(
            self.clear_files
        )

        self.start_button.clicked.connect(
            self.start_conversion
        )

        self.stop_button.clicked.connect(
            self.stop_conversion
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

    # ==========================================================
    # FILES
    # ==========================================================

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите видеофайлы",
            "",
            (
                "Видео (*.mp4 *.avi "
                "*.mkv *.mov *.wmv)"
            )
        )

        if not files:
            return

        for file in files:
            self.selected_files.append(
                file
            )

            self.file_list.addItem(
                file
            )

    def remove_selected_file(self):
        row = (
            self.file_list.currentRow()
        )

        if row < 0:
            return

        self.file_list.takeItem(row)

        del self.selected_files[row]

    def clear_files(self):
        self.file_list.clear()
        self.selected_files.clear()

    # ==========================================================
    # CONVERSION
    # ==========================================================

    def start_conversion(self):
        if not self.ffmpeg_available:
            QMessageBox.warning(
                self,
                "Ошибка",
                "FFmpeg не найден."
            )
            return

        if not self.selected_files:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Добавьте видео."
            )
            return

        output_format = (
            self.format_combo
            .currentText()
        )

        codec = (
            self.codec_combo
            .currentText()
        )

        resolution = (
            self.resolution_combo
            .currentText()
        )

        for file_path in (
            self.selected_files
        ):
            output_path = str(
                Path(file_path)
                .with_suffix(
                    f".{output_format}"
                )
            )

            settings = (
                ConversionSettings(
                    output_format=
                    output_format,

                    video_codec=
                    codec,

                    resolution=
                    resolution
                )
            )

            task = ConversionTask(
                input_file=file_path,
                output_file=output_path,
                settings=settings,
                status=TaskStatus.PENDING
            )

            self.queue_manager.add_task(
                task
            )

            self.task_table.add_task(
                task
            )

        self.queue_manager.start_queue()

        QMessageBox.information(
            self,
            "Готово",
            "Конвертация запущена."
        )

    def stop_conversion(self):
        self.queue_manager.stop_queue()

        QMessageBox.information(
            self,
            "Остановлено",
            "Очередь остановлена."
        )

    # ==========================================================
    # SETTINGS
    # ==========================================================

    def open_settings(self):
        dialog = SettingsDialog(
            self.database_manager,
            self
        )

        dialog.exec()

    # ==========================================================
    # DATABASE
    # ==========================================================

    def load_saved_tasks(self):
        tasks = (
            self.database_manager
            .get_all_tasks()
        )

        for task in tasks:
            self.task_table.load_task(
                task
            )