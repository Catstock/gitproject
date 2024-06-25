import csv
import glob
import os
import shutil
import sys
import traceback

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTextStream
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QTextEdit, QDesktopWidget
import subprocess


class GenerateWindow(QMainWindow):
    def __init__(self,parent=None,pano=""):
        super().__init__(parent)
        self.setWindowTitle("生成")

        self.parent = parent
        self.pa_no=pano
        # Create two horizontal layouts
        self.patientlayout = QHBoxLayout()
        self.videolayout = QHBoxLayout()
        self.audiolayout = QHBoxLayout()
        self.current_str = ""
        self.pa_head_path = []
        self.audio_path = []
        self.audio_no_list=[]
        self.batch_size=5

        self.pa_label = QLabel("当前患者："+str(self.pa_no))
        self.batch_label = QLabel("当前患者："+str(self.pa_no))
        self.info_label = QLabel("生成状态：")
        self.patientlayout.addWidget(self.pa_label)
        self.patientlayout.addWidget(self.info_label)

        self.video_label = QLabel("视频生成：")
        # Create three buttons for each layout
        self.video_vBtn = QPushButton("生成元音视频")
        self.video_vBtn.clicked.connect(self.video_vBtnClicked)
        self.video_wBtn = QPushButton("生成单词视频")
        self.video_wBtn.clicked.connect(self.video_wBtnClicked)
        self.video_sBtn = QPushButton("生成句子视频")
        self.video_sBtn.clicked.connect(self.video_sBtnClicked)

        self.audio_label = QLabel("音频生成：")
        self.audio_vBtn = QPushButton("生成元音音频")
        self.audio_vBtn.hide()
        self.audio_vBtn.clicked.connect(self.audio_vBtnClicked)
        self.audio_wBtn = QPushButton("生成单词音频")
        self.audio_wBtn.clicked.connect(self.audio_wBtnClicked)
        self.audio_sBtn = QPushButton("生成句子音频")
        self.audio_sBtn.clicked.connect(self.audio_sBtnClicked)

        self.video_label = QLabel("音频生成：")
        # Add buttons to the first layout
        self.videolayout.addWidget(self.video_label)
        self.videolayout.addWidget(self.video_vBtn)
        self.videolayout.addWidget(self.video_wBtn)
        self.videolayout.addWidget(self.video_sBtn)

        # Add buttons to the second layout
        self.audiolayout.addWidget(self.audio_label)
        self.audiolayout.addWidget(self.audio_vBtn)
        self.audiolayout.addWidget(self.audio_wBtn)
        self.audiolayout.addWidget(self.audio_sBtn)

        # Create a vertical layout
        self.vlayout = QVBoxLayout()

        # Add the two horizontal layouts to the vertical layout
        self.vlayout.addLayout(self.patientlayout)
        self.vlayout.addLayout(self.videolayout)
        self.vlayout.addLayout(self.audiolayout)
        self.add_all_btn=QPushButton("一键生成所有音频视频")
        self.add_all_btn.clicked.connect(self.generate_all)
        self.vlayout.addWidget(self.add_all_btn)

        # Create a central widget and set the vertical layout as its layout
        central_widget = QWidget()
        central_widget.setLayout(self.vlayout)

        # Set the central widget of the main window
        self.setCentralWidget(central_widget)


    def video_vBtnClicked(self):
        self.current_str="vowel"
        self.info_label.setText("元音视频生成中...")
        self.set_button_disable()
        self.video_generate()
    def video_wBtnClicked(self):
        self.current_str="word"
        self.info_label.setText("单词视频生成中...")
        self.set_button_disable()
        self.video_generate()
    def video_sBtnClicked(self):
        self.current_str="sentence"
        self.info_label.setText("句子视频生成中...")
        self.set_button_disable()
        self.video_generate()
    def audio_vBtnClicked(self):
        self.current_str="vowel"
        self.info_label.setText("元音音频生成中...")
        self.set_button_disable()
        self.audio_generate()
        self.info_label.setText("已完成生成！")
        self.set_button_enable()
    def audio_wBtnClicked(self):
        self.current_str="word"
        self.info_label.setText("单词音频生成中...")
        self.set_button_disable()
        self.audio_generate()
        self.info_label.setText("已完成生成！")
        self.set_button_enable()
    def audio_sBtnClicked(self):
        self.current_str="sentence"
        self.info_label.setText("句子音频生成中...")
        self.set_button_disable()
        self.audio_generate()
        self.info_label.setText("已完成生成！")
        self.set_button_enable()
    def set_button_disable(self):
        self.video_vBtn.setEnabled(False)
        self.video_wBtn.setEnabled(False)
        self.video_sBtn.setEnabled(False)
        self.audio_vBtn.setEnabled(False)
        self.audio_wBtn.setEnabled(False)
        self.audio_sBtn.setEnabled(False)
    def set_button_enable(self):
        self.video_vBtn.setEnabled(True)
        self.video_wBtn.setEnabled(True)
        self.video_sBtn.setEnabled(True)
        self.audio_vBtn.setEnabled(True)
        self.audio_wBtn.setEnabled(True)
        self.audio_sBtn.setEnabled(True)
    def video_generate(self):
        try:
            if self.current_str=="vowel":
                # 读取文件夹中的所有文件名
                folder_path = "audio/" + self.current_str
                file_names = glob.glob(os.path.join(folder_path, "*"))
                # 将所有文件名添加到列表中
                for file_name in file_names:
                    self.pa_head_path.append("../PyQt-Sqlite-Project-CURD-master/pa_head/pa_" + str(self.pa_no))
                    temp_audio_path = os.path.splitext(os.path.basename(file_name))[0]
                    self.audio_no_list.append(temp_audio_path)
                    self.audio_path.append("../PyQt-Sqlite-Project-CURD-master/" + file_name)
                thread = VideoGenerateThread(self, self.audio_no_list,self.pa_head_path,self.audio_path,self.batch_size)
                thread.start()
            elif self.current_str=="word" or self.current_str=="sentence":
                # 读取文件夹中的所有文件名
                folder_path = "pa_audio/pa" + str(self.pa_no) + "/" + self.current_str
                file_names = glob.glob(os.path.join(folder_path, "*"))
                print(file_names)
                # 将所有文件名添加到列表中
                for file_name in file_names:
                    self.pa_head_path.append("../PyQt-Sqlite-Project-CURD-master/pa_head/pa_" + str(self.pa_no))
                    temp_audio_path = os.path.splitext(os.path.basename(file_name))[0]
                    self.audio_no_list.append(temp_audio_path)
                    self.audio_path.append("../PyQt-Sqlite-Project-CURD-master/" + file_name)
                thread = VideoGenerateThread(self, self.audio_no_list, self.pa_head_path, self.audio_path,
                                             self.batch_size)
                thread.start()
        except Exception as e:
            print(f'Error: {e}')

    def video_generate_all(self):
        try:
            self.info_label.setText("元音视频生成中...")
            self.set_button_disable()
            self.current_str="vowel"

            self.prepare_data()
            self.thread1 = VideoGenerateThread(self, self.audio_no_list, self.pa_head_path, self.audio_path,
                                               self.batch_size)
            self.thread1.finished_signal.connect(self.start_second_thread)
            self.thread1.start()
        except Exception as e:
            print(f'Error: {e}')
            traceback.print_exc()

    def start_second_thread(self):
        self.info_label.setText("词语视频生成中...")
        self.current_str = "word"
        self.prepare_data()
        self.thread2 = VideoGenerateThread(self, self.audio_no_list, self.pa_head_path, self.audio_path,
                                           self.batch_size)
        self.thread2.finished_signal.connect(self.start_third_thread)
        self.thread2.start()

    def start_third_thread(self):
        try:
            self.info_label.setText("句子视频生成中...")
            self.current_str = "sentence"
            self.prepare_data()
            self.thread3 = VideoGenerateThread(self, self.audio_no_list, self.pa_head_path, self.audio_path,
                                               self.batch_size)
            self.thread3.finished_signal.connect(self.finish_video_generate)
            self.thread3.start()
        except Exception as e:
            print(f'Error: {e}')
            traceback.print_exc()

    def finish_video_generate(self):
        self.info_label.setText("已完成生成！")
        self.set_button_enable()

    def prepare_data(self):
        try:
            if self.current_str == "vowel":
                folder_path = "audio/" + self.current_str
            else:
                folder_path = "pa_audio/pa" + str(self.pa_no) + "/" + self.current_str
            file_names = glob.glob(os.path.join(folder_path, "*"))
            for file_name in file_names:
                self.pa_head_path.append("../PyQt-Sqlite-Project-CURD-master/pa_head/pa_" + str(self.pa_no))
                temp_audio_path = os.path.splitext(os.path.basename(file_name))[0]
                self.audio_no_list.append(temp_audio_path)
                self.audio_path.append("../PyQt-Sqlite-Project-CURD-master/" + file_name)
        except Exception as e:
            print(f'Error: {e}')


    def audio_generate(self):
        try:
            table=""
            table_no=""
            table_name=""
            stype=""
            if self.current_str=="vowel":
                return
            elif self.current_str=="word":
                table="words"
                table_no="word_no"
                table_name="word_name"
                stype="word"
            elif self.current_str == "sentence":
                table = "sentence"
                table_no = "sentence_no"
                table_name = "sentence_name"
                stype="sentence"

            import sqlite3
            # 连接到数据库
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            # 选择表并获取数据
            sql = "SELECT %s, %s FROM %s" % (table_name, table_no,table)
            c.execute(sql)
            data = c.fetchall()
            #创建存放音频的文件
            pa_path="pa_audio/pa" + str(self.pa_no)+"/"+stype
            if not os.path.exists(pa_path):
                os.makedirs(pa_path)

            current_dir = os.getcwd()
            # 更改工作目录到MockingBird
            os.chdir("../MockingBird")
            sys.path.append(os.getcwd())
            from MockingBird.clone import MockingbirdInterface
            mockingbird = MockingbirdInterface()
            source_audio = "../PyQt-Sqlite-Project-CURD-master/pa_audio/pa" + str(self.pa_no) + "/pa" + str(self.pa_no) + ".mp3"
            mockingbird.generate_audio(source_audio, data, self.pa_no, stype)
            # 将工作目录返回到原始位置
            os.chdir(current_dir)

            # 关闭数据库连接
            conn.close()
        except Exception as e:
            print(f'Error: {e}')

    def generate_all(self):
        try:
            self.audio_vBtnClicked()
            self.audio_wBtnClicked()
            self.audio_sBtnClicked()
            self.video_generate_all()
        except Exception as e:
            print(f'Error: {e}')

    def writecsv(self,pa_head_path,audio_path):
        try:
            # 将数据按照指定的格式组织为列表
            data = []
            for i in range(len(pa_head_path)):
                row = [pa_head_path[i], '1', 'None', '0', audio_path[i], 'None', '0', 'None']
                data.append(row)

            # 将数据写入csv文件
            with open('../Talking-Face_PC-AVS-main/misc/demo2.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=' ')
                writer.writerows(data)
        except Exception as e:
            print(f'Error: {e}')

    def runAudio2Video(self):
        try:
            # 定义多条Git Bash命令
            commands = ['pwd && cd ../Talking-Face_PC-AVS-main && pwd && bash experiments/demo_vox.sh',
                        'exit'
                        ]
            # 唤起Git Bash并执行命令
            for cmd in commands:
                subprocess.call(['C:/Program Files/Git/bin/bash.exe', '-c', cmd])
        except Exception as e:
            print(f'Error: {e}')

    # 剪切视频
    def transVideo(self, audio_nos):
        try:
            #目标文件夹
            target_path = "pa_video/pa"+str(self.pa_no)
            temp_name = "pa" + str(self.pa_no) + "_"
            if self.current_str == "vowel":
                temp_name = temp_name + "v"
            elif self.current_str == "word":
                temp_name = temp_name + "w"
            elif self.current_str == "sentence":
                temp_name = temp_name + "s"

            for audio_no in audio_nos:
                # 定义视频的名称和源路径、目标路径
                video_name = "avG_Pose_Driven_.mp4"
                source_path = "pa_video/results/id_pa_" + str(self.pa_no) + "_pose_pa_" + str(self.pa_no) + "_audio_" + str(audio_no)
                new_name=temp_name+str(audio_no)+".mp4"
                # 将视频重命名为new_name.mp4
                os.rename(os.path.join(source_path, video_name), os.path.join(source_path, new_name))
                # 将视频剪切到目标路径下
                shutil.move(os.path.join(source_path, new_name), os.path.join(target_path, new_name))
        except Exception as e:
            print(f'Error: {e}')

    def deleteVideo(self):
        folder_path = "pa_video/results"
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # 使用shutil.rmtree()删除非空目录
            except Exception as e:
                print(f'Error: {e}')

    def closeEvent(self, event):
        try:
            # 在关闭摄像头窗口时返回主窗口
            self.parent.show()
            event.accept()
        except Exception as e:
            print(f'Error: {e}')


class VideoGenerateThread(QThread):
    finished_signal = pyqtSignal()
    def __init__(self, parent=None,audio_no_list=[],pa_head_path=[],audio_path=[],batch_size=0):
        super().__init__(parent)
        self.main_window = parent
        self.audio_no_list = audio_no_list
        self.pa_head_path = pa_head_path
        self.audio_path = audio_path
        self.batch_size = batch_size

    def run(self):
        try:
            for i in range(0, len(self.audio_no_list), self.batch_size):
                pa_head_path_batch = self.pa_head_path[i:i + self.batch_size]
                audio_no_batch = self.audio_no_list[i:i + self.batch_size]
                audio_path_batch = self.audio_path[i:i + self.batch_size]
                # 对批处理进行操作
                self.main_window.writecsv(pa_head_path_batch, audio_path_batch)
                self.main_window.runAudio2Video()
                self.main_window.transVideo(audio_no_batch)

            self.main_window.deleteVideo()
            # 清空列表
            self.main_window.pa_head_path.clear()
            self.main_window.audio_path.clear()
            self.main_window.audio_no_list.clear()
            self.main_window.info_label.setText("已完成生成！")
            self.main_window.set_button_enable()
            self.finished_signal.emit()
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    app = QApplication([])
    window = GenerateWindow()
    window.show()
    app.exec_()
