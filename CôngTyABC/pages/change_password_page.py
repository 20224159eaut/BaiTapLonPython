from PyQt6.QtWidgets import (QVBoxLayout, QFormLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from pages.base_page import BasePage
from styles import APP_STYLE

class ChangePasswordPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ĐỔI MẬT KHẨU"))
        form = QFormLayout()
        self.old_pass = QLineEdit()
        self.old_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Mật khẩu cũ:", self.old_pass)
        form.addRow("Mật khẩu mới:", self.new_pass)
        form.addRow("Xác nhận:", self.confirm_pass)
        layout.addLayout(form)

        btn = QPushButton("Đổi mật khẩu")
        btn.clicked.connect(self.change_password)
        layout.addWidget(btn)

    def change_password(self):
        old = self.old_pass.text()
        new = self.new_pass.text()
        confirm = self.confirm_pass.text()
        if new != confirm:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        if old != self.user['password']:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu cũ không đúng.")
            return
        self.db.change_password(self.user['id'], new)
        # Cập nhật lại user trong bộ nhớ (nếu cần)
        self.user = self.db.get_user(self.user['id'])
        QMessageBox.information(self, "Thành công", "Đã đổi mật khẩu.")
        self.old_pass.clear()
        self.new_pass.clear()
        self.confirm_pass.clear()