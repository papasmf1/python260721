# 함수연습.py
x = 5 

#함수 정의
def func(a):
    return a+x 

#함수 호출
print(func(1))

#함수 정의
def func2(a):
    x = 10 
    return a+x 

#호출
print(func2(1))

#리턴없음
def setValue(newValue):
    x = newValue
    print("현재값:", x)

result = setValue(1)
print(result)

#여러개 리턴
def swap(x,y):
    return y,x 

result = swap(3,4)
print(result)