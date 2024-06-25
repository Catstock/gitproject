import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *


class addPaDialog(QDialog):
    add_pa_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(addPaDialog, self).__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("添加患者")

    def setUpUI(self):
        # 书名，书号，作者，分类，添加数量.出版社,出版日期
        # 书籍分类：哲学类、社会科学类、政治类、法律类、军事类、经济类、文化类、教育类、体育类、语言文字类、艺术类、历史类、地理类、天文学类、生物学类、医学卫生类、农业类
        genderCategory = ["男", "女"]
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # Label控件
        self.titlelabel = QLabel("  添加患者")
        self.paNameLabel = QLabel("姓    名:")
        self.birthLabel = QLabel("出生日期:")
        self.genderLabel = QLabel("性    别:")
        self.IdLabel = QLabel("身份证号:")
        self.historyLabel = QLabel("病    史:")
        self.paImageLabel = QLabel("照    片:")

        # button控件
        self.addBtn = QPushButton("添 加")

        # lineEdit控件
        self.paNameEdit = QLineEdit()
        self.IdEdit = QLineEdit()
        self.historyEdit = QLineEdit()
        self.genderComboBox = QComboBox()
        self.genderComboBox.addItems(genderCategory)
        self.paImageEdit = QLineEdit()
        self.paImageEdit.setText("请稍后在*查看*界面进行拍照")
        self.paImageEdit.setEnabled(False)
        self.birthTime = QDateTimeEdit()
        self.birthTime.setDisplayFormat("yyyy-MM-dd")
        # self.birthEdit = QLineEdit()

        self.paNameEdit.setMaxLength(10)
        self.IdEdit.setMaxLength(18)
        self.paImageEdit.setMaxLength(255)

        # 添加进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.paNameLabel, self.paNameEdit)
        self.layout.addRow(self.IdLabel, self.IdEdit)
        self.layout.addRow(self.historyLabel, self.historyEdit)
        self.layout.addRow(self.genderLabel, self.genderComboBox)
        self.layout.addRow(self.paImageLabel, self.paImageEdit)
        self.layout.addRow(self.birthLabel, self.birthTime)
        self.layout.addRow("", self.addBtn)

        # 设置字体
        font = QFont()
        font.setPixelSize(20)
        self.titlelabel.setFont(font)
        font.setPixelSize(14)
        self.paNameLabel.setFont(font)
        self.IdLabel.setFont(font)
        self.historyLabel.setFont(font)
        self.genderLabel.setFont(font)
        self.paImageLabel.setFont(font)
        self.birthLabel.setFont(font)

        self.paNameEdit.setFont(font)
        self.IdEdit.setFont(font)
        self.historyEdit.setFont(font)
        self.paImageEdit.setFont(font)
        self.birthTime.setFont(font)
        self.genderComboBox.setFont(font)

        # button设置
        font.setPixelSize(16)
        self.addBtn.setFont(font)
        self.addBtn.setFixedHeight(32)
        self.addBtn.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)
        self.layout.setVerticalSpacing(10)

        self.addBtn.clicked.connect(self.addBtnCicked)

    def addBtnCicked(self):
        paName = self.paNameEdit.text()
        paId = self.IdEdit.text()
        history = self.historyEdit.text()
        genderCategory = self.genderComboBox.currentText()
        paImage = ""
        birthTime = self.birthTime.text()
        if (
                paName == "" or paId == "" or history == "" or genderCategory == "" or birthTime == ""):
            print(QMessageBox.warning(self, "警告", "有字段为空，添加失败", QMessageBox.Yes, QMessageBox.Yes))
            return
        else:
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName('database.db')
            db.open()
            query = QSqlQuery()
            # 如果已存在，则update Book表的现存量，剩余可借量，不存在，则insert Book表，同时insert buyordrop表
            sql = "SELECT * FROM patient WHERE pa_id='%s'" % (paId)
            query.exec_(sql)
            if (query.next()):
                print(QMessageBox.warning(self, "警告", "该患者已存在", QMessageBox.Yes, QMessageBox.Yes))
                return
                # 提示已存在
            else:
                sql = "INSERT INTO patient(pa_name,pa_id,pa_history,pa_gender,pa_photo,pa_age) VALUES ('%s','%s','%s','%s','%s','%s')" % (
                    paName, paId, history, genderCategory, paImage, birthTime)
            query.exec_(sql)
            db.commit()
            print(QMessageBox.information(self, "提示", "添加患者成功!", QMessageBox.Yes, QMessageBox.Yes))
            self.add_pa_success_signal.emit()
            self.close()
            self.clearEdit()
        return

    def clearEdit(self):
        self.paNameEdit.clear()
        self.IdEdit.clear()
        self.historyEdit.clear()
        self.paImageEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = addPaDialog()
    mainMindow.show()
    sys.exit(app.exec_())