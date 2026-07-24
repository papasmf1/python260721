import sys
import sqlite3
from typing import Optional, Sequence, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MyProductDB:
    def __init__(self, db_name: str = "MyProduct.db") -> None:
        self.db_name = db_name
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def _create_table(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS MyProduct (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def insert_product(self, name: str, price: int) -> int:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO MyProduct (name, price) VALUES (?, ?)",
                (name, price),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def update_product(self, product_id: int, name: str, price: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
                (name, price, product_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM MyProduct WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_products(self, keyword: str) -> Sequence[Tuple[int, str, int]]:
        keyword = keyword.strip()
        with self._connect() as conn:
            cursor = conn.cursor()
            if not keyword:
                cursor.execute("SELECT id, name, price FROM MyProduct ORDER BY id DESC")
            elif keyword.isdigit():
                cursor.execute(
                    "SELECT id, name, price FROM MyProduct WHERE id = ? ORDER BY id DESC",
                    (int(keyword),),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, name, price
                    FROM MyProduct
                    WHERE name LIKE ?
                    ORDER BY id DESC
                    """,
                    (f"%{keyword}%",),
                )
            return cursor.fetchall()

    def fetch_all(self) -> Sequence[Tuple[int, str, int]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM MyProduct ORDER BY id DESC")
            return cursor.fetchall()


class BicycleProductManager(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.db = MyProductDB()
        self.current_selected_id: Optional[int] = None
        self._build_ui()
        self._load_table()

    def _build_ui(self) -> None:
        self.setWindowTitle("자전거용품 입출력 관리")
        self.setMinimumSize(760, 560)
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #08111f, stop:0.55 #102a43, stop:1 #1f3a5f);
            }
            QWidget {
                color: #f5f8ff;
                font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QLabel#titleLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 12px 8px;
            }
            QLabel[class="formLabel"] {
                color: #dbe8ff;
                font-weight: 600;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 10px;
                padding: 10px 12px;
                color: #ffffff;
                selection-background-color: #38bdf8;
            }
            QLineEdit:focus {
                border: 1px solid #7dd3fc;
                background: rgba(255, 255, 255, 0.18);
            }
            QLineEdit:read-only {
                color: #b8c9e6;
                background: rgba(255, 255, 255, 0.07);
            }
            QPushButton {
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: 700;
                color: #08111f;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8fafc, stop:1 #cbd5e1);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #e2e8f0);
            }
            QPushButton:pressed {
                background: #94a3b8;
                padding-top: 11px;
                padding-left: 17px;
            }
            QPushButton#insertButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #22c55e, stop:1 #16a34a);
                color: #ffffff;
            }
            QPushButton#updateButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #38bdf8, stop:1 #0284c7);
                color: #ffffff;
            }
            QPushButton#deleteButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fb7185, stop:1 #e11d48);
                color: #ffffff;
            }
            QPushButton#searchButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fbbf24, stop:1 #f59e0b);
                color: #1f2937;
            }
            QPushButton#clearButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #cbd5e1, stop:1 #94a3b8);
                color: #0f172a;
            }
            QTableWidget {
                background: rgba(255, 255, 255, 0.08);
                alternate-background-color: rgba(255, 255, 255, 0.12);
                color: #f8fbff;
                gridline-color: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 14px;
                selection-background-color: rgba(56, 189, 248, 0.45);
                selection-color: #ffffff;
            }
            QHeaderView::section {
                background: rgba(255, 255, 255, 0.16);
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: 700;
            }
            QTableCornerButton::section {
                background: rgba(255, 255, 255, 0.16);
                border: none;
            }
            """
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        title_label = QLabel("자전거용품 등록 / 수정 / 삭제 / 검색")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("자동 생성 ID")
        self.id_edit.setReadOnly(True)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("상품명 입력")

        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("가격 입력")

        form_layout.addLayout(self._row_widget("ID", self.id_edit))
        form_layout.addLayout(self._row_widget("이름", self.name_edit))
        form_layout.addLayout(self._row_widget("가격", self.price_edit))
        main_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.insert_button = QPushButton("입력")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.search_button = QPushButton("검색")
        self.clear_button = QPushButton("초기화")

        self.insert_button.setObjectName("insertButton")
        self.update_button.setObjectName("updateButton")
        self.delete_button.setObjectName("deleteButton")
        self.search_button.setObjectName("searchButton")
        self.clear_button.setObjectName("clearButton")

        self.insert_button.clicked.connect(self.insert_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.search_button.clicked.connect(self.search_product)
        self.clear_button.clicked.connect(self.clear_inputs)

        for button in (
            self.insert_button,
            self.update_button,
            self.delete_button,
            self.search_button,
            self.clear_button,
        ):
            button_layout.addWidget(button)

        main_layout.addLayout(button_layout)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "이름", "가격"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)
        main_layout.addWidget(self.table)

    def _row_widget(self, label_text: str, editor: QLineEdit) -> QHBoxLayout:
        row_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setProperty("class", "formLabel")
        label.setFixedWidth(60)
        row_layout.addWidget(label)
        row_layout.addWidget(editor)
        return row_layout

    def _show_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.warning(self, title, message)

    def _get_name_and_price(self) -> tuple[str, int]:
        name = self.name_edit.text().strip()
        price_text = self.price_edit.text().strip()

        if not name:
            raise ValueError("상품명을 입력하세요.")
        if not price_text:
            raise ValueError("가격을 입력하세요.")
        if not price_text.isdigit():
            raise ValueError("가격은 숫자로 입력하세요.")

        return name, int(price_text)

    def _load_table(self, rows: Optional[Sequence[Tuple[int, str, int]]] = None) -> None:
        if rows is None:
            rows = self.db.fetch_all()

        self.table.setRowCount(0)
        for row_index, (product_id, name, price) in enumerate(rows):
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(str(product_id)))
            self.table.setItem(row_index, 1, QTableWidgetItem(name))
            self.table.setItem(row_index, 2, QTableWidgetItem(f"{price:,}"))

    def insert_product(self) -> None:
        try:
            name, price = self._get_name_and_price()
            new_id = self.db.insert_product(name, price)
        except ValueError as exc:
            self._show_error("입력 오류", str(exc))
            return
        except sqlite3.Error as exc:
            self._show_error("DB 오류", str(exc))
            return

        self._load_table()
        self.clear_inputs()
        self._show_message("입력 완료", f"새 상품이 추가되었습니다. ID: {new_id}")

    def update_product(self) -> None:
        if self.current_selected_id is None:
            self._show_error("수정 오류", "수정할 행을 먼저 선택하세요.")
            return

        try:
            name, price = self._get_name_and_price()
            updated = self.db.update_product(self.current_selected_id, name, price)
        except ValueError as exc:
            self._show_error("입력 오류", str(exc))
            return
        except sqlite3.Error as exc:
            self._show_error("DB 오류", str(exc))
            return

        if not updated:
            self._show_error("수정 실패", "선택한 데이터를 찾을 수 없습니다.")
            return

        self._load_table()
        self._show_message("수정 완료", "상품 정보가 수정되었습니다.")

    def delete_product(self) -> None:
        if self.current_selected_id is None:
            self._show_error("삭제 오류", "삭제할 행을 먼저 선택하세요.")
            return

        reply = QMessageBox.question(
            self,
            "삭제 확인",
            f"ID {self.current_selected_id} 상품을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            deleted = self.db.delete_product(self.current_selected_id)
        except sqlite3.Error as exc:
            self._show_error("DB 오류", str(exc))
            return

        if not deleted:
            self._show_error("삭제 실패", "선택한 데이터를 찾을 수 없습니다.")
            return

        self._load_table()
        self.clear_inputs()
        self._show_message("삭제 완료", "상품이 삭제되었습니다.")

    def search_product(self) -> None:
        keyword = self.name_edit.text().strip()
        if not keyword:
            keyword = self.id_edit.text().strip()

        try:
            rows = self.db.search_products(keyword)
        except sqlite3.Error as exc:
            self._show_error("DB 오류", str(exc))
            return

        self._load_table(rows)
        if rows:
            self._show_message("검색 완료", f"{len(rows)}건을 찾았습니다.")
        else:
            self._show_message("검색 결과", "검색된 데이터가 없습니다.")

    def clear_inputs(self) -> None:
        self.current_selected_id = None
        self.id_edit.clear()
        self.name_edit.clear()
        self.price_edit.clear()
        self.table.clearSelection()
        self._load_table()

    def on_row_clicked(self, row: int, column: int) -> None:  # noqa: ARG002
        item_id = self.table.item(row, 0)
        item_name = self.table.item(row, 1)
        item_price = self.table.item(row, 2)

        if not item_id or not item_name or not item_price:
            return

        self.current_selected_id = int(item_id.text())
        self.id_edit.setText(item_id.text())
        self.name_edit.setText(item_name.text())
        self.price_edit.setText(item_price.text().replace(",", ""))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BicycleProductManager()
    window.show()
    sys.exit(app.exec())
