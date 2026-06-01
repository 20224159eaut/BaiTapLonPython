from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QTextEdit)
from pages.base_page import BasePage
from styles import APP_STYLE

class NotificationsPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("THÔNG BÁO"))
        self.notif_display = QTextEdit()
        self.notif_display.setReadOnly(True)
        layout.addWidget(self.notif_display)
        btn_mark = QPushButton("Đánh dấu đã đọc")
        btn_mark.clicked.connect(self.mark_read)
        layout.addWidget(btn_mark)
        self.load_data()

    def load_data(self):
        notifs = self.db.get_notifications(self.user['id'])
        text = ""
        for n in notifs:
            read = "✓" if n['is_read'] else "✉"
            text += f"[{read}] {n['created_at']} - {n['message']}\n"
        self.notif_display.setText(text)

    def mark_read(self):
        self.db.mark_notifications_read(self.user['id'])
        self.load_data()