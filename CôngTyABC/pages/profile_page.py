from PyQt6.QtWidgets import QVBoxLayout, QLabel
from pages.base_page import BasePage
from styles import APP_STYLE

class ProfilePage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("THÔNG TIN CÁ NHÂN"))
        info = (f"Họ tên: {self.user['full_name']}\n"
                f"Phòng ban: {self.user['department']}\n"
                f"Chức vụ: {self.user['position']}\n"
                f"Quyền hạn: {self.user['role']}\n"
                f"Tên đăng nhập: {self.user['username']}")
        lbl = QLabel(info)
        lbl.setStyleSheet("font-size: 14px; color: #FFD700;")
        layout.addWidget(lbl)