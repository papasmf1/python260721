# 클래스연습.py 
#1)클래스 정의
class Person: 
    #초기화 메서드
    def __init__(self):
        self.name = "default name"
    def printInfo(self):
        print("My name is {0}".format(self.name))

#2)인스턴스 사용
p1 = Person() #인스턴스 생성
p2 = Person() #인스턴스 생성
p2.name = "전우치"

#3)메서드호출
p1.printInfo() #메서드 호출
p2.printInfo() #메서드 호출