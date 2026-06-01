import os
import shutil
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QComboBox, QTextEdit,
                             QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from pages.base_page import BasePage
from styles import APP_STYLE

class SendDueOrderPage(BasePage):
    """Trang dành cho tài khoản role >=2 gửi yêu cầu chia sẻ tài liệu đến role 1 hoặc 2"""
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        self.selected_file_path = None   # Lưu đường dẫn file tạm thời

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Tiêu đề
        title = QLabel("📨 GỬI YÊU CẦU CHIA SẺ TÀI LIỆU")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Chọn người nhận (role 1 hoặc 2)
        layout.addWidget(QLabel("Chọn người nhận:"))
        self.user_combo = QComboBox()
        layout.addWidget(self.user_combo)

        # Đính kèm file
        layout.addWidget(QLabel("Đính kèm tài liệu (tuỳ chọn):"))
        self.file_label = QLabel("Chưa chọn file")
        self.file_label.setStyleSheet("color: gray; padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.file_label)

        self.btn_choose = QPushButton("📎 Chọn file")
        self.btn_choose.clicked.connect(self.choose_file)
        layout.addWidget(self.btn_choose)

        # Lời nhắn
        layout.addWidget(QLabel("Lời nhắn:"))
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Nhập nội dung yêu cầu...")
        self.message_edit.setMaximumHeight(100)
        layout.addWidget(self.message_edit)

        # Nút gửi
        self.btn_send = QPushButton("📤 Gửi yêu cầu")
        self.btn_send.clicked.connect(self.send_order)
        layout.addWidget(self.btn_send)

        self.load_users()

    def load_users(self):
        """Nạp danh sách người dùng có role = 1 hoặc 2"""
        self.user_combo.clear()
        users = self.db.get_users_by_roles([1, 2])
        if not users:
            self.user_combo.addItem("Không có tài khoản role 1 hoặc 2", None)
        else:
            for u in users:
                display = f"{u['full_name']} (role {u['role']}) - {u.get('department', '')}"
                self.user_combo.addItem(display, u['id'])

    def choose_file(self):
        """Mở hộp thoại chọn file và lưu đường dẫn"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn tài liệu", "", "All Files (*.*)")
        if file_path:
            self.selected_file_path = file_path
            self.file_label.setText(os.path.basename(file_path))

    def send_order(self):
        """Xử lý gửi yêu cầu (có thể kèm file)"""
        to_uid = self.user_combo.currentData()
        if not to_uid:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn người nhận hợp lệ.")
            return

        message = self.message_edit.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập nội dung yêu cầu.")
            return

        # Xử lý file đính kèm
        attachment_path = None
        if self.selected_file_path:
            # Tạo thư mục attachments nếu chưa có
            attach_dir = "attachments"
            if not os.path.exists(attach_dir):
                os.makedirs(attach_dir)

            # Tạo tên file duy nhất (timestamp + tên gốc)
            import time
            unique_name = f"{int(time.time())}_{os.path.basename(self.selected_file_path)}"
            dest = os.path.join(attach_dir, unique_name)

            try:
                shutil.copy2(self.selected_file_path, dest)
                attachment_path = dest
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể sao chép file: {e}")
                return

        # Gửi yêu cầu vào database
        try:
            self.db.add_due_order(
                from_uid=self.user['id'],
                to_uid=to_uid,
                message=message,
                attachment_path=attachment_path
            )
            QMessageBox.information(self, "Thành công", "Đã gửi yêu cầu chia sẻ tài liệu.")
            # Reset form
            self.message_edit.clear()
            self.selected_file_path = None
            self.file_label.setText("Chưa chọn file")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể gửi yêu cầu: {e}")