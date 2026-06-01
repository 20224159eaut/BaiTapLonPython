import sys
import os
from PyQt6.QtWidgets import QApplication
from database import Database
from login_dialog import LoginDialog
from main_window import MainWindow

def main():
    for folder in ['uploads', 'downloads']:
        os.makedirs(folder, exist_ok=True)

    db = Database()
    db.initialize_db()

    app = QApplication(sys.argv)
    while True:
        login = LoginDialog(db)
        if login.exec() == 1:  # thành công
            user = login.get_user()
            window = MainWindow(db, user)
            # Kết nối tín hiệu logout
            window.logout_signal.connect(lambda: handle_logout(window))
            window.show()
            app.exec()
            # Sau khi app.exec() kết thúc (khi MainWindow bị close)
            # Nếu không phải logout chủ động (do tắt cửa sổ), thoát hẳn
            # Chúng ta phân biệt bằng cách kiểm tra thuộc tính _logout_requested
            if not getattr(window, '_logout_requested', False):
                break  # Thoát vòng lặp, kết thúc ứng dụng
            # Nếu là logout, vòng lặp tiếp tục để hiển thị login
        else:
            break  # Nhấn Cancel / tắt login

    sys.exit()

def handle_logout(window):
    """Xử lý khi người dùng bấm Đăng xuất"""
    window._logout_requested = True  # Đánh dấu là logout chủ động
    window.close()  # Đóng MainWindow -> app.exec() sẽ trả về

if __name__ == '__main__':
    main()