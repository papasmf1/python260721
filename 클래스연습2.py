# 클래스연습2.py

# Person은 사람을 나타내는 기본 클래스예요.
# 사람이라면 누구나 가지고 있는 id와 name을 담아 둡니다.
class Person:
    # __init__은 새 객체가 만들어질 때 자동으로 실행되는 준비 함수예요.
    # id는 번호, name은 이름을 뜻해요.
    def __init__(self, id, name):
        self.id = id
        self.name = name

    # printInfo()는 이 사람의 정보를 화면에 보여주는 함수예요.
    def printInfo(self):
        print("Info(ID:{0}, Name:{1})".format(self.id, self.name))


# Manager는 Person을 물려받은 클래스예요.
# 즉, 사람의 기본 정보에 더해서 title이라는 직책 정보가 하나 더 있어요.
class Manager(Person):
    def __init__(self, id, name, title):
        # 부모 클래스인 Person의 준비 함수를 먼저 사용해서 id와 name을 넣어요.
        super().__init__(id, name)
        # Manager만 따로 가지는 추가 정보예요.
        self.title = title

    # Manager는 기본 사람 정보에 title까지 함께 보여줘요.
    def printInfo(self):
        print("Info(ID:{0}, Name:{1}, Title:{2})".format(self.id, self.name, self.title))


# Employee도 Person을 물려받은 클래스예요.
# 사람의 기본 정보에 더해서 skill이라는 기술 정보를 하나 더 가져요.
class Employee(Person):
    def __init__(self, id, name, skill):
        # 부모 클래스의 id와 name을 먼저 넣어요.
        super().__init__(id, name)
        # Employee만 따로 가지는 추가 정보예요.
        self.skill = skill

    # Employee는 기본 사람 정보에 skill까지 함께 보여줘요.
    def printInfo(self):
        print("Info(ID:{0}, Name:{1}, Skill:{2})".format(self.id, self.name, self.skill))


# people 리스트는 사람들, 매니저들, 직원들을 한 번에 담아 놓은 상자예요.
# 이렇게 해 두면 아래에서 하나씩 꺼내며 같은 방법으로 출력할 수 있어요.
people = [
    Person(1, "홍길동"),
    Manager(2, "이순신", "팀장"),
    Employee(3, "강감찬", "Python"),
    Person(4, "유관순"),
    Manager(5, "김유신", "부장"),
    Employee(6, "장보고", "Java"),
    Person(7, "전우치"),
    Manager(8, "신사임당", "과장"),
    Employee(9, "세종대왕", "C++"),
    Employee(10, "안중근", "AI")
]

# 리스트에 들어 있는 모든 사람을 하나씩 꺼내서 정보 출력 함수를 실행해요.
for person in people:
    person.printInfo()
