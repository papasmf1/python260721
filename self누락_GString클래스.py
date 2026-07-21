#전역변수 
strName = "Not Class Member"

#클래스 정의 
class DemoString:
    def __init__(self):
        #인스턴스 멤버 변수 
        self.strName = "" 
    def set(self, msg):
        self.strName = msg
    def print(self):
        #명확하게 지정 
        print(self.strName)

d = DemoString()
d.set("First Message")
d.print()
