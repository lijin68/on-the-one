"""File dialogs that reopen where you left off (and fall back sensibly if that folder is gone)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QComboBox, QDialog, QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..settings import Settings, nearest_existing_dir


def pick_file(parent, settings: Settings, key: str, title: str, file_filter: str) -> str:
    """Open-file dialog starting in `settings.<key>`; remembers the chosen file's folder."""
    start = nearest_existing_dir(getattr(settings, key, ""))
    path, _ = QFileDialog.getOpenFileName(parent, title, start, file_filter)
    if path:
        remember_dir(settings, key, str(Path(path).parent))
    return path


def pick_dir(parent, settings: Settings, key: str, title: str, start: str = "") -> str:
    """Folder dialog starting in `start` (if given) or `settings.<key>`; remembers the choice."""
    path = QFileDialog.getExistingDirectory(parent, title, nearest_existing_dir(start or getattr(settings, key, "")))
    if path:
        remember_dir(settings, key, path)
    return path


def remember_dir(settings: Settings, key: str, folder: str) -> None:
    if getattr(settings, key, None) != folder:
        setattr(settings, key, folder)
        settings.save()


class SurveyDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setWindowTitle("Welcome to DJ Toolkit")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Follows the guidelines in VOICE.md
        title = QLabel("Help us know who is in the booth.")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Question 1
        layout.addWidget(QLabel("Who are you?"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Hobbyist DJ", "Professional DJ", "Music Producer", "Just exploring"])
        layout.addWidget(self.role_combo)

        # Question 2
        layout.addWidget(QLabel("How did you find us?"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["GitHub", "Reddit / Forum", "Friend / Word of mouth", "Search engine", "Other"])
        layout.addWidget(self.source_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        skip_btn = QPushButton("Skip")
        skip_btn.clicked.connect(self._save_and_close)

        submit_btn = QPushButton("Save answers")
        submit_btn.setDefault(True)
        submit_btn.clicked.connect(self._save_and_close)

        btn_layout.addWidget(skip_btn)
        btn_layout.addWidget(submit_btn)
        layout.addLayout(btn_layout)

    def _save_and_close(self):
        # Record locally for now; no backend API to send this to yet.
        self.settings.has_answered_survey = True
        self.settings.save()
        self.accept()
