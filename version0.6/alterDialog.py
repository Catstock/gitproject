import os
import shutil
import subprocess
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *
import Camera

class alterPaDialog(QDialog):
    add_pa_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(alterPaDialog, self).__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("患者信息")
        self.save_clicked = False  # 添加一个布尔型变量

    def setUpUI(self):
        genderCategory = ["男", "女"]
        self.resize(1000, 800)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # 滚动条
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollWidget = QWidget()
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout.addWidget(self.scrollArea)

        self.temp_alter_no="11"
        # Label控件
        self.titlelabel = QLabel("患者信息")
        self.paNameLabel = QLabel("姓    名:")
        self.birthLabel = QLabel("出生日期:")
        self.genderLabel = QLabel("性    别:")
        self.IdLabel = QLabel("身份证号:")
        self.historyLabel = QLabel("病    史:")
        self.paImageLabel = QLabel("照    片:")
        self.pixmap_path=""
        self.picsize = 300
        self.pixmap = QPixmap('E:\code\gitproject\PyQt-Sqlite-Project-CURD-master\pa_head\pa_1\\000000.jpg')
        self.pixmap = self.pixmap.scaled(self.picsize, self.picsize, aspectRatioMode=Qt.KeepAspectRatio)

        # 创建一个QLabel对象并设置图片
        self.picLabel = QLabel()
        self.picLabel.setPixmap(self.pixmap)

        # 显示标签
        self.picLabel.show()

        # button控件
        self.alterBtn = QPushButton("确认修改")
        self.alterPicBtn = QPushButton("拍照")

        # lineEdit控件
        self.paNameEdit = QLineEdit()
        self.IdEdit = QLineEdit()
        self.historyEdit = QLineEdit()
        self.genderComboBox = QComboBox()
        self.genderComboBox.addItems(genderCategory)
        self.paImageEdit = QLineEdit()
        self.paImageEdit.setEnabled(False)
        self.birthTime = QDateTimeEdit()
        self.birthTime.setDisplayFormat("yyyy-MM-dd")        # self.birthEdit = QLineEdit()

        self.paNameEdit.setMaxLength(10)
        self.IdEdit.setMaxLength(18)
        self.paImageEdit.setMaxLength(255)
        #录音相关
        from standard_audio import StandardAudioRecorder
        self.audiorecorder = StandardAudioRecorder()
        self.audiorecorder.alterstr_clicked.connect(self.set_new_audio)
        self.audiorecorder.hide_generate_btn()
        self.audiorecorder.show_patient_notice()
        self.new_audio=0

        # 添加进formlayout
        self.formlayout=QFormLayout()
        self.scrollWidget.setLayout(self.formlayout)
        self.formlayout.addRow("", self.titlelabel)
        self.formlayout.addRow(self.paNameLabel, self.paNameEdit)
        self.formlayout.addRow(self.IdLabel, self.IdEdit)
        self.formlayout.addRow(self.historyLabel, self.historyEdit)
        self.formlayout.addRow(self.genderLabel, self.genderComboBox)
        self.formlayout.addRow(self.paImageLabel, self.paImageEdit)
        self.formlayout.addRow(self.picLabel)
        self.formlayout.addRow(self.birthLabel, self.birthTime)
        self.formlayout.addRow("", self.alterPicBtn)
        self.formlayout.addRow("患者声音：", self.audiorecorder)
        self.formlayout.addRow("", self.alterBtn)
        self.checkdocBtn=QPushButton("查看训练日志")
        self.checkdocBtn.clicked.connect(self.checkdocBtnClicked)
        self.formlayout.addRow("", self.checkdocBtn)

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
        self.alterBtn.setFont(font)
        self.alterBtn.setFixedHeight(32)
        self.alterBtn.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)
        self.formlayout.setVerticalSpacing(10)

        self.alterPicBtn.clicked.connect(self.alterPicBtnClicked)
        self.alterBtn.clicked.connect(self.alterBtnClicked)

    def checkdocBtnClicked(self):
        # 要打开的docx文件路径
        file_path = 'pa_train/pa_'+str(self.temp_alter_no)+'/output.docx'
        # 检查文件是否存在
        if os.path.isfile(file_path):
            # 根据系统设置确定默认应用程序
            if os.name == 'nt':
                # Windows系统下使用start命令打开文件
                subprocess.call(['start', file_path], shell=True)
            elif os.name == 'posix':
                # MacOS或Linux系统下使用open命令打开文件
                subprocess.call(['open', file_path])
            else:
                # 其他操作系统，你可以根据系统类型自己进行处理
                pass
        else:
            # 使用QMessageBox弹出错误消息
            error_message = '文件不存在'
            QMessageBox.critical(None, '错误', error_message, QMessageBox.Ok)

    # 将录制的音频放到指定文件夹
    def transAudio(self):
        try:
            # 目标文件夹
            source_path = "audio"
            audio_name = "temp_save_audio.mp3"
            target_path = "pa_audio/pa"+str(self.temp_alter_no)
            new_name = "pa"+str(self.temp_alter_no)+".mp3"
            if not os.path.exists(os.path.join(source_path, audio_name)):
                print(QMessageBox.warning(self, "警告", "请选择一条音频", QMessageBox.Yes, QMessageBox.Yes))

            if not os.path.exists(target_path):
                os.makedirs(target_path)  # 如果文件夹不存在，则创建文件夹
            if os.path.exists(os.path.join(source_path, new_name)):
                os.remove(os.path.join(source_path, new_name))
            # 将音频重命名为new_name
            os.rename(os.path.join(source_path, audio_name), os.path.join(source_path, new_name))
            # 将音频复制到目标路径下，source_path包含文件名及后缀名，video_name是其中分离出的文件名
            shutil.move(os.path.join(source_path, new_name), os.path.join(target_path, new_name))
        except Exception as e:
            print(f'Error: {e}')

    def set_new_audio(self):
        self.new_audio=1

    # 展示原本的患者信息
    def fillContent(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT * FROM patient WHERE pa_no='%s'" % (self.temp_alter_no)
        print(self.temp_alter_no)
        query.exec_(sql)
        if (query.next()):
            print("打印："+query.value(1))
            self.paNameEdit.setText(query.value(1))
            self.IdEdit.setText(query.value(4))
            self.historyEdit.setText(query.value(5))
            self.genderComboBox.setCurrentText(query.value(2))
            self.paImageEdit.setText(query.value(6))
            self.pixmap=QPixmap(query.value(6))
            self.pixmap_path=query.value(6)
            self.pixmap = self.pixmap.scaled(self.picsize, self.picsize, aspectRatioMode=Qt.KeepAspectRatio)
            self.picLabel.setPixmap(self.pixmap)
            temp_list= str(query.value(3)).split('-')
            self.birthTime.setDate(QDate(int(temp_list[0]),int(temp_list[1]),int(temp_list[2])))
            pa_audio_path="pa_audio/pa"+str(self.temp_alter_no)+"/"+"pa"+str(self.temp_alter_no)+".mp3"
            if os.path.exists(pa_audio_path):
                self.audiorecorder.set_file_path(pa_audio_path)
            else:
                temp_path="audio/temp_save_audio.mp3"
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                self.audiorecorder.play_button.setEnabled(False)
            return
            # 提示已存在
        else:
            print(QMessageBox.warning(self, "警告", "该患者不存在", QMessageBox.Yes, QMessageBox.Yes))
        # query.exec_(sql)
        db.commit()

    def setNo(self,no_value):
        self.temp_alter_no=str(no_value)

    def alterBtnClicked(self):
        paName = self.paNameEdit.text()
        paId = self.IdEdit.text()
        history = self.historyEdit.text()
        genderCategory = self.genderComboBox.currentText()
        paImage = "pa_head/pa_"+str(self.temp_alter_no)+"/000000.jpg"
        # paImage =self.paImageEdit.text()
        birthTime = self.birthTime.text()
        if (
                paName == "" or paId == "" or history == "" or genderCategory == "" or paImage == "" or birthTime == ""):
            print(QMessageBox.warning(self, "警告", "有字段为空，修改失败", QMessageBox.Yes, QMessageBox.Yes))
            return
        else:
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName('database.db')
            db.open()
            query = QSqlQuery()
            sql = "UPDATE patient SET pa_name='%s',pa_id='%s',pa_history='%s',pa_gender='%s',pa_photo='%s',pa_age='%s' WHERE pa_no='%s'" % (
                paName, paId, history, genderCategory, paImage, birthTime,self.temp_alter_no)
            if not query.exec_(sql):
                print(QMessageBox.warning(self, "警告", "该患者已存在!", QMessageBox.Yes, QMessageBox.Yes))
                return
            db.commit()
            if self.new_audio==1:
                self.transAudio()
                self.new_audio=0
            print(QMessageBox.information(self, "提示", "修改成功!", QMessageBox.Yes, QMessageBox.Yes))
            self.add_pa_success_signal.emit()
            self.save_clicked = True  # 设置 save_clicked 为 True
            self.close()  # 关闭窗口
            self.clearEdit()  # 清除输入框内容
            self.save_clicked = False  # 重置 save_clicked 为 False
        return

    def alterPicBtnClicked(self):
        self.hide()
        from Camera import CameraWindow
        camera_window = CameraWindow(self,self.temp_alter_no)
        camera_window.set_main_window(self)
        camera_window.show()
        # 在主窗口B中进行拍照
        # ...

        # 关闭主窗口B并返回对话框A
        #camera_window.close()
        #self.show()

    def clearEdit(self):
        self.paNameEdit.clear()
        self.IdEdit.clear()
        self.historyEdit.clear()
        self.paImageEdit.clear()

    def showEvent(self, event):
        # 在对话框再次显示时触发的函数
        if self.pixmap_path!="":
            self.pixmap = QPixmap(self.pixmap_path)
            self.pixmap = self.pixmap.scaled(self.picsize, self.picsize, aspectRatioMode=Qt.KeepAspectRatio)
            self.picLabel.setPixmap(self.pixmap)
        event.accept()

    def closeEvent(self, event):
        if not self.save_clicked:
            reply = QMessageBox.question(self, '提示', '是否要保存修改？',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.alterBtnClicked()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = alterPaDialog()
    mainMindow.show()
    sys.exit(app.exec_())