import shutil
import subprocess
import sys
import os
from PyQt5.QtCore import Qt, QBuffer, QIODevice, QFile, QUrl, QByteArray, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QAudioFormat, QAudioDeviceInfo, QMediaPlayer, QMediaContent, QAudioInput
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog, \
    QMessageBox, QLineEdit
from PyQt5.uic.properties import QtGui
from pydub import AudioSegment

# 在新增词语/句子时录制音频的控件
class StandardAudioRecorder(QWidget):
    generate_clicked = pyqtSignal()
    audio_clicked = pyqtSignal()
    alterstr_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.text_str=""
        self.file_path = 'audio/temp_save_audio.mp3'
        #缓存播放
        self.player = QMediaPlayer()
        # 创建录音按钮
        self.record_button = QPushButton("开始录音")
        self.record_button.clicked.connect(self.start_recording)

        # 创建停止录音按钮
        self.stop_button = QPushButton("停止录音")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)

        # 创建播放录音按钮
        self.play_button = QPushButton("播放录音")
        self.play_button.clicked.connect(self.play_recording)
        self.play_button.setEnabled(False)

        # 创建一个 QLabel 用于显示录音状态信息
        self.record_label = QLabel("请点击“开始录音”按钮开始录音")
        # 患者录音
        self.notice_label = QLabel("请尽力朗读以下文字，朗读完成后点击结束录音完成录音")
        self.text_label = QLabel("大家好，我叫张三。我喜欢看书、听音乐和和朋友们聊天。我的家乡有美丽的山和清澈的河流。我很喜欢我的家乡。虽然我现在遇到了一些挑战，但我相信自己可以克服它们。")
        font=QFont()
        font.setPixelSize(40)
        self.text_label.setFont(font)
        self.text_label.setWordWrap(True)
        self.notice_label.hide()
        self.text_label.hide()

        self.open_buttton = QPushButton("从本地选择音频")
        self.open_buttton.clicked.connect(self.open_file)

        self.generate_button = QPushButton("算法生成音频")
        self.generate_button.clicked.connect(self.generate_audio)

        # 创建一个 QVBoxLayout 布局管理器，并将按钮和 QLabel 添加到其中
        vbox = QVBoxLayout()
        vbox.addWidget(self.record_label)
        vbox.addWidget(self.notice_label)
        vbox.addWidget(self.text_label)
        vbox.addWidget(self.record_button)
        vbox.addWidget(self.stop_button)
        vbox.addWidget(self.play_button)
        vbox.addWidget(self.open_buttton)
        vbox.addWidget(self.generate_button)
        # 设置 QWidget 的布局管理器
        self.setLayout(vbox)

        # 初始化录音参数
        self.audio_input = None
        self.buffer = None
        self.recordings = []
        # 创建播放器，并连接stateChanged信号
        self.media_player = QMediaPlayer(self)
        self.media_player.stateChanged.connect(self.on_media_player_state_changed)

    def start_recording(self):
        try:
            # 创建 QAudioFormat 对象
            format = QAudioFormat()
            format.setChannelCount(1)
            format.setSampleRate(44100)
            format.setSampleSize(16)
            format.setCodec("audio/pcm")
            format.setByteOrder(QAudioFormat.LittleEndian)
            format.setSampleType(QAudioFormat.SignedInt)

            # 创建 QAudioDeviceInfo 对象
            device_info = QAudioDeviceInfo.defaultInputDevice()

            # 创建 QAudioInput 对象
            self.audio_input = QAudioInput(device_info, format)

            # 创建 QBuffer 对象
            self.buffer = QBuffer()
            self.buffer.open(QIODevice.ReadWrite)

            # 将 QBuffer 对象绑定到 QAudioInput 对象上
            self.audio_input.start(self.buffer)

            # 更新 QLabel 显示的录音状态信息
            self.record_label.setText("正在录音...")


            self.stop_button.setEnabled(True)
            self.play_button.setEnabled(False)
        except Exception as e:
            print(f'Error: {e}')

    def stop_recording(self):
        try:
            if self.audio_input is not None:
                # 停止录音
                self.audio_input.stop()
                # 将录音数据添加到列表中
                self.buffer.close()
                self.recordings.append(self.buffer.data())
                # 显示录音成功信息
                self.record_label.setText("录音已完成")
                self.temp_save_recording()
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.on_alterstr_clicked()
        except Exception as e:
            print(f'Error: {e}')

    def play_recording(self):
        try:
            if self.file_path:
                # Set the media content of the media player
                media_content = QMediaContent(QUrl.fromLocalFile(self.file_path))
                self.media_player.setMedia(media_content)
            # 播放录音
            self.media_player.play()
            self.record_button.setEnabled(False)
        except Exception as e:
            print(f'Error: {e}')

    def open_file(self):
        try:
            # Open a file dialog to select a mp3 file
            file_path, _ = QFileDialog.getOpenFileName(self, "Open mp3 file", "", "mp3 Files (*.mp3)")
            if file_path:
                # Set the media content of the media player
                media_content = QMediaContent(QUrl.fromLocalFile(file_path))
                self.media_player.setMedia(media_content)
                self.copyAudio(file_path) # 放到save_temp_audio.mp3中
                self.record_label.setText("录音已加载")
                # 激活播放按钮
                self.play_button.setEnabled(True)
                self.on_alterstr_clicked()
        except Exception as e:
            print(f"Error: {e}")

    def on_media_player_state_changed(self, state):
        try:
            if state == QMediaPlayer.StoppedState:
                # 释放资源
                self.media_player.setMedia(QMediaContent())
                self.media_player.setVideoOutput(None)
                # self.video_widget.hide()
                self.record_button.setEnabled(True)
                self.stop_button.setEnabled(False)
        except Exception as e:
            print(f'Error: {e}')

    def temp_save_recording(self):
        try:
            if not self.recordings:
                return
            # 将录音数据转换为 AudioSegment 对象
            audio_data = b"".join(self.recordings)
            audio_segment = AudioSegment(data=audio_data, sample_width=2, frame_rate=44100, channels=1)
            # 保存录音
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("mp3")
            folder_path="audio"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # 如果文件夹不存在，则创建文件夹
            self.file_path=folder_path+"/temp_save_audio.mp3"
            if self.file_path:
                # 将mp3格式的录音文件复制到指定的文件路径中
                audio_segment.export(self.file_path, format="mp3")
        except Exception as e:
            print(f'Error: {e}')

    def copyAudio(self, source_path):
        try:
            #目标文件夹
            audio_name = os.path.basename(source_path) # 包含后缀名
            target_path = "audio"
            if not os.path.exists(target_path):
                os.makedirs(target_path)  # 如果文件夹不存在，则创建文件夹
            new_name = "temp_save_audio.mp3"
            # 将音频复制到目标路径下，source_path包含文件名及后缀名，audio_name是其中分离出的文件名
            shutil.copy(source_path, os.path.join(target_path, audio_name))
            if os.path.exists(os.path.join(target_path, new_name)):
                os.remove(os.path.join(target_path, new_name))
            # 将音频重命名为new_name.mp3
            os.rename(os.path.join(target_path, audio_name), os.path.join(target_path, new_name))
        except Exception as e:
            print(f'Error: {e}')

    def generate_audio(self):
        self.on_generate_clicked()
        try:
            text = self.text_str.replace(" ", "")
            text = text.strip()
            if text == "":
                print(QMessageBox.warning(self, "警告", "输入词语名称", QMessageBox.Yes, QMessageBox.Yes))
            else:
                import pyttsx3
                # 保存音频到'/audio/a1.mp3'
                say = pyttsx3.init()  # 创建pyttsx对象，并初始化对象
                # rate = say.getProperty('rate')  # 获取当前语速属性的值
                # print('默认的语速是：',rate)
                say.setProperty('rate', 100)  # 语速属性为0-500
                say.say(text)  # 合成并播放语音
                say.save_to_file(text, 'audio/temp_save_audio.mp3')
                say.runAndWait()
                self.play_button.setEnabled(True)
                self.on_audio_clicked()
                self.on_alterstr_clicked()
                return
        except Exception as e:
            print(f'Error: {e}')

        return

    def on_generate_clicked(self):
        self.generate_clicked.emit()

    def on_audio_clicked(self):
        self.audio_clicked.emit()

    def on_alterstr_clicked(self):
        self.alterstr_clicked.emit()

    def set_text_str(self,text):
        self.text_str=text

    def set_file_path(self,file_path):
        self.copyAudio(file_path)# 放到temp_save_audio.mp3中
        # 激活播放按钮
        self.play_button.setEnabled(True)

    def hide_generate_btn(self):
        self.generate_button.hide()

    def show_patient_notice(self):
        self.text_label.show()
        self.notice_label.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = StandardAudioRecorder()
    recorder.show()
    sys.exit(app.exec_())

