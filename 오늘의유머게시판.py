# web2.py 
#오늘의 유머 베스트 게시판  
#웹크롤링을 위한 라이브러리 
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request 
#특정 문자열을 검색하기 위한 정규표현식
import re 

#User-Agent를 조작하는 경우(아이폰에서 사용하는 사파리 브라우져의 헤더) 
hdr = {'User-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.23 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'}

#파일에 저장 
f = open("todayHumor.txt", "wt", encoding="utf-8")
#페이징처리 추가(페이지 변경)
for i in range(1, 11):
    url = "https://www.todayhumor.co.kr/board/list.php?table=bestofbest&page=" + str(i)
    print(url)
    #웹브라우져의 헤더를 추가 
    req = urllib.request.Request(url, headers=hdr)
    data = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(data, 'html.parser')
    lst = soup.find_all('td', attrs={'class':'subject'})
    for tag in lst:
        #한번 더 <a>태그를 검색 
        title = tag.find("a").text.strip()
        #검색
        if (re.search('일본', title)):
            print(title)
            f.write(title + "\n")

f.close() 
print("저장완료")
    
#<td class="subject">
#  <a href="/board/view.php">치과에 충치치료받던 관우같은 아이</a>
#</td> 