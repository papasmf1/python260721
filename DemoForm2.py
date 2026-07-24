# DemoForm2.py 
# DemoForm2.ui(화면을 저장) + DemoForm2.py(로직을 저장)
import sys 
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt6 import uic
#웹크롤링을 위한 라이브러리 
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request 
#특정 문자열을 검색하기 위한 정규표현식
import re 


#디자인 파일 로딩
form_class = uic.loadUiType("DemoForm2.ui")[0]

#DemoForm 클래스 정의(부모 클래스 => QMainWindow)
class DemoForm(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    #슬롯메서드연결
    def firstClick(self):
        hdr = {'User-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.23 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1'}
        f = open("clien.txt", "wt", encoding="utf-8")
        for i in range(0,10):
            url = "https://www.clien.net/service/board/sold?&od=T31&category=0&po=" + str(i)
            req = urllib.request.Request(url, headers=hdr)
            data = urllib.request.urlopen(req).read()
            soup = BeautifulSoup(data, 'html.parser')
            lst = soup.find_all('span', attrs={'data-role':'list-title-text'})
            for tag in lst:
                title = tag.text.strip()
                #원하는 매물만 검색
                if (re.search('아이폰', title)):
                    print(title)
                    f.write(title + "\n")

        f.close() 
        self.label.setText("클리앙 중고장터 크롤링 완료")
    def secondClick(self):
        self.label.setText("두번째 버튼 클릭")
    def thirdClick(self):
        self.label.setText("세번째 버튼 클릭")


#직접 모듈을 실행했는지 체크 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demoWindow = DemoForm()
    demoWindow.show()
    sys.exit(app.exec())