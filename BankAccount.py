# BankAccount.py

#은행의 계정을 표현한 클래스 
class BankAccount:
    #초기화 메서드 
    def __init__(self, id, name, balance):
        #인스턴스 멤버 변수(내부에 숨겨달라 부탁) 
        self.__id = id
        self.__name = name 
        self.__balance = balance 
    def deposit(self, amount):
        self.__balance += amount 
    def withdraw(self, amount):
        self.__balance -= amount
    #지금 인스턴스 상태를 문자열 리턴 
    def __str__(self):
        return "{0} , {1} , {2}".format(self.__id, self.__name, self.__balance)

#인스턴스 객체를 생성
account1 = BankAccount(100, "전우치", 15000)
account1.deposit(5000)
account1.withdraw(3000)
print(account1)

#외부에서 접근(인스턴스)
#print(account1.__balance) 
#테스트 코드
#print(account1._BankAccount__balance) #이렇게 접근 가능하지만 권장하지 않음 
