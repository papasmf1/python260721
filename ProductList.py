import sqlite3
from typing import List, Optional, Tuple


class ProductDB:
    def __init__(self, db_name: str = "MyProduct.db") -> None:
        self.db_name = db_name
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_name)

    def _create_table(self) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS Products (
                    productID INTEGER PRIMARY KEY,
                    productName TEXT NOT NULL,
                    productPrice INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def insert_product(self, product_id: int, product_name: str, product_price: int) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                (product_id, product_name, product_price),
            )
            conn.commit()

    def insert_many_products(self, products: List[Tuple[int, str, int]]) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
                products,
            )
            conn.commit()

    def update_product(
        self,
        product_id: int,
        product_name: Optional[str] = None,
        product_price: Optional[int] = None,
    ) -> bool:
        fields = []
        values = []

        if product_name is not None:
            fields.append("productName = ?")
            values.append(product_name)
        if product_price is not None:
            fields.append("productPrice = ?")
            values.append(product_price)

        if not fields:
            return False

        values.append(product_id)
        query = f"UPDATE Products SET {', '.join(fields)} WHERE productID = ?"

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def select_product(self, product_id: int) -> Optional[Tuple[int, str, int]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
                (product_id,),
            )
            return cursor.fetchone()

    def select_all_products(self) -> List[Tuple[int, str, int]]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT productID, productName, productPrice FROM Products ORDER BY productID")
            return cursor.fetchall()

    def count_products(self) -> int:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Products")
            return cursor.fetchone()[0]

    def clear_products(self) -> None:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Products")
            conn.commit()

    def seed_sample_data(self, count: int = 1000, reset: bool = True) -> None:
        # 중복 ID 에러를 피하기 위해 기본값으로 기존 데이터를 지우고 다시 채운다.
        if reset:
            self.clear_products()

        products = []
        for i in range(1, count + 1):
            name = f"전자제품_{i:04d}"
            price = 10000 + (i * 250)
            products.append((i, name, price))

        self.insert_many_products(products)


if __name__ == "__main__":
    db = ProductDB("MyProduct.db")

    # 1) 샘플 데이터 1000건 생성
    db.seed_sample_data(1000, reset=True)
    print(f"샘플 데이터 생성 완료: {db.count_products()}건")

    # 2) INSERT 예시
    db.insert_product(1001, "전자제품_추가", 555000)
    print("INSERT 결과:", db.select_product(1001))

    # 3) UPDATE 예시
    updated = db.update_product(1001, product_name="전자제품_수정", product_price=777000)
    print("UPDATE 성공 여부:", updated)
    print("UPDATE 결과:", db.select_product(1001))

    # 4) SELECT 예시
    first_five = db.select_all_products()[:5]
    print("SELECT 상위 5건:", first_five)

    # 5) DELETE 예시
    deleted = db.delete_product(1001)
    print("DELETE 성공 여부:", deleted)
    print("최종 데이터 건수:", db.count_products())
