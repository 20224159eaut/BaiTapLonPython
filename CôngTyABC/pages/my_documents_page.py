import os, shutil
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QLineEdit,
                             QFileDialog, QMessageBox, QDialog, QFormLayout,
                             QTextEdit, QComboBox, QHeaderView)
from pages.base_page import BasePage
from styles import APP_STYLE

class MyDocumentsPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("TÀI LIỆU CỦA TÔI"))

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("Thêm")
        self.btn_edit = QPushButton("Sửa")
        self.btn_del = QPushButton("Xóa")
        self.btn_share = QPushButton("Chia sẻ")
        self.btn_update_shared = QPushButton("Cập nhật tài liệu đã chia sẻ")
        self.btn_view_shared = QPushButton("Xem tài liệu đã chia sẻ")
        self.btn_download = QPushButton("Tải xuống")
        self.btn_detail = QPushButton("Chi tiết")
        self.btn_open = QPushButton("Mở file")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tìm kiếm...")
        self.btn_search = QPushButton("Tìm")

        for btn in [self.btn_add, self.btn_edit, self.btn_del, self.btn_share,
                    self.btn_update_shared, self.btn_view_shared, self.btn_download, self.btn_detail, self.btn_open]:
            toolbar.addWidget(btn)
        toolbar.addStretch()
        toolbar.addWidget(self.search_edit)
        toolbar.addWidget(self.btn_search)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Tên", "Mô tả", "Loại", "Ngày tạo", "Trạng thái"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Kết nối
        self.btn_add.clicked.connect(self.add_document)
        self.btn_edit.clicked.connect(self.edit_document)
        self.btn_del.clicked.connect(self.delete_document)
        self.btn_share.clicked.connect(self.share_document)
        self.btn_update_shared.clicked.connect(self.update_shared_document)
        self.btn_view_shared.clicked.connect(self.view_shared_documents)
        self.btn_download.clicked.connect(self.download_document)
        self.btn_detail.clicked.connect(self.show_detail)
        self.btn_open.clicked.connect(self.open_file)
        self.btn_search.clicked.connect(self.search)
        self.table.cellDoubleClicked.connect(self.show_detail)
        self.load_data()

    def load_data(self):
        docs = self.db.get_user_documents(self.user['id'])  # giờ lấy tất cả
        self.table.setRowCount(len(docs))
        for row, doc in enumerate(docs):
            self.table.setItem(row, 0, QTableWidgetItem(str(doc['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(doc['title']))
            self.table.setItem(row, 2, QTableWidgetItem(doc['description']))
            self.table.setItem(row, 3, QTableWidgetItem(doc['file_type']))
            self.table.setItem(row, 4, QTableWidgetItem(doc['created_at']))
            self.table.setItem(row, 5, QTableWidgetItem(doc['shared_status']))

    def add_document(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm tài liệu")
        layout = QFormLayout(dialog)
        title_edit = QLineEdit()
        desc_edit = QTextEdit()
        file_path_edit = QLineEdit()
        file_path_edit.setReadOnly(True)
        file_type_combo = QComboBox()
        file_type_combo.addItems(["PDF", "Word", "Excel", "Khác"])
        choose_btn = QPushButton("Chọn file")

        def choose_file():
            fname, _ = QFileDialog.getOpenFileName(dialog, "Chọn file")
            if fname:
                basename = os.path.basename(fname)
                dest = os.path.join("uploads", basename)
                shutil.copy(fname, dest)
                file_path_edit.setText(dest)
        choose_btn.clicked.connect(choose_file)

        layout.addRow("Tiêu đề:", title_edit)
        layout.addRow("Mô tả:", desc_edit)
        layout.addRow("File:", file_path_edit)
        layout.addRow("", choose_btn)
        layout.addRow("Loại file:", file_type_combo)

        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)

        ok_btn.clicked.connect(lambda: self.save_new_document(dialog, title_edit.text(),
                                                              desc_edit.toPlainText(),
                                                              file_path_edit.text(),
                                                              file_type_combo.currentText()))
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def save_new_document(self, dialog, title, desc, path, ftype):
        if not title or not path:
            QMessageBox.warning(self, "Lỗi", "Tiêu đề và file không được để trống")
            return
        self.db.add_document(self.user['id'], title, desc, path, ftype)
        self.db.add_log(self.user['id'], f"Thêm tài liệu '{title}'")
        dialog.accept()
        self.load_data()

    def edit_document(self):
        row = self.table.currentRow()
        if row < 0: return
        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if not doc: return
        dialog = QDialog(self)
        dialog.setWindowTitle("Sửa tài liệu")
        layout = QFormLayout(dialog)
        title_edit = QLineEdit(doc['title'])
        desc_edit = QTextEdit()
        desc_edit.setText(doc['description'] or "")
        file_path_edit = QLineEdit(doc['file_path'])
        file_path_edit.setReadOnly(True)
        file_type_combo = QComboBox()
        file_type_combo.addItems(["PDF", "Word", "Excel", "Khác"])
        file_type_combo.setCurrentText(doc['file_type'])
        choose_btn = QPushButton("Chọn file mới")
        def choose_new_file():
            fname, _ = QFileDialog.getOpenFileName(dialog, "Chọn file")
            if fname:
                basename = os.path.basename(fname)
                dest = os.path.join("uploads", basename)
                shutil.copy(fname, dest)
                file_path_edit.setText(dest)
        choose_btn.clicked.connect(choose_new_file)
        layout.addRow("Tiêu đề:", title_edit)
        layout.addRow("Mô tả:", desc_edit)
        layout.addRow("File:", file_path_edit)
        layout.addRow("", choose_btn)
        layout.addRow("Loại:", file_type_combo)
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("Cập nhật")
        cancel_btn = QPushButton("Hủy")
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addRow(btn_box)
        ok_btn.clicked.connect(lambda: self.update_document(dialog, doc_id, title_edit.text(),
                                                            desc_edit.toPlainText(),
                                                            file_path_edit.text(),
                                                            file_type_combo.currentText()))
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def update_document(self, dialog, doc_id, title, desc, path, ftype):
        self.db.update_document(doc_id, title, desc, path, ftype)
        self.db.add_log(self.user['id'], f"Sửa tài liệu ID {doc_id}")
        dialog.accept()
        self.load_data()

    def delete_document(self):
        row = self.table.currentRow()
        if row < 0: return
        doc_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Xác nhận", "Xóa tài liệu này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_document(doc_id)
            self.db.add_log(self.user['id'], f"Xóa tài liệu ID {doc_id}")
            self.load_data()

    def share_document(self):
        row = self.table.currentRow()
        if row < 0: return
        doc_id = int(self.table.item(row, 0).text())
        from PyQt6.QtWidgets import QInputDialog
        dept, ok = QInputDialog.getItem(self, "Chia sẻ", "Chọn phòng ban:",
                                        ["Hành chính", "Kinh doanh", "Kỹ thuật", "Nhân sự", "Ban Giám đốc"], 0, False)
        if ok and dept:
            self.db.share_document(doc_id, dept)
            QMessageBox.information(self, "Thành công", "Tài liệu đã được gửi chờ duyệt.")
            self.load_data()

    def update_shared_document(self):
        docs = self.db.get_shared_documents_by_user(self.user['id'])
        if not docs:
            QMessageBox.information(self, "Thông báo", "Bạn chưa có tài liệu chia sẻ nào.")
            return
        from PyQt6.QtWidgets import QInputDialog
        items = [f"{d['id']}: {d['title']} ({d['shared_status']})" for d in docs]
        item, ok = QInputDialog.getItem(self, "Chọn tài liệu", "Tài liệu đã chia sẻ:", items, 0, False)
        if ok and item:
            doc_id = int(item.split(":")[0])
            doc = self.db.get_document(doc_id)
            dialog = QDialog(self)
            dialog.setWindowTitle("Yêu cầu cập nhật tài liệu chia sẻ")
            layout = QFormLayout(dialog)
            title_edit = QLineEdit(doc['title'])
            desc_edit = QTextEdit()
            desc_edit.setText(doc['description'] or "")
            file_path_edit = QLineEdit(doc['file_path'])
            file_path_edit.setReadOnly(True)
            file_type_combo = QComboBox()
            file_type_combo.addItems(["PDF", "Word", "Excel", "Khác"])
            file_type_combo.setCurrentText(doc['file_type'])
            choose_btn = QPushButton("Chọn file mới")
            def choose_new_file():
                fname, _ = QFileDialog.getOpenFileName(dialog, "Chọn file")
                if fname:
                    dest = os.path.join("uploads", os.path.basename(fname))
                    shutil.copy(fname, dest)
                    file_path_edit.setText(dest)
            choose_btn.clicked.connect(choose_new_file)
            layout.addRow("Tiêu đề:", title_edit)
            layout.addRow("Mô tả:", desc_edit)
            layout.addRow("File:", file_path_edit)
            layout.addRow("", choose_btn)
            layout.addRow("Loại:", file_type_combo)
            btn_box = QHBoxLayout()
            ok_btn = QPushButton("Gửi yêu cầu duyệt")
            cancel_btn = QPushButton("Hủy")
            btn_box.addWidget(ok_btn)
            btn_box.addWidget(cancel_btn)
            layout.addRow(btn_box)
            ok_btn.clicked.connect(lambda: self.request_update_shared(dialog, doc_id, title_edit.text(),
                                                                      desc_edit.toPlainText(),
                                                                      file_path_edit.text(),
                                                                      file_type_combo.currentText()))
            cancel_btn.clicked.connect(dialog.reject)
            dialog.exec()

    def request_update_shared(self, dialog, doc_id, title, desc, path, ftype):
        self.db.request_update_shared_document(doc_id, title, desc, path, ftype)
        self.db.add_log(self.user['id'], f"Yêu cầu cập nhật tài liệu ID {doc_id}")
        dialog.accept()
        self.load_data()

    def view_shared_documents(self):
        docs = self.db.get_shared_documents_by_user(self.user['id'])
        if not docs:
            QMessageBox.information(self, "Thông tin", "Không có tài liệu chia sẻ nào.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Tài liệu đã chia sẻ")
        dialog.resize(700, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["ID", "Tên", "Trạng thái", "Phòng ban", "Ngày"])
        table.setRowCount(len(docs))
        for row, doc in enumerate(docs):
            table.setItem(row, 0, QTableWidgetItem(str(doc['id'])))
            table.setItem(row, 1, QTableWidgetItem(doc['title']))
            table.setItem(row, 2, QTableWidgetItem(doc['shared_status']))
            table.setItem(row, 3, QTableWidgetItem(doc['department']))
            table.setItem(row, 4, QTableWidgetItem(doc['created_at']))
        layout.addWidget(table)
        dialog.exec()

    def download_document(self):
        """Mở hộp thoại chọn nơi lưu và tải file về máy"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tài liệu để tải xuống.")
            return

        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if not doc or not doc['file_path']:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file đính kèm.")
            return

        src_path = doc['file_path']
        if not os.path.exists(src_path):
            QMessageBox.warning(self, "Lỗi", "File gốc không tồn tại trên máy chủ.")
            return

        # Gợi ý tên file mặc định (dựa trên tên gốc)
        default_name = os.path.basename(src_path)
        # Mở hộp thoại Save As
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu tài liệu về máy",
            default_name,  # Tên file mặc định
            "Tất cả file (*.*)"
        )
        if save_path:  # Người dùng đã chọn nơi lưu
            try:
                shutil.copy(src_path, save_path)
                QMessageBox.information(self, "Thành công", f"Đã tải xuống:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file:\n{str(e)}")

    def search(self):
        keyword = self.search_edit.text()
        if not keyword:
            self.load_data()
        else:
            docs = self.db.search_my_documents(self.user['id'], keyword)
            self.table.setRowCount(len(docs))
            for row, doc in enumerate(docs):
                self.table.setItem(row, 0, QTableWidgetItem(str(doc['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(doc['title']))
                self.table.setItem(row, 2, QTableWidgetItem(doc['description']))
                self.table.setItem(row, 3, QTableWidgetItem(doc['file_type']))
                self.table.setItem(row, 4, QTableWidgetItem(doc['created_at']))
                self.table.setItem(row, 5, QTableWidgetItem(doc['shared_status']))

    def show_detail(self, row=None):
        """Hiển thị chi tiết tài liệu được chọn (dùng cho cả nút nhấn và double-click)"""
        # Nếu được gọi từ double-click, row là chỉ số hàng; nếu từ nút thì lấy dòng hiện tại
        if row is None:
            row = self.table.currentRow()
        else:
            # Khi double-click, row được truyền từ tín hiệu cellDoubleClicked(int, int)
            # Nó là chỉ số hàng, ta chỉ cần dùng nó
            pass

        if row < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một tài liệu.")
            return

        doc_id = int(self.table.item(row, 0).text())
        doc = self.db.get_document(doc_id)
        if not doc:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy tài liệu.")
            return

        # Tạo dialog hiển thị thông tin
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chi tiết tài liệu: {doc['title']}")
        dialog.resize(500, 400)
        dialog.setStyleSheet(APP_STYLE)

        layout = QFormLayout(dialog)
        layout.addRow("ID:", QLabel(str(doc['id'])))
        layout.addRow("Tiêu đề:", QLabel(doc['title']))
        layout.addRow("Mô tả:", QLabel(doc['description'] if doc['description'] else "Không có"))
        layout.addRow("Loại file:", QLabel(doc['file_type']))
        layout.addRow("Đường dẫn file:", QLabel(doc['file_path']))
        layout.addRow("Phòng ban:", QLabel(doc['department'] if doc['department'] else "Chưa chia sẻ"))
        layout.addRow("Trạng thái chia sẻ:", QLabel(doc['shared_status']))
        if doc['rejection_reason']:
            layout.addRow("Lý do từ chối:", QLabel(doc['rejection_reason']))
        layout.addRow("Ngày tạo:", QLabel(doc['created_at']))
        layout.addRow("Cập nhật lần cuối:", QLabel(doc['updated_at']))

        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(dialog.accept)
        layout.addRow(btn_close)

        dialog.exec()

    def open_file(self):
        """Mở file đính kèm bằng ứng dụng mặc định của HĐH"""
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
            # Mở file bằng chương trình mặc định
            import sys
            if sys.platform == 'win32':
                os.startfile(filepath)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.run([opener, filepath])   # Trên Windows
            # Trên macOS/Linux, dùng subprocess: subprocess.run(['open' if sys.platform=='darwin' else 'xdg-open', filepath])
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể mở file:\n{str(e)}")