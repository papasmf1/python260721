#웹크롤링
from bs4 import BeautifulSoup

#페이지를 로딩(rt: read text)
page = open("Chap09_test.html", "rt", encoding="utf-8")

#검색이 용이한 객체
soup = BeautifulSoup(page, "html.parser")
#print(soup.prettify()) #html 문서를 보기 좋게 출력
#<p>태그를 몽땅 검색
#print(soup.find_all("p")) #리스트로 반환
#첫번째<p>태그를 검색
#print(soup.find("p")) #첫번째 <p>태그만 반환
#<p class="outer-text">태그를 검색
#print(soup.find_all("p", class_="outer-text"))
# attrs속성 더 많이 사용 
#print(soup.find_all("p", attrs={"class": "outer-text"}))

#태그 내부에 문자열만 추출
#<p>  문자열  </p>
#파일에 저장(mode값을 "wt"로 설정 => write text)
f = open("demo.txt", "wt", encoding="utf-8")
for item in soup.find_all("p"): 
    title = item.text.strip() 
    #치환
    title = title.replace("\n", "")
    print(title)
    f.write(title + "\n")

f.close()

