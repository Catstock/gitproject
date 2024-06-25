import sys

from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QMainWindow, QWidget, QPushButton, QApplication


class TrainDialogue(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('训练报告')
        self.resize(600,800)
        self.layout = QVBoxLayout()
        self.text_edit = QTextEdit("")
        self.text_edit.setReadOnly(True)
        font=QFont()
        font.setPixelSize(30)
        self.text_edit.setFont(font)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

        # 将分数和文本添加到弹窗中
        for i, (ques,score, text) in enumerate(zip(parent.ques_list,parent.score_list, parent.text_list)):
            self.text_edit.insertHtml(f"{ques}<br>{score}<br>{text}<br><br>")

        # 将光标移动到文本末尾
        self.text_edit.moveCursor(QTextCursor.End)

class MWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ques_list=['张三是大学老师','张三是大学老师']
        self.score_list = ['86分，很棒！', '75分，继续努力']
        self.text_list = ['<font color="red"><b>'+'张三'+'</b></font>'+'是大学老师','张三'+'<font color="red"><b>'+'是大学老师'+'</b></font>']

        # 创建UI界面
        self.setWindowTitle('Train Window')
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.mission_btn = QPushButton('Mission Completed', self.central_widget)
        self.mission_btn.clicked.connect(self.show_dialogue)
    def show_dialogue(self):
        try:
            dialogue=TrainDialogue(self)
            dialogue.show()
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MWindow()
    window.show()
    sys.exit(app.exec_())

