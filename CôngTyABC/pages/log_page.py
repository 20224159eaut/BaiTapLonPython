from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTextEdit
from pages.base_page import BasePage
from styles import APP_STYLE

class LogPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("NHẬT KÍ HOẠT ĐỘNG"))
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        self.load_data()

    def load_data(self):
        logs = self.db.get_logs()
        text = ""
        for l in logs:
            text += f"[{l['timestamp']}] {l['full_name']}: {l['action']}\n"
        self.log_display.setText(text)