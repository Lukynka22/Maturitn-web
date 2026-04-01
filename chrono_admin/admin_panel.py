"""
Admin panel – produkty, uživatelé, statistika + import produktů z CSV
"""

import csv
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QLineEdit, QMessageBox,
    QTextEdit, QTabWidget, QComboBox, QFileDialog
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from database import get_connection


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHRONO Admin Panel")
        self.setGeometry(300, 150, 1200, 700)

        self.tabs = QTabWidget()
        self.init_ui()

        self.load_products()
        self.load_users()
        self.load_years()
        self.load_statistics()

    # =================================================
    # UI
    # =================================================

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.tabs.addTab(self.create_products_tab(), "Produkty")
        self.tabs.addTab(self.create_users_tab(), "Uživatelé")
        self.tabs.addTab(self.create_stats_tab(), "Statistika")

    def create_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.make_title("Správa hodinek"))

        form = QHBoxLayout()
        self.name_input = self.make_input("Název")
        self.price_input = self.make_input("Cena")
        self.stock_input = self.make_input("Skladem")
        self.image_input = self.make_input("Cesta k obrázku")

        add_btn = QPushButton("Přidat produkt")
        add_btn.clicked.connect(self.add_product)

        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.import_products_csv)

        for w in [
            self.name_input,
            self.price_input,
            self.stock_input,
            self.image_input,
            add_btn,
            import_btn
        ]:
            form.addWidget(w)

        layout.addLayout(form)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Popis")
        layout.addWidget(self.desc_input)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Název", "Cena", "Skladem", "Popis", "Kategorie", "Akce"
        ])
        self.table.cellChanged.connect(self.update_product_cell)

        layout.addWidget(QLabel("Produkty v databázi"))
        layout.addWidget(self.table)

        tab.setLayout(layout)
        return tab

    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.make_title("Registrovaní uživatelé"))

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Email", "Avatar", "Akce"
        ])
        self.users_table.cellChanged.connect(self.update_user_cell)

        layout.addWidget(self.users_table)
        tab.setLayout(layout)
        return tab

    def create_stats_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.make_title("Statistika objednávek"))

        controls = QHBoxLayout()

        self.year_combo = QComboBox()
        self.month_combo = QComboBox()

        self.month_combo.addItem("Celý rok", 0)
        for i, month in enumerate([
            "Leden", "Únor", "Březen", "Duben", "Květen", "Červen",
            "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"
        ], start=1):
            self.month_combo.addItem(month, i)

        load_btn = QPushButton("Načíst graf")
        load_btn.clicked.connect(self.load_statistics)

        controls.addWidget(QLabel("Rok:"))
        controls.addWidget(self.year_combo)
        controls.addWidget(QLabel("Období:"))
        controls.addWidget(self.month_combo)
        controls.addWidget(load_btn)

        layout.addLayout(controls)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 15px; font-weight: bold; margin: 8px 0;")
        layout.addWidget(self.stats_label)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        tab.setLayout(layout)
        return tab

    # =================================================
    # HELPERS
    # =================================================

    def make_title(self, text):
        label = QLabel(text)
        label.setStyleSheet("font-size:18px; font-weight:bold;")
        return label

    def make_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        return inp

    def fetch_all(self, query, params=()):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    def execute_query(self, query, params=()):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    # =================================================
    # PRODUKTY
    # =================================================

    def load_products(self):
        products = self.fetch_all(
            "SELECT id, nazev, cena, skladem, popis, kategorie FROM product"
        )

        self.table.blockSignals(True)
        self.table.setRowCount(len(products))

        for r, product in enumerate(products):
            self.table.setItem(r, 0, QTableWidgetItem(str(product["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(product["nazev"] or ""))
            self.table.setItem(r, 2, QTableWidgetItem(str(product["cena"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(product["skladem"])))
            self.table.setItem(r, 4, QTableWidgetItem(product["popis"] or ""))
            self.table.setItem(r, 5, QTableWidgetItem(product["kategorie"] or ""))

            btn = QPushButton("Smazat")
            btn.clicked.connect(lambda _, pid=product["id"]: self.delete_product(pid))
            self.table.setCellWidget(r, 6, btn)

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

        self.execute_query(
            """
            INSERT INTO product (nazev, cena, skladem, popis, image)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, price, stock, desc, image)
        )

        QMessageBox.information(self, "OK", "Produkt přidán")

        for inp in [self.name_input, self.price_input, self.stock_input, self.image_input]:
            inp.clear()
        self.desc_input.clear()

        self.load_products()

    def import_products_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Vyber CSV soubor s produkty",
            "",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        imported_count = 0

        try:
            conn = get_connection()
            cursor = conn.cursor()

            with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file, delimiter=';')

                required_columns = {"nazev", "cena", "skladem", "popis", "image", "kategorie"}
                if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                    QMessageBox.warning(
                        self,
                        "Chyba",
                        "CSV musí obsahovat sloupce: nazev; cena; skladem; popis; image; kategorie"
                    )
                    conn.close()
                    return

                for row in reader:
                    name = (row.get("nazev") or "").strip()
                    price = (row.get("cena") or "").strip()
                    stock = (row.get("skladem") or "").strip()
                    desc = (row.get("popis") or "").strip()
                    image = (row.get("image") or "").strip()
                    category = (row.get("kategorie") or "").strip()

                    if not name or not price or not stock:
                        continue

                    try:
                        price = int(price)
                        stock = int(stock)
                    except ValueError:
                        continue

                    cursor.execute(
                        """
                        INSERT INTO product (nazev, cena, skladem, popis, image, kategorie)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (name, price, stock, desc, image, category)
                    )
                    imported_count += 1

            conn.commit()
            conn.close()

            QMessageBox.information(
                self,
                "Import hotov",
                f"Bylo importováno {imported_count} produktů."
            )
            self.load_products()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Chyba importu",
                f"Nepodařilo se importovat CSV.\n\nDetail: {str(e)}"
            )

    def delete_product(self, product_id):
        self.execute_query("DELETE FROM product WHERE id=%s", (product_id,))
        QMessageBox.information(self, "OK", "Produkt smazán")
        self.load_products()

    def update_product_cell(self, row, column):
        if column in (0, 6):
            return

        item_id = self.table.item(row, 0)
        value_item = self.table.item(row, column)
        if not item_id or not value_item:
            return

        column_map = {
            1: "nazev",
            2: "cena",
            3: "skladem",
            4: "popis",
            5: "kategorie"
        }

        if column not in column_map:
            return

        product_id = item_id.text()
        value = value_item.text()
        column_name = column_map[column]

        try:
            if column_name in ("cena", "skladem"):
                value = int(value)
        except ValueError:
            QMessageBox.warning(self, "Chyba", f"{column_name} musí být číslo")
            self.load_products()
            return

        self.execute_query(
            f"UPDATE product SET {column_name}=%s WHERE id=%s",
            (value, product_id)
        )

    # =================================================
    # UŽIVATELÉ
    # =================================================

    def load_users(self):
        users = self.fetch_all("SELECT id, username, email, avatar FROM user")

        self.users_table.blockSignals(True)
        self.users_table.setRowCount(len(users))

        for r, user in enumerate(users):
            self.users_table.setItem(r, 0, QTableWidgetItem(str(user["id"])))
            self.users_table.setItem(r, 1, QTableWidgetItem(user["username"] or ""))
            self.users_table.setItem(r, 2, QTableWidgetItem(user["email"] or ""))
            self.users_table.setItem(r, 3, QTableWidgetItem(user["avatar"] or ""))

            btn = QPushButton("Smazat")
            btn.clicked.connect(lambda _, uid=user["id"]: self.delete_user(uid))
            self.users_table.setCellWidget(r, 4, btn)

        self.users_table.blockSignals(False)

    def update_user_cell(self, row, column):
        if column in (0, 4):
            return

        item_id = self.users_table.item(row, 0)
        value_item = self.users_table.item(row, column)
        if not item_id or not value_item:
            return

        column_map = {
            1: "username",
            2: "email",
            3: "avatar"
        }

        if column not in column_map:
            return

        user_id = item_id.text()
        value = value_item.text()
        column_name = column_map[column]

        self.execute_query(
            f"UPDATE user SET {column_name}=%s WHERE id=%s",
            (value, user_id)
        )

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

        self.execute_query("DELETE FROM user WHERE id=%s", (user_id,))
        QMessageBox.information(self, "OK", "Uživatel smazán")
        self.load_users()

    # =================================================
    # STATISTIKA
    # =================================================

    def load_years(self):
        self.year_combo.clear()

        try:
            years = self.fetch_all("""
                SELECT DISTINCT YEAR(created_at) AS year_value
                FROM `order`
                WHERE created_at IS NOT NULL
                ORDER BY year_value DESC
            """)
        except Exception:
            years = []

        if years:
            for row in years:
                self.year_combo.addItem(str(row["year_value"]), row["year_value"])
        else:
            current_year = datetime.now().year
            self.year_combo.addItem(str(current_year), current_year)

    def load_statistics(self):
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()

        if year is None:
            year = datetime.now().year

        try:
            if month == 0:
                summary = self.fetch_all("""
                    SELECT COUNT(*) AS total_orders,
                           COALESCE(SUM(total_price), 0) AS total_revenue
                    FROM `order`
                    WHERE YEAR(created_at)=%s
                """, (year,))[0]

                rows = self.fetch_all("""
                    SELECT MONTH(created_at) AS period_num,
                           COALESCE(SUM(total_price), 0) AS revenue
                    FROM `order`
                    WHERE YEAR(created_at)=%s
                    GROUP BY MONTH(created_at)
                    ORDER BY MONTH(created_at)
                """, (year,))

                labels = ["Led", "Úno", "Bře", "Dub", "Kvě", "Čvn", "Čvc", "Srp", "Zář", "Říj", "Lis", "Pro"]
                values = [0] * 12

                for row in rows:
                    values[row["period_num"] - 1] = float(row["revenue"])

                self.stats_label.setText(
                    f"Rok {year} | Objednávek: {summary['total_orders']} | Tržba: {summary['total_revenue']} Kč"
                )

            else:
                summary = self.fetch_all("""
                    SELECT COUNT(*) AS total_orders,
                           COALESCE(SUM(total_price), 0) AS total_revenue
                    FROM `order`
                    WHERE YEAR(created_at)=%s AND MONTH(created_at)=%s
                """, (year, month))[0]

                rows = self.fetch_all("""
                    SELECT DAY(created_at) AS period_num,
                           COALESCE(SUM(total_price), 0) AS revenue
                    FROM `order`
                    WHERE YEAR(created_at)=%s AND MONTH(created_at)=%s
                    GROUP BY DAY(created_at)
                    ORDER BY DAY(created_at)
                """, (year, month))

                max_day = 31
                labels = [str(i) for i in range(1, max_day + 1)]
                values = [0] * max_day

                for row in rows:
                    values[row["period_num"] - 1] = float(row["revenue"])

                self.stats_label.setText(
                    f"{self.month_combo.currentText()} {year} | "
                    f"Objednávek: {summary['total_orders']} | "
                    f"Tržba: {summary['total_revenue']} Kč"
                )

            self.draw_chart(labels, values)

        except Exception as e:
            self.stats_label.setText("Statistika není dostupná.")
            QMessageBox.warning(
                self,
                "Chyba statistiky",
                "Nepodařilo se načíst statistiku.\n"
                "Zkontroluj tabulku order a sloupce total_price, created_at.\n\n"
                f"Detail: {e}"
            )

    def draw_chart(self, labels, values):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.bar(labels, values)
        ax.set_title("Tržba")
        ax.set_xlabel("Období")
        ax.set_ylabel("Kč")
        ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()
