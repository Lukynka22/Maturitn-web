from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from werkzeug.security import check_password_hash
from database import get_connection


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("CHRONO Admin – Přihlášení")
        self.setGeometry(400, 250, 350, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Uživatelské jméno")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Heslo")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Přihlásit se")
        login_btn.clicked.connect(self.login)

        layout.addWidget(QLabel("Přihlášení admina"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login(self):
        from admin_panel import AdminPanel

        username = self.username_input.text().strip()
        password = self.password_input.text()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            QMessageBox.warning(self, "Chyba", "Uživatel neexistuje")
            return

        if not check_password_hash(user["password"], password):
            QMessageBox.warning(self, "Chyba", "Špatné heslo")
            return

        if not user["is_admin"]:
            QMessageBox.warning(self, "Chyba", "Nemáš oprávnění pro admin panel")
            return

        QMessageBox.information(self, "OK", "Přihlášení úspěšné")
        self.admin_panel = AdminPanel()
        self.admin_panel.show()
        self.close()
