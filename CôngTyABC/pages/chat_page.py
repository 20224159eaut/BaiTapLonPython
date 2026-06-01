from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
                             QComboBox, QPushButton)
from PyQt6.QtCore import QTimer
from pages.base_page import BasePage
from styles import APP_STYLE

class ChatPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("TRÒ CHUYỆN"))

        # Chọn người nhận
        receiver_layout = QHBoxLayout()
        receiver_layout.addWidget(QLabel("Gửi đến:"))
        self.receiver_combo = QComboBox()
        self.receiver_combo.addItem("Tất cả", None)
        receiver_layout.addWidget(self.receiver_combo)
        layout.addLayout(receiver_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        send_btn = QPushButton("Gửi")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        # Tự động cập nhật chat
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(3000)
        self.load_data()
        self.load_users()

    def load_data(self):
        msgs = self.db.get_messages(self.user['id'])
        text = ""
        for m in msgs:
            text += f"[{m['timestamp']}] {m['sender_name']}: {m['content']}\n"
        self.chat_display.setText(text)

    def load_users(self):
        # Nạp danh sách người dùng để chọn người nhận
        users = self.db.get_all_users()
        for u in users:
            if u['id'] != self.user['id']:
                self.receiver_combo.addItem(u['full_name'], u['id'])

    def send_message(self):
        content = self.chat_input.toPlainText().strip()
        if not content:
            return
        receiver_id = self.receiver_combo.currentData()
        self.db.send_message(self.user['id'], content, receiver_id)
        self.chat_input.clear()
        self.load_data()