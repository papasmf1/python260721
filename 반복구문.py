# 반복구문.py

value = 5 
while value > 0:
    print(value)
    value -= 1

print("---for in루프---")
lst = [10, 20, 30]
for item in lst:
    print(item)

#탭으로 코딩하기 
d = {"성함":"홍길동", "나이": 20, "주소": "서울시"}
for item in d.items():
    print(item)

#수열함수
print("---range함수---")
print( list(range(10)) )
print( list(range(1,11)) )
print( list(range(2000, 2027)) )
print( list(range(1,32)) )

#리스트 컴프리헨션(함축)
lst = list(range(1, 11))
print( [i**2 for i in lst if i>5] )

colors = {100:"kiwi", 200:"banana", 300:"mango"}
print( [v.upper() for v in colors.values()] )


