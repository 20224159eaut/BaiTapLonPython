from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QWidget, QScrollArea, QSizePolicy)

from PyQt6.QtCore import Qt
from pages.base_page import BasePage
from styles import APP_STYLE

class StatsPage(BasePage):
    def __init__(self, db, user):
        super().__init__(db, user)
        self.setStyleSheet(APP_STYLE)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📊 THỐNG KÊ HỆ THỐNG")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        self.refresh_btn = QPushButton("🔄 Cập nhật dữ liệu")
        self.refresh_btn.clicked.connect(self.load_data)
        main_layout.addWidget(self.refresh_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        self.load_data()
    
    def load_data(self):
        # Xóa nội dung cũ
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Lấy dữ liệu (có in ra console để debug)
        total, approved, pending, rejected, users = self.db.get_document_stats()
        print(f"Stats: total={total}, approved={approved}, pending={pending}, rejected={rejected}, users={users}")

        docs_by_dept = list(self.db.get_docs_by_department())
        docs_by_type = list(self.db.get_docs_by_type())
        users_by_role = list(self.db.get_users_by_role_count())
        pending_orders = self.db.get_pending_due_orders_count()
        unread_notif = self.db.get_unread_notifications_total()
        logs_7days = list(self.db.get_logs_last_7_days())
        top_users = list(self.db.get_top_users_by_documents(5))

        # Debug chi tiết từng nhóm để biết mục nào bị rỗng
        print("DEBUG stats groups sizes:", {
            "docs_by_dept": len(docs_by_dept),
            "docs_by_type": len(docs_by_type),
            "users_by_role": len(users_by_role),
            "pending_orders": pending_orders,
            "unread_notif": unread_notif,
            "logs_7days": len(logs_7days),
            "top_users": len(top_users),
        })

        
        # Card số liệu
        card_grid = QGridLayout()
        card_grid.setSpacing(15)
        self.add_card(card_grid, 0, 0, "📄 Tổng tài liệu", str(total), "#FFD700")
        self.add_card(card_grid, 0, 1, "✅ Đã duyệt", str(approved), "#4CAF50")
        self.add_card(card_grid, 0, 2, "⏳ Chờ duyệt", str(pending), "#FF9800")
        self.add_card(card_grid, 1, 0, "❌ Từ chối", str(rejected), "#F44336")
        self.add_card(card_grid, 1, 1, "👥 Người dùng", str(users), "#2196F3")
        self.add_card(card_grid, 1, 2, "📨 Yêu cầu chờ", str(pending_orders), "#9C27B0")
        self.add_card(card_grid, 2, 0, "🔔 Thông báo chưa đọc", str(unread_notif), "#E91E63")
        card_widget = QWidget()
        card_widget.setLayout(card_grid)
        self.content_layout.addWidget(card_widget)
        
        # Các bảng thống kê
        self.add_table_group("🏢 Tài liệu đã duyệt theo phòng ban", docs_by_dept, ["Phòng ban", "Số lượng"])
        self.add_table_group("📁 Tài liệu theo loại file", docs_by_type, ["Loại file", "Số lượng"])
        # Chuyển role number thành tên
        role_names = {1: "Nhân viên", 2: "Trưởng phòng", 3: "Giám đốc"}
        users_display = [(role_names.get(row['role'], "Khác"), row['count']) for row in users_by_role]
        self.add_table_group("👤 Người dùng theo vai trò", users_display, ["Vai trò", "Số lượng"])
        self.add_table_group("📅 Hoạt động 7 ngày qua", logs_7days, ["Ngày", "Số thao tác"])
        self.add_table_group("🏆 Top người dùng nhiều tài liệu", top_users, ["Người dùng", "Số tài liệu"])
        
        self.content_layout.addStretch()
    
    def add_card(self, grid, row, col, title, value, color):
        card = QGroupBox(title)
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: rgba(94, 57, 47, 0.3);
                border: 2px solid {color};
                border-radius: 15px;
                margin-top: 15px;
                padding: 10px;
                font-weight: bold;
                color: {color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        layout = QVBoxLayout(card)
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        grid.addWidget(card, row, col)
    
    def add_table_group(self, title, data, headers):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(94, 57, 47, 0.2);
                border: 1px solid #D4AF37;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
                color: #FFD700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(group)
        if not data:
            lbl = QLabel("Không có dữ liệu")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
        else:
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

            # sqlite3.Row khi được iterate thường cho ra giá trị, nhưng đôi khi sẽ lộ thứ tự không như mong đợi.
            # Ép row_data thành list theo số cột headers để đảm bảo render đúng.
            table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                if row_data is None:
                    row_values = [""] * len(headers)
                elif hasattr(row_data, 'keys') and hasattr(row_data, 'values'):
                    row_values = list(row_data)[:len(headers)]
                else:
                    row_values = list(row_data)[:len(headers)]

                # Nếu thiếu cột thì pad cho đủ.
                if len(row_values) < len(headers):
                    row_values = row_values + [""] * (len(headers) - len(row_values))

                for col_idx, val in enumerate(row_values):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

            # Force sizing so it always shows inside QScrollArea
            table.setMinimumHeight(max(120, 28 * max(1, len(data))))
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            table.resizeColumnsToContents()
            layout.addWidget(table)

        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.content_layout.addWidget(group)

