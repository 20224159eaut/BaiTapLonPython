import os
import shutil
from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFileDialog,
                             QInputDialog, QMessageBox, QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
from pages.base_page import BasePage
from styles import APP_STYLE

class DuePage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)

        title = QLabel("⏰ TÀI LIỆU ĐẾN HẠN")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # Bảng hiển thị các yêu cầu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Người gửi", "Lời nhắn", "Ngày gửi", "File đính kèm", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        """Tải danh sách yêu cầu chưa hoàn thành và hiển thị lên bảng"""
        orders = self.db.get_due_orders(self.user['id'])
        self.table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            # ID (ẩn, dùng để xử lý)
            id_item = QTableWidgetItem(str(order['id']))
            id_item.setData(Qt.ItemDataRole.UserRole, order['id'])
            self.table.setItem(row, 0, id_item)

            # Người gửi
            self.table.setItem(row, 1, QTableWidgetItem(order['from_name']))

            # Lời nhắn
            self.table.setItem(row, 2, QTableWidgetItem(order['message']))

            # Ngày gửi (đã được chuyển múi giờ trong DB)
            self.table.setItem(row, 3, QTableWidgetItem(order['created_at']))

            # File đính kèm
            attachment = order.get('attachment_path')
            if attachment and os.path.exists(attachment):
                btn_download = QPushButton("📥 Tải file")
                btn_download.clicked.connect(lambda checked, path=attachment: self.download_file(path))
                self.table.setCellWidget(row, 4, btn_download)
            else:
                self.table.setItem(row, 4, QTableWidgetItem("Không có"))

            # Nút xử lý yêu cầu (chia sẻ tài liệu)
            btn_process = QPushButton("📤 Chia sẻ")
            btn_process.clicked.connect(lambda checked, oid=order['id']: self.process_order(oid))
            self.table.setCellWidget(row, 5, btn_process)

    def download_file(self, src_path):
        """Tải file đính kèm về máy"""
        save_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", os.path.basename(src_path))
        if save_path:
            try:
                shutil.copy2(src_path, save_path)
                QMessageBox.information(self, "Thành công", "Đã lưu file.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")

    def process_order(self, order_id):
        """Xử lý một yêu cầu: chọn tài liệu của mình và chia sẻ vào phòng ban"""
        # Lấy danh sách tài liệu của user hiện tại
        docs = self.db.get_user_documents(self.user['id'])
        if not docs:
            QMessageBox.information(self, "Thông báo", "Bạn chưa có tài liệu nào để chia sẻ.")
            return

        items = [f"{d['id']}: {d['title']}" for d in docs]
        doc_item, ok = QInputDialog.getItem(self, "Chọn tài liệu", "Tài liệu của bạn:", items, 0, False)
        if not ok or not doc_item:
            return

        doc_id = int(doc_item.split(":")[0])

        # Chọn phòng ban để chia sẻ
        departments = ["Hành chính", "Kinh doanh", "Kỹ thuật", "Nhân sự", "Ban Giám đốc"]
        dept, ok = QInputDialog.getItem(self, "Phòng ban", "Chia sẻ đến phòng ban:", departments, 0, False)
        if not ok or not dept:
            return

        # Thực hiện chia sẻ
        self.db.share_document(doc_id, dept)

        # Đánh dấu yêu cầu đã hoàn thành
        self.db.complete_due_order(order_id)

        # Thông báo cho người gửi yêu cầu (tuỳ chọn)
        # Lấy order để biết người gửi
        # Ở đây không cần vì đã có add_log trong share_document rồi

        QMessageBox.information(self, "Hoàn thành", "Đã chia sẻ tài liệu và hoàn thành yêu cầu.")
        self.load_data()  # Refresh danh sách