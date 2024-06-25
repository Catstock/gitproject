import os
import shutil
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *


class addsentenceDialog(QDialog):
    add_sentence_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(addsentenceDialog, self).__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("添加句子")

    def setUpUI(self):
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # 标题
        self.titlelabel = QLabel("添加句子")
        # 内容
        self.sentenceNameLabel = QLabel("句子名:")
        self.audio_path_label = QLabel("音频文件:")
        # lineEdit控件
        self.strNameEdit = QLineEdit()
        self.strNameEdit.setMaxLength(10)

        # 录音相关
        from standard_audio import StandardAudioRecorder
        self.vbox = QVBoxLayout()
        self.audiorecorder = StandardAudioRecorder()
        self.audiorecorder.generate_clicked.connect(self.setAudioText)
        self.audiorecorder.audio_clicked.connect(self.setGenerateLabel)
        self.vbox.addWidget(self.audiorecorder)

        self.audiopack_widget = QWidget()
        self.audiopack_widget.setLayout(self.vbox)

        self.generate_label = QLabel("尚未选择音频")
        # 提交
        self.addBtn = QPushButton("添 加")
        self.addBtn.clicked.connect(self.addBtnClicked)

        # 添加进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.sentenceNameLabel, self.strNameEdit)
        self.layout.addRow(self.audio_path_label, self.audiopack_widget)
        self.layout.addRow("", self.generate_label)
        self.layout.addRow("", self.addBtn)

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
        self.addBtn.setFont(font)
        self.addBtn.setFixedHeight(32)
        self.addBtn.setFixedWidth(140)

        # 设置间距
        self.titlelabel.setMargin(8)

    def addBtnClicked(self):
        try:
            sentenceName = self.strNameEdit.text()

            if (sentenceName == ""):
                print(QMessageBox.warning(self, "警告", "有字段为空，添加失败", QMessageBox.Yes, QMessageBox.Yes))
                return
            elif not os.path.exists("audio/temp_save_audio.mp3"):
                print(QMessageBox.warning(self, "警告", "请选择一条音频", QMessageBox.Yes, QMessageBox.Yes))
                return
            else:
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName('database.db')
                db.open()
                query = QSqlQuery()
                # 如果已存在，则update Book表的现存量，剩余可借量，不存在，则insert Book表，同时insert buyordrop表
                sql = "SELECT * FROM sentence WHERE sentence_name='%s'" % (sentenceName)
                query.exec_(sql)
                if (query.next()):
                    print(QMessageBox.warning(self, "警告", "句子名已存在", QMessageBox.Yes, QMessageBox.Yes))
                    return
                # 分两步，1保存并获取自增编号，2修改音频路径
                sql = "INSERT INTO sentence(sentence_name,sentence_audio) VALUES ('%s','%s')" % (
                    sentenceName, "audio_path")
                if not query.exec_(sql):
                    error = query.lastError()
                    print(f"Error executing query: {error.text()}")
                db.commit()
                query.exec_("SELECT last_insert_rowid();")
                print(query.next())
                # 得知自增编号
                new_sentence_id = query.value(0)
                sentenceAudio = "audio/sentence/" + str(new_sentence_id) + ".mp3"
                sql = "UPDATE sentence SET sentence_audio='%s' WHERE sentence_no=%d" % (sentenceAudio, new_sentence_id)
                query.exec_(sql)
                db.commit()
                target_path = "audio/sentence"
                new_name = str(new_sentence_id) + ".mp3"
                self.transAudio(target_path, new_name)  # 将save_temp_audio.mp3改名并剪切到目标路径
                print(QMessageBox.information(self, "提示", "添加句子成功!", QMessageBox.Yes, QMessageBox.Yes))
                self.add_sentence_success_signal.emit()
                self.close()
                self.clearEdit()
            return
        except Exception as e:
            print(f'Error: {e}')

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = addsentenceDialog()
    mainMindow.show()
    sys.exit(app.exec_())