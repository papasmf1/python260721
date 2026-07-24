# DemoForm.py 
# DemoForm.ui(화면을 저장) + DemoForm.py(로직을 저장)
import sys 
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6 import uic

#디자인 파일 로딩
form_class = uic.loadUiType("DemoForm.ui")[0]

#DemoForm 클래스 정의
class DemoForm(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.label.setText("안녕하세요 PyQt")

#직접 모듈을 실행했는지 체크 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demoWindow = DemoForm()
    demoWindow.show()
    sys.exit(app.exec())