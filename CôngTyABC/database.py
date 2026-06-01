import sqlite3
import os
from datetime import datetime, timedelta

# Việt Nam: GMT+7 (giữ để tham chiếu, KHÔNG dùng để cộng thêm giờ vào DB)
VN_TZ_OFFSET = timedelta(hours=7)

# Lưu ý:
# - App đang lưu thời gian theo giờ local của máy.
# - Vì vậy khi ghi vào DB KHÔNG được cộng thêm +7h (tránh bị lệch).


def _shift_datetime_str_to_vn(dt_str: str):
    """Chuyển chuỗi timestamp trong DB sang giờ Việt Nam.
    Giả định DB đang lưu dạng 'YYYY-MM-DD HH:MM:SS' theo giờ UTC/không rõ.
    Nếu parse thất bại thì trả nguyên chuỗi.
    """
    if dt_str is None:
        return dt_str
    if isinstance(dt_str, (int, float)):
        try:
            dt = datetime.fromtimestamp(dt_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(dt_str)
    if not isinstance(dt_str, str):
        dt_str = str(dt_str)
    try:
        dt = datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return dt_str


DB_NAME = 'company_abc.db'

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

    def _add_column_if_not_exists(self, table, column, col_type):
        """Thêm cột vào bảng nếu chưa tồn tại"""
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in self.cursor.fetchall()]
        if column not in columns:
            self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
            self.conn.commit()

    def initialize_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                role INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                file_type TEXT,
                department TEXT,
                shared_status TEXT DEFAULT 'private',
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                document_id INTEGER,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER DEFAULT NULL,
                content TEXT NOT NULL,
                is_global INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS due_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                message TEXT,
                is_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                -- cột attachment_path sẽ được thêm bên dưới nếu chưa có
            )
        ''')
        self.conn.commit()

        # Thêm cột attachment_path cho bảng due_orders (nếu chưa có)
        self._add_column_if_not_exists("due_orders", "attachment_path", "TEXT")

        # Tạo tài khoản admin nếu chưa có
        self.cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        if self.cursor.fetchone() is None:
            self.cursor.execute('''
                INSERT INTO users (username, password, full_name, department, position, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin123', 'Giám đốc', 'Ban Giám đốc', 'Giám đốc', 3))
            self.conn.commit()

    # ========== USER ==========
    def validate_login(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return self.cursor.fetchone()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def change_password(self, user_id, new_password):
        self.cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
        self.conn.commit()

    def create_user(self, username, password, full_name, department, position, role):
        self.cursor.execute('''
            INSERT INTO users (username, password, full_name, department, position, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, full_name, department, position, role))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def get_users_by_roles(self, roles):
        """Lấy danh sách user có role nằm trong danh sách roles"""
        placeholders = ','.join(['?'] * len(roles))
        self.cursor.execute(f"SELECT id, full_name, role FROM users WHERE role IN ({placeholders})", roles)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_user(self, user_id, full_name, department, position, role):
        self.cursor.execute('''
            UPDATE users SET full_name=?, department=?, position=?, role=?
            WHERE id=?
        ''', (full_name, department, position, role, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()

    # ========== DOCUMENTS ==========
    def add_document(self, user_id, title, description, file_path, file_type, department=None):
        self.cursor.execute('''
            INSERT INTO documents (user_id, title, description, file_path, file_type, department, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            title,
            description,
            file_path,
            file_type,
            department,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        self.conn.commit()

    def update_document(self, doc_id, title, description, file_path, file_type):
        self.cursor.execute('''
            UPDATE documents SET title=?, description=?, file_path=?, file_type=?, updated_at=?
            WHERE id=?
        ''', (title, description, file_path, file_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), doc_id))
        self.conn.commit()

    def delete_document(self, doc_id):
        self.cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        self.conn.commit()

    def get_user_documents(self, user_id):
        self.cursor.execute("SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return self.cursor.fetchall()

    def get_shared_documents_by_user(self, user_id):
        self.cursor.execute("SELECT * FROM documents WHERE user_id = ? AND shared_status != 'private'", (user_id,))
        return self.cursor.fetchall()

    def get_approved_department_docs(self, department=None):
        if department:
            self.cursor.execute("SELECT d.*, u.full_name FROM documents d JOIN users u ON d.user_id = u.id WHERE d.shared_status = 'approved' AND d.department = ?", (department,))
        else:
            self.cursor.execute("SELECT d.*, u.full_name FROM documents d JOIN users u ON d.user_id = u.id WHERE d.shared_status = 'approved'")
        return self.cursor.fetchall()

    def get_pending_documents(self):
        self.cursor.execute("SELECT d.*, u.full_name, u.department as user_dept FROM documents d JOIN users u ON d.user_id = u.id WHERE d.shared_status = 'pending'")
        return self.cursor.fetchall()

    def share_document(self, doc_id, department):
        self.cursor.execute("UPDATE documents SET shared_status = 'pending', department = ? WHERE id = ?",
                            (department, doc_id))
        self.conn.commit()
        doc = self.get_document(doc_id)
        self.add_log(doc['user_id'], f"Chia sẻ tài liệu '{doc['title']}' vào phòng ban {department}")

    def request_update_shared_document(self, doc_id, title, description, file_path, file_type):
        self.cursor.execute('''
            UPDATE documents SET title=?, description=?, file_path=?, file_type=?, shared_status='pending', updated_at=?
            WHERE id=?
        ''', (title, description, file_path, file_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), doc_id))
        self.conn.commit()

    def get_document(self, doc_id):
        self.cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        return self.cursor.fetchone()

    def search_my_documents(self, user_id, keyword):
        q = "%" + keyword + "%"
        self.cursor.execute("SELECT * FROM documents WHERE user_id = ? AND (title LIKE ? OR description LIKE ?)",
                            (user_id, q, q))
        return self.cursor.fetchall()

    def search_department_docs(self, keyword, doc_type=None, dept=None):
        query = "SELECT d.*, u.full_name FROM documents d JOIN users u ON d.user_id = u.id WHERE d.shared_status = 'approved'"
        params = []
        if keyword:
            query += " AND (d.title LIKE ? OR d.description LIKE ?)"
            q = "%" + keyword + "%"
            params.extend([q, q])
        if doc_type:
            query += " AND d.file_type = ?"
            params.append(doc_type)
        if dept:
            query += " AND d.department = ?"
            params.append(dept)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # ========== APPROVAL ==========
    def approve_document(self, doc_id, approver_id):
        self.cursor.execute("UPDATE documents SET shared_status = 'approved' WHERE id = ?", (doc_id,))
        self.conn.commit()
        doc = self.get_document(doc_id)
        self.add_notification(doc['user_id'], f"Tài liệu '{doc['title']}' đã được duyệt.", 'approve', doc_id)
        self.add_log(approver_id, f"Duyệt tài liệu ID {doc_id}")

    def reject_document(self, doc_id, reason, approver_id):
        self.cursor.execute("UPDATE documents SET shared_status = 'rejected', rejection_reason = ? WHERE id = ?",
                            (reason, doc_id))
        self.conn.commit()
        doc = self.get_document(doc_id)
        self.add_notification(doc['user_id'], f"Tài liệu '{doc['title']}' bị từ chối. Lý do: {reason}", 'reject', doc_id)
        self.add_log(approver_id, f"Từ chối tài liệu ID {doc_id} - Lý do: {reason}")

    # ========== NOTIFICATION ==========
    def add_notification(self, user_id, message, ntype, doc_id=None):
        self.cursor.execute('''
            INSERT INTO notifications (user_id, message, type, document_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, message, ntype, doc_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()

    def get_notifications(self, user_id):
        self.cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if 'created_at' in d:
                d['created_at'] = _shift_datetime_str_to_vn(d['created_at'])
            result.append(d)
        return result

    def unread_notifications_count(self, user_id):
        self.cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
        return self.cursor.fetchone()[0]

    def mark_notifications_read(self, user_id):
        self.cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        self.conn.commit()

    # ========== LOG ==========
    def add_log(self, user_id, action):
        self.cursor.execute(
            "INSERT INTO logs (user_id, action, timestamp) VALUES (?, ?, ?)",
            (user_id, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        self.conn.commit()

    def get_logs(self):
        self.cursor.execute("SELECT l.*, u.full_name FROM logs l JOIN users u ON l.user_id = u.id ORDER BY l.timestamp DESC")
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if 'timestamp' in d:
                d['timestamp'] = _shift_datetime_str_to_vn(d['timestamp'])
            result.append(d)
        return result

    # ========== CHAT ==========
    def send_message(self, sender_id, content, receiver_id=None):
        is_global = 1 if receiver_id is None else 0
        self.cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, content, is_global, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (sender_id, receiver_id, content, is_global, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()

    def get_messages(self, user_id=None):
        if user_id:
            self.cursor.execute('''
                SELECT m.*, u.full_name as sender_name FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE (m.receiver_id = ? OR m.receiver_id IS NULL OR m.is_global = 1)
                ORDER BY m.timestamp ASC
            ''', (user_id,))
        else:
            self.cursor.execute('''
                SELECT m.*, u.full_name as sender_name FROM messages m
                JOIN users u ON m.sender_id = u.id
                ORDER BY m.timestamp ASC
            ''')
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if 'timestamp' in d:
                d['timestamp'] = _shift_datetime_str_to_vn(d['timestamp'])
            result.append(d)
        return result

    # ========== DUE ORDERS ==========
    def add_due_order(self, from_uid, to_uid, message, attachment_path=None):
        self.cursor.execute('''
            INSERT INTO due_orders (from_user_id, to_user_id, message, attachment_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (from_uid, to_uid, message, attachment_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        # Thông báo cho người nhận
        self.add_notification(to_uid, f"Bạn có yêu cầu chia sẻ tài liệu mới từ {from_uid}", 'due_order')

    def get_due_orders(self, user_id):
        self.cursor.execute('''
            SELECT o.*, u.full_name as from_name FROM due_orders o
            JOIN users u ON o.from_user_id = u.id
            WHERE o.to_user_id = ? AND o.is_completed = 0
        ''', (user_id,))
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if 'created_at' in d:
                d['created_at'] = _shift_datetime_str_to_vn(d['created_at'])
            result.append(d)
        return result

    def complete_due_order(self, order_id):
        self.cursor.execute("UPDATE due_orders SET is_completed = 1 WHERE id = ?", (order_id,))
        self.conn.commit()
    
        # ========== STATS ==========
    def get_document_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM documents")
        total = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM documents WHERE shared_status = 'approved'")
        approved = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM documents WHERE shared_status = 'pending'")
        pending = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM documents WHERE shared_status = 'rejected'")
        rejected = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM users")
        users = self.cursor.fetchone()[0]
        return total, approved, pending, rejected, users

    def get_docs_by_department(self):
        """Số lượng tài liệu đã duyệt theo phòng ban.

        Lưu ý: documents.department có thể NULL (do luồng approve/update hiện tại không luôn ghi).
        Vì vậy thống kê theo phòng ban của người tạo tài liệu (users.department).
        """
        self.cursor.execute("""
            SELECT u.department, COUNT(*) as count
            FROM documents d
            JOIN users u ON d.user_id = u.id
            WHERE d.shared_status = 'approved' AND u.department IS NOT NULL
            GROUP BY u.department
        """)
        return self.cursor.fetchall()


    def get_docs_by_type(self):
        """Số lượng tài liệu theo loại file"""
        self.cursor.execute("""
            SELECT file_type, COUNT(*) as count 
            FROM documents 
            GROUP BY file_type
        """)
        return self.cursor.fetchall()

    def get_users_by_role_count(self):
        """Số lượng người dùng theo role"""
        self.cursor.execute("""
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        """)
        return self.cursor.fetchall()

    def get_pending_due_orders_count(self):
        """Số yêu cầu chia sẻ chưa hoàn thành"""
        self.cursor.execute("SELECT COUNT(*) FROM due_orders WHERE is_completed = 0")
        return self.cursor.fetchone()[0]

    def get_unread_notifications_total(self):
        """Tổng số thông báo chưa đọc của toàn hệ thống"""
        self.cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = 0")
        return self.cursor.fetchone()[0]

    def get_logs_last_7_days(self):
        """Số lượng log trong 7 ngày gần nhất (theo ngày)"""
        self.cursor.execute("""
            SELECT date(timestamp) as day, COUNT(*) as count
            FROM logs
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY date(timestamp)
            ORDER BY day DESC
        """)
        return self.cursor.fetchall()

    def get_top_users_by_documents(self, limit=5):
        """Top người dùng có nhiều tài liệu nhất"""
        self.cursor.execute("""
            SELECT u.full_name, COUNT(d.id) as doc_count
            FROM users u
            LEFT JOIN documents d ON u.id = d.user_id
            GROUP BY u.id
            ORDER BY doc_count DESC
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()