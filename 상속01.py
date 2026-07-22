#부모 클래스(공통 코드)
class Person:
    def __init__(self, name, phoneNumber):
        self.name = name
        self.phoneNumber = phoneNumber
    def printInfo(self):
        print("Info(Name:{0}, Phone Number: {1})".format(self.name, self.phoneNumber))
    def working(self):
        print("일을 합니다.")

#자식 클래스(약간 더 특화)
class Student(Person):
    #덮어쓰기(재정의, override해~~) => 마라탕
    def __init__(self, name, phoneNumber, subject, studentID):
        #부모 초기화 메서드 호출
        super().__init__(name, phoneNumber)
        self.subject = subject
        self.studentID = studentID
    #상속받고 덮어쓰기(재정의)
    def printInfo(self):
        print("Info(Name:{0}, Phone Number: {1}, Subject: {2}, Student ID: {3})"
            .format(self.name, self.phoneNumber, self.subject, self.studentID))

p = Person("전우치", "010-222-1234")
s = Student("이순신", "010-111-1234", "인공지능", "26123")
p.printInfo()
s.printInfo()
s.working()

