APP_STYLE = """
QMainWindow {
    background-color: #3E2723;
}
QPushButton {
    background-color: #8D6E63;
    color: #FFD700;
    border: 1px solid #D4AF37;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #A1887F;
}
QLineEdit, QTextEdit, QComboBox, QTableWidget {
    background-color: #5D4037;
    color: #FFD700;
    border: 1px solid #D4AF37;
    border-radius: 4px;
    padding: 4px;
}
QTableWidget QHeaderView::section {
    background-color: #6D4C41;
    color: #FFD700;
    border: 1px solid #D4AF37;
    padding: 4px;
}
QLabel {
    color: #FFD700;
}
QGroupBox {
    border: 2px solid #D4AF37;
    border-radius: 8px;
    margin-top: 10px;
    color: #FFD700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QListWidget {
    background: #4E342E;
    color: #FFD700;
    border: none;
}
QListWidget::item:selected {
    background: #8D6E63;
}
QComboBox::drop-down {
    border: none;
}
QScrollBar:vertical {
    background: #3E2723;
    width: 12px;
}
QScrollBar::handle:vertical {
    background: #8D6E63;
    border-radius: 6px;
}
"""