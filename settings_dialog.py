import os

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QMessageBox,
    QDialogButtonBox
)


class SettingsDialog(QDialog):
    """
    Диалог настроек приложения.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QSettings(
            "VideoConverterGUI",
            "Settings"
        )

        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.setup_ui()
        self.load_settings()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # ==================================================
        # ПАПКА СОХРАНЕНИЯ
        # ==================================================

        folder_layout = QHBoxLayout()

        self.output_folder_edit = QLineEdit()

        self.folder_button = QPushButton("Обзор")

        self.folder_button.clicked.connect(
            self.choose_output_folder
        )

        folder_layout.addWidget(
            self.output_folder_edit
        )

        folder_layout.addWidget(
            self.folder_button
        )

        form_layout.addRow(
            "Папка сохранения:",
            folder_layout
        )

        # ==================================================
        # FFMPEG PATH
        # ==================================================

        ffmpeg_layout = QHBoxLayout()

        self.ffmpeg_path_edit = QLineEdit()

        self.ffmpeg_button = QPushButton(
            "Обзор"
        )

        self.ffmpeg_button.clicked.connect(
            self.choose_ffmpeg
        )

        ffmpeg_layout.addWidget(
            self.ffmpeg_path_edit
        )

        ffmpeg_layout.addWidget(
            self.ffmpeg_button
        )

        form_layout.addRow(
            "Путь к FFmpeg:",
            ffmpeg_layout
        )

        # ==================================================
        # ЧИСЛО ПОТОКОВ
        # ==================================================

        self.thread_spinbox = QSpinBox()

        self.thread_spinbox.setMinimum(1)
        self.thread_spinbox.setMaximum(16)
        self.thread_spinbox.setValue(2)

        form_layout.addRow(
            "Количество потоков:",
            self.thread_spinbox
        )

        # ==================================================
        # ТЕМА
        # ==================================================

        self.theme_combo = QComboBox()

        self.theme_combo.addItems([
            "Светлая",
            "Тёмная"
        ])

        form_layout.addRow(
            "Тема интерфейса:",
            self.theme_combo
        )

        # ==================================================
        # АВТОСТАРТ ОЧЕРЕДИ
        # ==================================================

        self.auto_start_checkbox = (
            QCheckBox(
                "Автоматически запускать очередь"
            )
        )

        form_layout.addRow(
            "",
            self.auto_start_checkbox
        )

        # ==================================================
        # АВТОСОХРАНЕНИЕ
        # ==================================================

        self.auto_save_checkbox = (
            QCheckBox(
                "Автоматически сохранять состояние"
            )
        )

        form_layout.addRow(
            "",
            self.auto_save_checkbox
        )

        main_layout.addLayout(form_layout)

        # ==================================================
        # КНОПКИ
        # ==================================================

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        self.buttons.accepted.connect(
            self.save_settings
        )

        self.buttons.rejected.connect(
            self.reject
        )

        main_layout.addWidget(self.buttons)

    # =====================================================
    # ВЫБОР ПАПКИ
    # =====================================================

    def choose_output_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку сохранения"
        )

        if folder:
            self.output_folder_edit.setText(
                folder
            )

    # =====================================================
    # ВЫБОР FFMPEG
    # =====================================================

    def choose_ffmpeg(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите ffmpeg executable"
        )

        if file_path:
            self.ffmpeg_path_edit.setText(
                file_path
            )

    # =====================================================
    # СОХРАНЕНИЕ
    # =====================================================

    def save_settings(self):

        output_folder = (
            self.output_folder_edit.text()
            .strip()
        )

        ffmpeg_path = (
            self.ffmpeg_path_edit.text()
            .strip()
        )

        if output_folder:

            if not os.path.exists(
                    output_folder
            ):
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Папка сохранения "
                    "не существует."
                )
                return

        if ffmpeg_path:

            if not os.path.exists(
                    ffmpeg_path
            ):
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Файл FFmpeg "
                    "не найден."
                )
                return

        self.settings.setValue(
            "output_folder",
            output_folder
        )

        self.settings.setValue(
            "ffmpeg_path",
            ffmpeg_path
        )

        self.settings.setValue(
            "threads",
            self.thread_spinbox.value()
        )

        self.settings.setValue(
            "theme",
            self.theme_combo.currentText()
        )

        self.settings.setValue(
            "auto_start",
            self.auto_start_checkbox.isChecked()
        )

        self.settings.setValue(
            "auto_save",
            self.auto_save_checkbox.isChecked()
        )

        QMessageBox.information(
            self,
            "Успешно",
            "Настройки сохранены."
        )

        self.accept()

    # =====================================================
    # ЗАГРУЗКА
    # =====================================================

    def load_settings(self):

        self.output_folder_edit.setText(
            self.settings.value(
                "output_folder",
                ""
            )
        )

        self.ffmpeg_path_edit.setText(
            self.settings.value(
                "ffmpeg_path",
                ""
            )
        )

        self.thread_spinbox.setValue(
            int(
                self.settings.value(
                    "threads",
                    2
                )
            )
        )

        theme = self.settings.value(
            "theme",
            "Светлая"
        )

        index = self.theme_combo.findText(
            theme
        )

        if index >= 0:
            self.theme_combo.setCurrentIndex(
                index
            )

        auto_start = (
            self.settings.value(
                "auto_start",
                False,
                bool
            )
        )

        self.auto_start_checkbox.setChecked(
            auto_start
        )

        auto_save = (
            self.settings.value(
                "auto_save",
                True,
                bool
            )
        )

        self.auto_save_checkbox.setChecked(
            auto_save
        )

    # =====================================================
    # GETTERS
    # =====================================================

    def get_output_folder(self):

        return (
            self.output_folder_edit.text()
            .strip()
        )

    def get_ffmpeg_path(self):

        return (
            self.ffmpeg_path_edit.text()
            .strip()
        )

    def get_threads(self):

        return self.thread_spinbox.value()

    def get_theme(self):

        return (
            self.theme_combo.currentText()
        )

    def is_auto_start_enabled(self):

        return (
            self.auto_start_checkbox
            .isChecked()
        )

    def is_auto_save_enabled(self):

        return (
            self.auto_save_checkbox
            .isChecked()
        )