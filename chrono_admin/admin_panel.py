"""
Admin panel – správa hodinek a uživatelů
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton,
    QLineEdit, QMessageBox, QTextEdit,
    QTabWidget
)

from database import get_connection


class AdminPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()
        self.load_users()

    def init_ui(self):

        self.setWindowTitle("CHRONO Admin Panel")
        self.setGeometry(300, 150, 1200, 700)

        layout = QVBoxLayout()
        tabs = QTabWidget()

        # =================================================
        # TAB 1 – PRODUKTY
        # =================================================

        products_tab = QWidget()
        products_layout = QVBoxLayout()

        title = QLabel("Správa hodinek")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        products_layout.addWidget(title)

        form = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Název")

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Cena")

        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Skladem")

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Cesta k obrázku")

        add_btn = QPushButton("Přidat produkt")
        add_btn.clicked.connect(self.add_product)

        form.addWidget(self.name_input)
        form.addWidget(self.price_input)
        form.addWidget(self.stock_input)
        form.addWidget(self.image_input)
        form.addWidget(add_btn)

        products_layout.addLayout(form)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Popis")
        products_layout.addWidget(self.desc_input)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Název", "Cena", "Skladem", "Popis", "Kategorie", "Akce"
        ])
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.cellChanged.connect(self.update_product_cell)

        products_layout.addWidget(QLabel("Produkty v databázi"))
        products_layout.addWidget(self.table)

        products_tab.setLayout(products_layout)

        # =================================================
        # TAB 2 – UŽIVATELÉ
        # =================================================

        users_tab = QWidget()
        users_layout = QVBoxLayout()

        users_title = QLabel("Registrovaní uživatelé")
        users_title.setStyleSheet("font-size:18px; font-weight:bold;")
        users_layout.addWidget(users_title)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Email", "Avatar", "Akce"
        ])
        self.users_table.setEditTriggers(QTableWidget.DoubleClicked)
        self.users_table.cellChanged.connect(self.update_user_cell)

        users_layout.addWidget(self.users_table)
        users_tab.setLayout(users_layout)

        # =================================================

        tabs.addTab(products_tab, "Produkty")
        tabs.addTab(users_tab, "Uživatelé")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # =================================================
    # PRODUKTY
    # =================================================

    def load_products(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nazev, cena, skladem, popis, kategorie FROM product"
        )
        products = cursor.fetchall()
        conn.close()

        self.table.blockSignals(True)
        self.table.setRowCount(len(products))

        for r, product in enumerate(products):
            self.table.setItem(r, 0, QTableWidgetItem(str(product["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(product["nazev"] or ""))
            self.table.setItem(r, 2, QTableWidgetItem(str(product["cena"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(product["skladem"])))
            self.table.setItem(r, 4, QTableWidgetItem(product["popis"] or ""))
            self.table.setItem(r, 5, QTableWidgetItem(product["kategorie"] or ""))

            delete_btn = QPushButton("Smazat")
            delete_btn.clicked.connect(
                lambda _, pid=product["id"]: self.delete_product(pid)
            )
            self.table.setCellWidget(r, 6, delete_btn)

        self.table.blockSignals(False)

    def add_product(self):

        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.text().strip()
        image = self.image_input.text().strip()
        desc = self.desc_input.toPlainText().strip()

        if not name or not price or not stock:
            QMessageBox.warning(self, "Chyba", "Vyplň název, cenu a sklad")
            return

        try:
            price = int(price)
            stock = int(stock)
        except ValueError:
            QMessageBox.warning(self, "Chyba", "Cena a sklad musí být číslo")
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO product (nazev, cena, skladem, popis, image)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, price, stock, desc, image)
        )

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Produkt přidán")

        self.name_input.clear()
        self.price_input.clear()
        self.stock_input.clear()
        self.image_input.clear()
        self.desc_input.clear()

        self.load_products()

    def delete_product(self, product_id):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM product WHERE id=%s",
            (product_id,)
        )

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Produkt smazán")
        self.load_products()

    def update_product_cell(self, row, column):

        if column in (0, 6):
            return

        product_id_item = self.table.item(row, 0)
        value_item = self.table.item(row, column)

        if product_id_item is None or value_item is None:
            return

        product_id = product_id_item.text()
        value = value_item.text()

        column_map = {
            1: "nazev",
            2: "cena",
            3: "skladem",
            4: "popis",
            5: "kategorie"
        }

        if column not in column_map:
            return

        column_name = column_map[column]

        try:
            if column_name in ("cena", "skladem"):
                value = int(value)
        except ValueError:
            QMessageBox.warning(self, "Chyba", f"{column_name} musí být číslo")
            self.load_products()
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"UPDATE product SET {column_name}=%s WHERE id=%s",
            (value, product_id)
        )

        conn.commit()
        conn.close()

    # =================================================
    # UŽIVATELÉ
    # =================================================

    def load_users(self):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, email, avatar FROM user"
        )
        users = cursor.fetchall()
        conn.close()

        self.users_table.blockSignals(True)
        self.users_table.setRowCount(len(users))

        for r, user in enumerate(users):
            self.users_table.setItem(r, 0, QTableWidgetItem(str(user["id"])))
            self.users_table.setItem(r, 1, QTableWidgetItem(user["username"] or ""))
            self.users_table.setItem(r, 2, QTableWidgetItem(user["email"] or ""))
            self.users_table.setItem(r, 3, QTableWidgetItem(user["avatar"] or ""))

            delete_btn = QPushButton("Smazat")
            delete_btn.clicked.connect(
                lambda _, uid=user["id"]: self.delete_user(uid)
            )

            self.users_table.setCellWidget(r, 4, delete_btn)

        self.users_table.blockSignals(False)

    def update_user_cell(self, row, column):

        if column in (0, 4):
            return

        user_id_item = self.users_table.item(row, 0)
        value_item = self.users_table.item(row, column)

        if user_id_item is None or value_item is None:
            return

        user_id = user_id_item.text()
        value = value_item.text()

        column_map = {
            1: "username",
            2: "email",
            3: "avatar"
        }

        if column not in column_map:
            return

        column_name = column_map[column]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"UPDATE user SET {column_name}=%s WHERE id=%s",
            (value, user_id)
        )

        conn.commit()
        conn.close()

    def delete_user(self, user_id):

        reply = QMessageBox.question(
            self,
            "Potvrzení",
            "Opravdu chceš smazat tohoto uživatele?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM user WHERE id=%s",
            (user_id,)
        )

        conn.commit()
        conn.close()

        QMessageBox.information(self, "OK", "Uživatel smazán")
        self.load_users()
