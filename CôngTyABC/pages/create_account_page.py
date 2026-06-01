from PyQt6.QtWidgets import (
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from pages.base_page import BasePage
from styles import APP_STYLE


class CreateAccountPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QGroupBox("Tạo tài khoản")
        header.setStyleSheet(
            """
            QGroupBox { 
                background-color: rgba(94, 57, 47, 0.18);
                border: 2px solid #D4AF37;
                border-radius: 14px;
                margin-top: 10px;
                padding: 10px;
            }
            QLabel { color: #FFD700; }
            """
        )
        header_layout = QHBoxLayout(header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.setSpacing(12)

        icon_lbl = QLabel("👤")
        icon_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_lbl = QLabel("TẠO TÀI KHOẢN MỚI")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold;")

        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch(1)

        main_layout.addWidget(header)

        # Card form
        card = QGroupBox("Thông tin tài khoản")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(18, 14, 18, 14)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("vd: nguyenan")

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Nhập mật khẩu")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("vd: Nguyễn An")

        self.dept_edit = QLineEdit()
        self.dept_edit.setPlaceholderText("vd: Phòng Kế toán")

        self.pos_edit = QLineEdit()
        self.pos_edit.setPlaceholderText("vd: Chuyên viên")

        self.role_combo = QComboBox()
        self.role_combo.addItems(["1: Nhân viên", "2: Trưởng bộ phận", "3: Cấp cao"])

        form.addRow("Tên đăng nhập:", self.username_edit)
        form.addRow("Mật khẩu:", self.password_edit)
        form.addRow("Họ tên:", self.fullname_edit)
        form.addRow("Phòng ban:", self.dept_edit)
        form.addRow("Chức vụ:", self.pos_edit)
        form.addRow("Phân quyền:", self.role_combo)

        card_layout.addLayout(form)
        main_layout.addWidget(card)

        btn = QPushButton("Tạo tài khoản")
        btn.clicked.connect(self.create_user)
        btn.setSizePolicy(btn.sizePolicy().horizontalPolicy(), btn.sizePolicy().verticalPolicy())
        main_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addStretch(1)

    def create_user(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        fullname = self.fullname_edit.text().strip()
        dept = self.dept_edit.text().strip()
        pos = self.pos_edit.text().strip()
        # Lấy role từ tiền tố '1: ...' / '2: ...'
        role_text = self.role_combo.currentText().split(":", 1)[0].strip()
        role = int(role_text)
        if not username or not password or not fullname:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin.")
            return
        try:
            self.db.create_user(username, password, fullname, dept, pos, role)
            QMessageBox.information(self, "Thành công", f"Đã tạo tài khoản {username}.")
            self.username_edit.clear()
            self.password_edit.clear()
            self.fullname_edit.clear()
            self.dept_edit.clear()
            self.pos_edit.clear()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))
