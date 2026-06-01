import os
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QInputDialog,
                             QMessageBox, QHeaderView, QFileDialog)
from pages.base_page import BasePage
from styles import APP_STYLE

class ApprovePage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("DUYỆT TÀI LIỆU"))
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "Người gửi", "Phòng", "Mô tả", "Ngày", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_approve = QPushButton("Phê duyệt")
        btn_reject = QPushButton("Từ chối")
        btn_open = QPushButton("Mở file")
        btn_layout.addWidget(btn_approve)
        btn_layout.addWidget(btn_reject)
        btn_layout.addWidget(btn_open)
        layout.addLayout(btn_layout)

        btn_approve.clicked.connect(self.approve)
        btn_reject.clicked.connect(self.reject)
        btn_open.clicked.connect(self.open_file)
        self.load_data()

    def load_data(self):
        docs = self.db.get_pending_documents()
        self.table.setRowCount(len(docs))
        for row, doc in enumerate(docs):
            self.table.setItem(row, 0, QTableWidgetItem(str(doc['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(doc['title']))
            self.table.setItem(row, 2, QTableWidgetItem(doc['full_name']))
            self.table.setItem(row, 3, QTableWidgetItem(doc['user_dept']))
            self.table.setItem(row, 4, QTableWidgetItem(doc['description']))
            self.table.setItem(row, 5, QTableWidgetItem(doc['created_at']))
            self.table.setItem(row, 6, QTableWidgetItem(doc['shared_status']))

    def approve(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn một tài liệu để duyệt")
            return
        doc_id = int(self.table.item(row, 0).text())
        self.db.approve_document(doc_id, self.user['id'])
        QMessageBox.information(self, "Thành công", "Tài liệu đã được phê duyệt.")
        self.load_data()

    def reject(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn một tài liệu để từ chối")
            return
        doc_id = int(self.table.item(row, 0).text())
        reasons = [
            "Lý do 1: Không đúng định dạng",
            "Lý do 2: Thiếu thông tin quan trọng",
            "Lý do 3: Không phù hợp phòng ban",
            "Lý do 4: Nội dung nhạy cảm",
            "Lý do 5: Trùng lặp tài liệu"
        ]
        reason, ok = QInputDialog.getItem(self, "Lý do từ chối", "Chọn lý do:", reasons, 0, False)
        if ok and reason:
            self.db.reject_document(doc_id, reason, self.user['id'])
            QMessageBox.information(self, "Đã từ chối", "Tài liệu đã bị từ chối.")
            self.load_data()
    
    def open_file(self):
        """Mở file đính kèm của tài liệu đang chọn"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tài liệu.")
            return
        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if not doc or not doc['file_path']:
            QMessageBox.warning(self, "Lỗi", "Tài liệu không có file đính kèm.")
            return
        filepath = doc['file_path']
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy file:\n{filepath}")
            return
        try:
            import sys
            if sys.platform == 'win32':
                os.startfile(filepath)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.run([opener, filepath])   # Windows
            # Nếu cần hỗ trợ macOS/Linux, thay bằng subprocess như đã hướng dẫn
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở file:\n{str(e)}")