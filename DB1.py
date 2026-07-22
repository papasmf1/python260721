# db1.py 
import sqlite3
#연결객체 생성
con = sqlite3.connect(":memory:") # 메모리 DB 생성
#커서객체 생성
cur = con.cursor()
#테이블 생성
cur.execute("CREATE TABLE PhoneBook (Name text, PhoneNum text);")
#1건 입력 
cur.execute("INSERT INTO PhoneBook VALUES ('홍길동', '010-1234-5678');")
#입력 파라메터 처리
name = "전우치"
phoneNum = "010-222"
cur.execute("INSERT INTO PhoneBook VALUES (?, ?);", (name, phoneNum))
#여러건 입력
data = [("이순신", "010-333"), ("강감찬", "010-444")]
cur.executemany("INSERT INTO PhoneBook VALUES (?, ?);", data)

#검색
cur.execute("SELECT * FROM PhoneBook;")
#검색결과 출력
for row in cur:
    print(row)