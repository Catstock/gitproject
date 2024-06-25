import os
import shutil
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import time
from PyQt5.QtSql import *


class alterWordDialog(QDialog):
    alter_word_success_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUpUI()
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("修改词语")
        self.imagepath=""

    def setUpUI(self):
        self.resize(300, 400)
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.word_no = ""
        self.old_name=""
        self.new_audio=False
        # 标题
        self.titlelabel = QLabel("修改词语")
        # 内容
        self.wordNameLabel = QLabel("词语名:")
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
        self.audiorecorder.alterstr_clicked.connect(self.setNewAudio)
        self.vbox.addWidget(self.audiorecorder)

        self.audiopack_widget = QWidget()
        self.audiopack_widget.setLayout(self.vbox)

        self.generate_label = QLabel("原音频路径：")
        self.imageBtn = QPushButton("上传图片")  # 图片
        self.imageBtn.clicked.connect(self.imageBtnClicked)
        self.imagelabel = QLabel()
        # 提交
        self.alterBtn = QPushButton("添 加")
        self.alterBtn.clicked.connect(self.alterBtnClicked)

        # 修改进formlayout
        self.layout.addRow("", self.titlelabel)
        self.layout.addRow(self.wordNameLabel, self.strNameEdit)
        self.layout.addRow(self.audio_path_label, self.audiopack_widget)
        self.layout.addRow("", self.generate_label)
        self.layout.addRow("词语图片：", self.imageBtn)  # 图片
        self.layout.addRow("", self.imagelabel)
        self.layout.addRow("", self.alterBtn)

        # 设置字体
        font = QFont()
        font.setPixelSize(20)
        self.titlelabel.setFont(font)
        font.setPixelSize(14)
        self.wordNameLabel.setFont(font)
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
            wordName = self.strNameEdit.text()

            if (wordName == ""):
                print(QMessageBox.warning(self, "警告", "有字段为空，修改失败", QMessageBox.Yes, QMessageBox.Yes))
                return
            elif self.old_name != self.strNameEdit.text() and not self.new_audio:
                print(QMessageBox.warning(self, "警告", "请选择一条音频", QMessageBox.Yes, QMessageBox.Yes))
                return
            else:
                target_path = "audio/word"
                audio_name = str(self.word_no) + ".mp3"
                self.transAudio(target_path, audio_name)  # 将save_temp_audio.mp3改名并剪切到目标路径
                image_name = str(self.word_no) + ".jpg"
                if not self.imagepath=="":
                    self.copyImage(image_name)
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName('database.db')
                db.open()
                query = QSqlQuery()
                sql = "UPDATE words SET word_name='%s', word_audio='%s', word_image='%s' WHERE word_no='%s'" % (
                    wordName, target_path+"/"+audio_name, "image/"+image_name, self.word_no)
                if not query.exec_(sql):
                    print(QMessageBox.warning(self, "警告", "该词语已存在!", QMessageBox.Yes, QMessageBox.Yes))
                    return
                db.commit()
                print(QMessageBox.information(self, "提示", "修改词语成功!", QMessageBox.Yes, QMessageBox.Yes))
                self.alter_word_success_signal.emit()
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
        sql = "SELECT * FROM words WHERE word_no='%s'" % (self.word_no)
        query.exec_(sql)
        if (query.next()):
            self.old_name=query.value(1)
            self.strNameEdit.setText(query.value(1))
            self.audiorecorder.set_file_path(query.value(2))
            pixmap = QPixmap(query.value(3)) # 图片
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagelabel.setPixmap(scaled_pixmap)
            self.imagelabel.setScaledContents(True)
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

    def setNo(self,word_no):
        self.word_no=word_no
        self.generate_label.setText("原音频路径：audio/word/" + str(self.word_no) + ".mp3")

    def setNewAudio(self):
        self.new_audio=True

    def imageBtnClicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open jpg file", "", "jpg Files (*.jpg)")
        self.imagepath=file_path
        if self.imagepath:
            # Set the pixmap content of the label
            pixmap = QPixmap(self.imagepath)
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagelabel.setPixmap(scaled_pixmap)
            self.imagelabel.setScaledContents(True)

    # 复制图片
    def copyImage(self,new_name):
        try:
            source_path=self.imagepath
            # 目标文件夹
            image_name = os.path.basename(source_path)  # 包含后缀名
            target_path = "image"
            if not os.path.exists(target_path):
                os.makedirs(target_path)  # 如果文件夹不存在，则创建文件夹
            # 将音频复制到目标路径下，source_path包含文件名及后缀名，image_name是其中分离出的文件名
            shutil.copy(source_path, os.path.join(target_path, image_name))
            if os.path.exists(os.path.join(target_path, new_name)):
                os.remove(os.path.join(target_path, new_name))
            # 将音频重命名为new_name.jpg
            os.rename(os.path.join(target_path, image_name), os.path.join(target_path, new_name))
        except Exception as e:
            print(f'Error: {e}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = alterWordDialog()
    mainMindow.show()
    sys.exit(app.exec_())