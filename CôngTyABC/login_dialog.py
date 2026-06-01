from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from styles import APP_STYLE

class LoginDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user = None
        self.setWindowTitle("Đăng nhập - Công ty ABC")
        self.setFixedSize(400, 300)
        self.setStyleSheet(APP_STYLE + """
            QDialog { background-color: #3E2723; border: 3px solid #D4AF37; border-radius: 15px; }
            QLabel { color: #D4AF37; font-size: 14px; }
            QLineEdit { background: #5D4037; color: #FFD700; border: 1px solid #D4AF37; padding: 5px; border-radius: 5px; }
            QPushButton { background: #8D6E63; color: #FFD700; border: 1px solid #FFD700; padding: 8px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #A1887F; }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("ĐẠI VIỆT QUẢN LÝ VĂN BẢN")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
        layout.addWidget(title)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Tên đăng nhập")
        layout.addWidget(QLabel("Tên đăng nhập"))
        layout.addWidget(self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Mật khẩu")
        layout.addWidget(QLabel("Mật khẩu"))
        layout.addWidget(self.password_edit)

        login_btn = QPushButton("Đăng nhập")
        login_btn.clicked.connect(self.check_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def check_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        user = self.db.validate_login(username, password)
        if user:
            self.db.add_log(user['id'], "Đăng nhập thành công")
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def get_user(self):
        return self.user