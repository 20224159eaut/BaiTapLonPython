import os
import shutil
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QComboBox, QFileDialog, QMessageBox, QHeaderView)
from pages.base_page import BasePage
from styles import APP_STYLE

class DepartmentDocsPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("TÀI LIỆU PHÒNG BAN"))
        self.btn_detail = QPushButton("Xem chi tiết")
        layout.addWidget(self.btn_detail)
        self.btn_detail.clicked.connect(self.show_detail)
        search_layout = QHBoxLayout()
        self.dept_search_edit = QLineEdit()
        self.dept_search_edit.setPlaceholderText("Từ khóa...")
        self.dept_type_combo = QComboBox()
        self.dept_type_combo.addItems(["", "PDF", "Word", "Excel", "Khác"])
        self.dept_dept_combo = QComboBox()
        self.dept_dept_combo.addItems(["", "Hành chính", "Kinh doanh", "Kỹ thuật", "Nhân sự", "Ban Giám đốc"])
        btn_search = QPushButton("Tìm")
        search_layout.addWidget(QLabel("Từ khóa:"))
        search_layout.addWidget(self.dept_search_edit)
        search_layout.addWidget(QLabel("Loại:"))
        search_layout.addWidget(self.dept_type_combo)
        search_layout.addWidget(QLabel("Phòng:"))
        search_layout.addWidget(self.dept_dept_combo)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "Mô tả", "Người chia sẻ", "Ngày", "Phòng"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_download = QPushButton("Tải xuống")
        layout.addWidget(btn_download)

        btn_open = QPushButton("Mở file")
        btn_open.clicked.connect(self.open_file)
        layout.addWidget(btn_open)

        btn_search.clicked.connect(self.search)
        btn_download.clicked.connect(self.download_document)
        self.load_data()

    def load_data(self):
        docs = self.db.get_approved_department_docs()
        self.populate_table(docs)

    def populate_table(self, docs):
        self.table.setRowCount(len(docs))
        for row, doc in enumerate(docs):
            self.table.setItem(row, 0, QTableWidgetItem(str(doc['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(doc['title']))
            self.table.setItem(row, 2, QTableWidgetItem(doc['description']))
            self.table.setItem(row, 3, QTableWidgetItem(doc['full_name']))
            self.table.setItem(row, 4, QTableWidgetItem(doc['created_at']))
            self.table.setItem(row, 5, QTableWidgetItem(doc['department']))

    def search(self):
        keyword = self.dept_search_edit.text()
        dtype = self.dept_type_combo.currentText() or None
        dept = self.dept_dept_combo.currentText() or None
        docs = self.db.search_department_docs(keyword, dtype, dept)
        self.populate_table(docs)

    def download_document(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tài liệu.")
            return

        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if not doc or not doc['file_path']:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file đính kèm.")
            return

        src_path = doc['file_path']
        if not os.path.exists(src_path):
            QMessageBox.warning(self, "Lỗi", "File gốc không tồn tại.")
            return

        default_name = os.path.basename(src_path)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu tài liệu về máy",
            default_name,
            "Tất cả file (*.*)"
        )
        if save_path:
            try:
                shutil.copy(src_path, save_path)
                QMessageBox.information(self, "Thành công", f"Đã tải xuống:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{str(e)}")

    def show_detail(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Chọn một tài liệu.")
            return
        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if doc:
            # Lấy tên người chia sẻ từ cột 3
            sharer = self.table.item(row, 3).text()
            detail = (f"Tên: {doc['title']}\n"
                    f"Mô tả: {doc['description']}\n"
                    f"Loại: {doc['file_type']}\n"
                    f"Người chia sẻ: {sharer}\n"
                    f"Thời gian chia sẻ: {doc['created_at']}\n"
                    f"Phòng ban: {doc['department']}")
            QMessageBox.information(self, "Chi tiết tài liệu", detail)

    def open_file(self):
        """Mở file đính kèm bằng ứng dụng mặc định của hệ điều hành"""
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
            os.startfile(filepath)   # Windows
            # Nếu muốn hỗ trợ macOS/Linux thì dùng subprocess như hướng dẫn trước
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở file:\n{str(e)}")