from PyQt6.QtWidgets import QWidget

class BasePage(QWidget):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user

    def load_data(self):
        pass  # Ghi đè ở các trang con