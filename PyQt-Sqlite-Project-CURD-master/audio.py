import subprocess
import sys
import os
import wave
from PyQt5.QtCore import Qt, QBuffer, QIODevice, QFile, QUrl, QByteArray
from PyQt5.QtMultimedia import QAudioFormat, QAudioDeviceInfo, QMediaPlayer, QMediaContent, QAudioInput
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFileDialog
from pydub import AudioSegment

class AudioRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.pa_no="0"
        self.train_str_no="w0"
        self.file_path=""
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

        # 创建一个 QVBoxLayout 布局管理器，并将按钮和 QLabel 添加到其中
        vbox = QHBoxLayout()
        vbox.addWidget(self.record_button)
        vbox.addWidget(self.stop_button)
        vbox.addWidget(self.play_button)
        vbox.addWidget(self.record_label)
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
                # self.record_label.setText("录音已完成")
                self.save_recording()
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(False)
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
            self.stop_button.setEnabled(False)
        except Exception as e:
            print(f'Error: {e}')

    def on_media_player_state_changed(self, state):
        try:
            if state == QMediaPlayer.StoppedState:
                # 释放资源
                self.media_player.setMedia(QMediaContent())
                self.media_player.setVideoOutput(None)
                # self.video_widget.hide()
                self.record_button.setEnabled(True)
                self.stop_button.setEnabled(True)
        except Exception as e:
            print(f'Error: {e}')

    def save_recording(self):
        try:
            if not self.recordings:
                return
            # 将录音数据转换为 AudioSegment 对象
            audio_data = b"".join(self.recordings)
            audio_segment = AudioSegment(data=audio_data, sample_width=2, frame_rate=44100, channels=1)
            # 保存录音
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("mp3")
            #file_path, _ = file_dialog.getSaveFileName(self, "保存录音", "", "Audio Files (*.mp3)")
            folder_path="pa_train/pa_"+str(self.pa_no)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # 如果文件夹不存在，则创建文件夹
            self.file_path=folder_path+"/trial0_"+str(self.train_str_no)+".mp3"
            if self.file_path:
                # 将wav格式的录音文件复制到指定的文件路径中
                audio_segment.export(self.file_path, format="mp3")
                # 显示保存成功信息
                self.record_label.setText(f"录音已保存到 {self.file_path}")
        except Exception as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = AudioRecorder()
    recorder.show()
    sys.exit(app.exec_())

