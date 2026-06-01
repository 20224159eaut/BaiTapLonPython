
import os
from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QListWidget,
                             QListWidgetItem, QWidget, QHBoxLayout, QLabel, QSizePolicy,
                             QScrollArea, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from datetime import datetime
from styles import APP_STYLE

# Import tất cả các trang
from pages.my_documents_page import MyDocumentsPage
from pages.department_docs_page import DepartmentDocsPage
from pages.notifications_page import NotificationsPage
from pages.approve_page import ApprovePage
from pages.create_account_page import CreateAccountPage
from pages.due_page import DuePage
from pages.stats_page import StatsPage
from pages.user_management_page import UserManagementPage
from pages.log_page import LogPage
from pages.chat_page import ChatPage
from pages.profile_page import ProfilePage
from pages.change_password_page import ChangePasswordPage
from pages.send_due_order_page import SendDueOrderPage


class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()  # Phát ra khi nhấn Đăng xuất

    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user
        self._logout_requested = False  # Cờ phân biệt logout / tắt cửa sổ

        self.setWindowTitle("Quản lý tài liệu Công ty ABC")
        self.resize(1200, 800)
        self.setStyleSheet(APP_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMinimumWidth(220)
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: #4E342E;
                color: #FFD700;
                border-right: 2px solid #D4AF37;
            }
            QListWidget::item {
                padding: 15px;
                font-weight: bold;
            }
            QListWidget::item:selected {
                background: #8D6E63;
            }
        """)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Ánh xạ tên hiển thị -> widget trang
        self.page_map = {}

        # Xây dựng sidebar + stack
        self.build_sidebar_and_stack()

        # Kết nối sự kiện chọn item
        self.sidebar.currentRowChanged.connect(self.on_sidebar_changed)

        # Timer cập nhật số thông báo chưa đọc
        self.notif_timer = QTimer()
        self.notif_timer.timeout.connect(self.update_notification_badge)
        self.notif_timer.start(5000)
        self.update_notification_badge()

        # Chọn item đầu tiên (Trang chủ) mặc định
        self.sidebar.setCurrentRow(0)

    def build_sidebar_and_stack(self):
        """Xây dựng sidebar và stack đồng bộ, lưu widget vào item data"""
        self.sidebar.clear()
        while self.stack.count() > 0:
            self.stack.removeWidget(self.stack.widget(0))

        def wrap_in_scroll(page_widget: QWidget) -> QWidget:
            """Bọc page trong QScrollArea để tránh page push kích thước cửa sổ (nhất là các QTableWidget)."""
            scroll = QScrollArea()
            scroll.setWidget(page_widget)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            return scroll

        # Hàm tiện ích thêm một mục
        def add_item(text, widget):
            page_container = wrap_in_scroll(widget)
            item = QListWidgetItem(text)  # Tạo item
            item.setData(Qt.ItemDataRole.UserRole, page_container)  # Gắn widget đã bọc
            self.sidebar.addItem(item)
            self.stack.addWidget(page_container)

        # Trang chào mừng
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(94, 57, 47, 0.2);
                border-radius: 30px;
                margin: 50px;
            }
            QLabel {
                color: #FFD700;
                font-family: 'Segoe UI', Arial;
                background: transparent;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(15)

        # Xác định tên role
        role_map = {1: "Nhân viên", 2: "Trưởng phòng", 3: "Giám đốc"}
        role_name = role_map.get(self.user['role'], "Thành viên")
        full_name = self.user['full_name']

        # Nếu full_name đã bắt đầu bằng role_name thì không thêm nữa
        if not full_name.startswith(role_name):
            display_name = f"{role_name} {full_name}"
        else:
            display_name = full_name

        # Dòng 1: Xin chào,
        lbl1 = QLabel("Chào mừng quay trở lại!")
        lbl1.setStyleSheet("font-size: 32px; font-weight: bold;")
        # Dòng 2: Tên hiển thị (không lặp)
        lbl2 = QLabel(display_name)
        lbl2.setStyleSheet("font-size: 28px; font-weight: normal;")
        # Dòng 3: Bắt đầu làm việc nào!
        lbl3 = QLabel("Hãy bắt đầu làm việc nào!")
        lbl3.setStyleSheet("font-size: 26px; font-weight: bold;")

        # Ngày tháng hiện tại
        today_str = datetime.now().strftime("%d/%m/%Y")
        lbl_date = QLabel(f"Hôm nay: {today_str}")
        lbl_date.setStyleSheet("font-size: 20px; margin-top: 30px; color: #FFC107;")

        welcome_layout.addWidget(lbl1)
        welcome_layout.addWidget(lbl2)
        welcome_layout.addWidget(lbl3)
        welcome_layout.addWidget(lbl_date)
        welcome_layout.addStretch()

        add_item("🏠 Trang chủ", welcome_widget)

        # Các trang chung
        add_item("📄 Tài liệu của tôi", MyDocumentsPage(self.db, self.user))
        add_item("📂 Tài liệu phòng ban", DepartmentDocsPage(self.db, self.user))
        add_item("🔔 Thông báo", NotificationsPage(self.db, self.user))   # ← widget NotificationsPage

        # Duyệt tài liệu (role ≥ 2)
        if self.user['role'] >= 2:
            add_item("✅ Duyệt tài liệu", ApprovePage(self.db, self.user))

        # Tạo tài khoản (role 3)
        if self.user['role'] == 3:
            add_item("👤 Tạo tài khoản", CreateAccountPage(self.db, self.user))

        # Gửi yêu cầu chia sẻ (role ≥ 2)
        if self.user['role'] >= 2:
            add_item("📨 Gửi yêu cầu", SendDueOrderPage(self.db, self.user))

        # Tài liệu đến hạn (role 1)
        if self.user['role'] in [1, 2]:
            add_item("⏰ Tài liệu đến hạn", DuePage(self.db, self.user))

        # Thống kê, quản lý người dùng, nhật ký (role 3)
        if self.user['role'] == 3:
            add_item("📊 Thống kê", StatsPage(self.db, self.user))
            add_item("⚙️ Quản lí người dùng", UserManagementPage(self.db, self.user))
            add_item("📜 Nhật kí", LogPage(self.db, self.user))

        # Các trang chung khác
        add_item("💬 Trò chuyện", ChatPage(self.db, self.user))
        add_item("👤 Thông tin cá nhân", ProfilePage(self.db, self.user))
        add_item("🔑 Đổi mật khẩu", ChangePasswordPage(self.db, self.user))

        # Mục Đăng xuất (widget rỗng)
        add_item("🚪 Đăng xuất", QWidget())

    def on_sidebar_changed(self, index):
        """Xử lý khi chọn mục trong sidebar"""
        item = self.sidebar.item(index)
        if item is None:
            return

        item_text = item.text()

        # Nếu là mục Đăng xuất (chỉ cần kiểm tra bắt đầu bằng "🚪")
        if item_text.startswith("🚪 Đăng xuất"):
            self.db.add_log(self.user['id'], "Đăng xuất")
            self._logout_requested = True
            self.logout_signal.emit()
            return

        # Lấy widget đã lưu trong data của item
        container = item.data(Qt.ItemDataRole.UserRole)
        if container:
            self.stack.setCurrentWidget(container)

            # container là QScrollArea, widget gốc là container.widget()
            page_widget = container.widget() if hasattr(container, 'widget') else None
            if page_widget and hasattr(page_widget, 'load_data'):
                page_widget.load_data()

    def update_notification_badge(self):
        """Cập nhật số thông báo chưa đọc trên mục Thông báo"""
        count = self.db.unread_notifications_count(self.user['id'])
        # Tìm item "🔔 Thông báo" để sửa text
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if item.text().startswith("🔔 Thông báo"):
                if count > 0:
                    item.setText(f"🔔 Thông báo ({count})")
                else:
                    item.setText("🔔 Thông báo")
                break