# web2.py 
#클리앙의 중고장터를 크롤링 
#웹크롤링을 위한 라이브러리 
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request 
#특정 문자열을 검색하기 위한 정규표현식
import re 

#User-Agent를 조작하는 경우(아이폰에서 사용하는 사파리 브라우져의 헤더) 
hdr = {'User-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.23 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'}

#파일에 저장 
f = open("clien.txt", "wt", encoding="utf-8")
#페이징처리 추가
for i in range(0,10):
    url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po=" + str(i)
    print(url)
    #웹브라우져의 헤더를 추가 
    req = urllib.request.Request(url, headers=hdr)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, 'html.parser')
    lst = soup.find_all('span', attrs={'data-role':'list-title-text'})
    for tag in lst:
        title = tag.text.strip()
        print(title)
        f.write(title + "\n")

f.close() 
print("저장완료")
    
#선택한 영역을 주석처리: ctrl + / 
# <span class="subject_fixed" data-role="list-title-text" title="맥미니 m4 16g 256g 팝니다">
# 		맥미니 m4 16g 256g 팝니다
# </span>