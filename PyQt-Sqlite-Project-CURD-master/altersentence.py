import os
import shutil
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *


class altersentenceDialog(QDialog):
    alter_sentence_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("修改句子")

    def setUpUI(self):
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.sentence_no = ""
        self.old_name = ""
        self.new_audio=False
        # 标题
        self.titlelabel = QLabel("修改句子")
        # 内容
        self.sentenceNameLabel = QLabel("句子名:")
        self.audio_path_label = QLabel("音频文件:")
        # lineEdit控件
        self.strNameEdit = QLineEdit()

        # 录音相关
        from standard_audio import StandardAudioRecorder
        self.vbox = QVBoxLayout()
        self.audiorecorder = StandardAudioRecorder()
        self.audiorecorder.generate_clicked.connect(self.setAudioText)
        self.audiorecorder.audio_clicked.connect(self.setGenerateLabel)
        self.audiorecorder.alterstr_clicked.connect(self.setNewAudio)
        self.vbox.addWidget(self.audiorecorder)

        self.audiopack_widget = QWidget()
        self.audiopack_widget.setLayout(self.vbox)

        self.generate_label = QLabel("原音频路径：")
        # 提交
        self.alterBtn = QPushButton("添 加")
        self.alterBtn.clicked.connect(self.alterBtnClicked)

        # 修改进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.sentenceNameLabel, self.strNameEdit)
        self.layout.addRow(self.audio_path_label, self.audiopack_widget)
        self.layout.addRow("", self.generate_label)
        self.layout.addRow("", self.alterBtn)

        # 设置字体
        font = QFont()
        font.setPixelSize(20)
        self.titlelabel.setFont(font)
        font.setPixelSize(14)
        self.sentenceNameLabel.setFont(font)
        self.strNameEdit.setFont(font)
        self.audio_path_label.setFont(font)

        # button设置
        font.setPixelSize(16)
        self.alterBtn.setFont(font)
        self.alterBtn.setFixedHeight(32)
        self.alterBtn.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)

    def alterBtnClicked(self):
        try:
            sentenceName = self.strNameEdit.text()

            if (sentenceName == ""):
                print(QMessageBox.warning(self, "警告", "有字段为空，修改失败", QMessageBox.Yes, QMessageBox.Yes))
                return
            elif self.old_name != self.strNameEdit.text() and not self.new_audio:
                print(QMessageBox.warning(self, "警告", "请选择一条音频", QMessageBox.Yes, QMessageBox.Yes))
                return
            else:
                target_path = "audio/sentence"
                new_name = str(self.sentence_no) + ".mp3"
                self.transAudio(target_path, new_name)  # 将save_temp_audio.mp3改名并剪切到目标路径
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName('database.db')
                db.open()
                query = QSqlQuery()
                sql = "UPDATE sentence SET sentence_name='%s',sentence_audio='%s' WHERE sentence_no='%s'" % (
                    sentenceName,target_path+"/"+new_name, self.sentence_no)
                if not query.exec_(sql):
                    print(QMessageBox.warning(self, "警告", "该句子已存在!", QMessageBox.Yes, QMessageBox.Yes))
                    return
                db.commit()
                print(QMessageBox.information(self, "提示", "修改句子成功!", QMessageBox.Yes, QMessageBox.Yes))
                self.alter_sentence_success_signal.emit()
                self.close()
                self.clearEdit()
            return
        except Exception as e:
            print(f'Error: {e}')

    def fillContent(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT * FROM sentence WHERE sentence_no='%s'" % (self.sentence_no)
        query.exec_(sql)
        if (query.next()):
            self.old_name=query.value(1)
            self.strNameEdit.setText(query.value(1))
            self.audiorecorder.set_file_path(query.value(2))
            return
            # 提示已存在
        else:
            print(QMessageBox.warning(self, "警告", "该数据不存在", QMessageBox.Yes, QMessageBox.Yes))
        # query.exec_(sql)
        db.commit()

    def clearEdit(self):
        self.strNameEdit.clear()

    # 将temp_save_audio.mp3剪切到对应的音频文件夹下保存
    def transAudio(self, target_path, new_name):
        try:
            # 目标文件夹
            source_path = "audio"
            audio_name = "temp_save_audio.mp3"
            if not os.path.exists(os.path.join(source_path, audio_name)):
                print(QMessageBox.warning(self, "警告", "请选择一条音频", QMessageBox.Yes, QMessageBox.Yes))

            if not os.path.exists(target_path):
                os.makedirs(target_path)  # 如果文件夹不存在，则创建文件夹
            # 将音频重命名为new_name
            os.rename(os.path.join(source_path, audio_name), os.path.join(source_path, new_name))
            # 将音频复制到目标路径下，source_path包含文件名及后缀名，video_name是其中分离出的文件名
            shutil.move(os.path.join(source_path, new_name), os.path.join(target_path, new_name))
        except Exception as e:
            print(f'Error: {e}')

    def get_str_name_edit(self):
        return self.strNameEdit

    def setAudioText(self):
        self.audiorecorder.set_text_str(self.strNameEdit.text())

    def setGenerateLabel(self):
        self.generate_label.setText("已选中音频文件")

    def setNo(self,sentence_no):
        self.sentence_no=sentence_no
        self.generate_label.setText("原音频路径：audio/sentence/" + str(self.sentence_no) + ".mp3")

    def setNewAudio(self):
        self.new_audio=True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = altersentenceDialog()
    mainMindow.show()
    sys.exit(app.exec_())