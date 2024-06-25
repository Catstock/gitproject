import os
import random

import qtawesome
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtWebEngineWidgets import QWebEngineView
#from PyQt5.QtPrintSupport import *
import sys,sqlite3,time
from PyQt5.uic.properties import QtCore

from fullPlayDialog import fullScreenVedioDialog
from av_test import VideoRecorder
#训练录制相关
class RecordingThread(QThread):
    def __init__(self, duration, trainfile):
        super().__init__()
        self.duration = duration
        self.trainfile = trainfile

    def run(self):
        self.vr = VideoRecorder()
        self.vr.start_recording(self.duration, self.trainfile)
    # 手动
    def set_vr_flag(self,value):
        self.vr.setflag(value)

class VowelWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(VowelWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 播放器
        self.videowidget = QVideoWidget()
        self.player = QMediaPlayer()
        self.player.stateChanged.connect(self.on_state_changed)#训练录制相关
        self.audio_player = QMediaPlayer()
        self.fsDialog = fullScreenVedioDialog()
        self.media_path = ""
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 当前患者编号
        self.temp_pano = "0"
        # 训练词语数
        self.vowel_total = 10
        self.current_v = 0
        self.vArray = []  # 词语列表
        self.trainfolder="" # 训练录制相关
        self.trainfile=""
        self.playflag=0
        self.duration=0
        self.is_random=0 # 随机 0为正序
        self.is_auto=0 # 0为自动
        self.recording_thread=None
        self.read_no = 0  # version2 记录读的次数
        self.ques_list = []  # 总结报告
        self.score_list = []
        self.text_list = []
        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.resize(960, 700)
        try:
            # 提示
            self.msgBox = QMessageBox()
            self.msgBox.setWindowTitle("提示")
            self.msgBox.setText("请对着视频跟读")
            font = QFont()
            font.setPointSize(40)
            self.msgBox.setFont(font)
            self.msgtimer = QTimer()
            self.msgtimer.setSingleShot(True)
            self.msgtimer.timeout.connect(self.msgBox.accept)
        except Exception as e:
            print(f'Error: {e}')
        # 选择用户
        self.layout = QVBoxLayout()
        self.indexlayout = QHBoxLayout()
        self.optionPackLayout = QHBoxLayout()
        self.optionLayout = QVBoxLayout()
        self.optionLayout1 = QHBoxLayout()
        self.optionLayout2 = QHBoxLayout()
        self.contentLayout = QHBoxLayout()
        self.video_layout = QVBoxLayout()
        self.vowel_layout = QVBoxLayout()
        self.vowel_layout1 = QHBoxLayout()
        self.vowel_layout2 = QHBoxLayout()
        self.vowel_layout3 = QHBoxLayout()
        self.vowel_layout4 = QHBoxLayout()

        self.titlelabel = QLabel("康复训练")
        font = self.titlelabel.font()
        font.setPointSize(25)
        font.setBold(1)
        font.setFamily("黑体")
        self.titlelabel.setFont(font)
        index_btn_len = 150
        self.IndexBtn = QtWidgets.QPushButton("首页")
        self.IndexBtn.setObjectName('index_button')
        self.IndexBtn.setFixedWidth(index_btn_len)
        self.trainMissionBtn = QtWidgets.QPushButton("训练任务")
        self.trainMissionBtn.setObjectName('index_button')
        self.trainMissionBtn.setFixedWidth(index_btn_len)
        self.user_manage_btn = QtWidgets.QPushButton("用户管理")
        self.user_manage_btn.setObjectName('index_button')
        self.user_manage_btn.setFixedWidth(index_btn_len)
        self.sys_manage_btn = QtWidgets.QPushButton("系统管理")
        self.sys_manage_btn.setObjectName('index_button')
        self.sys_manage_btn.setFixedWidth(index_btn_len)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.sys_manage_btn)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.trainMissionBtn.clicked.connect(self.trainMissionBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)
        self.sys_manage_btn.clicked.connect(self.sysManageBtnClicked)

        # 选项按钮1-10
        r = range(1, 11)
        for ele in r:
            exec('self.optionBtn{} = QPushButton("{}")'.format(ele, ele))
        self.optionLayout1.addWidget(self.optionBtn1)
        self.optionLayout1.addWidget(self.optionBtn2)
        self.optionLayout1.addWidget(self.optionBtn3)
        self.optionLayout1.addWidget(self.optionBtn4)
        self.optionLayout1.addWidget(self.optionBtn5)
        self.optionLayout2.addWidget(self.optionBtn6)
        self.optionLayout2.addWidget(self.optionBtn7)
        self.optionLayout2.addWidget(self.optionBtn8)
        self.optionLayout2.addWidget(self.optionBtn9)
        self.optionLayout2.addWidget(self.optionBtn10)
        self.leftPageBtn = QPushButton("上一题")
        self.rightPageBtn = QPushButton("下一题")
        self.leftPageBtn.clicked.connect(self.leftBtnClick)
        self.rightPageBtn.clicked.connect(self.rightBtnClick)
        self.optionLayout.addLayout(self.optionLayout1)
        self.optionLayout.addLayout(self.optionLayout2)
        self.optionPackLayout.addWidget(self.leftPageBtn)
        self.optionPackLayout.addLayout(self.optionLayout)
        self.optionPackLayout.addWidget(self.rightPageBtn)

        # 视频
        self.videowidget.resize(300, 300)
        self.player.setVideoOutput(self.videowidget)
        self.playLayout = QHBoxLayout()
        self.playpause = QPushButton("播放")
        self.fullplay = QPushButton("全屏播放")
        self.playLayout.addWidget(self.playpause)
        self.playLayout.addWidget(self.fullplay)
        self.video_layout.addWidget(self.videowidget)
        self.video_layout.addLayout(self.playLayout)
        self.video_layout.setStretch(0, 4)
        self.video_layout.setStretch(1, 1)

        # 词语展示板块
        self.vowelPicLabel = QLabel()
        font = QFont()
        font.setBold(1)
        font.setPixelSize(500)
        font.setFamily("黑体")
        self.vowelPicLabel.setFont(font)
        self.vowelBtn = QPushButton("发音")
        self.vowelBtn.clicked.connect(self.vowelBtnClick)
        self.vowelLabel = QLabel("")
        font = QFont()
        font.setPixelSize(50)
        font.setBold(1)
        font.setFamily("黑体")
        self.vowelLabel.setFont(font)

        # 录音相关
        # self.temp_pano = "0"
        self.train_str_no = ""
        self.file_path = ""
        self.trial_no = "0"  # 尚未自动生成
        from myaudiolayout import AudioRecorder
        self.vbox = QVBoxLayout()
        self.audiorecorder = AudioRecorder(self.temp_pano, self.train_str_no, self.trial_no, parent=self)
        self.audiorecorder.pagestate_clicked.connect(self.setBtnsState)  # 改变上下翻页按钮是否激活，防止录音被打断
        self.audiorecorder.hide()# 去除录音
        self.endRecordBtn = QPushButton("结束录制") # 手动
        font.setPixelSize(25)
        self.endRecordBtn.setFont(font)
        self.endRecordBtn.clicked.connect(self.endRecordBtnClicked)
        from assess import AudioAssess  # version2
        self.audio_assess = AudioAssess()
        self.audio_assess.set_hide()
        self.audio_assess.user_text_edit.hide()
        self.vbox.addWidget(self.audiorecorder)
        self.vbox.addWidget(self.endRecordBtn) # 手动
        self.vbox.addWidget(self.audio_assess)

        # 总排版
        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.optionPackLayout)
        self.layout.addLayout(self.contentLayout)
        # 连词成句按钮板块
        self.vowel_layout1.addWidget(self.vowelPicLabel, 1, Qt.AlignCenter)
        self.vowel_layout2.addWidget(self.vowelBtn)
        self.vowel_layout.addLayout(self.vowel_layout1)
        self.vowel_layout.addWidget(self.vowelLabel, 1, Qt.AlignCenter)
        self.vowel_layout.addLayout(self.vowel_layout2)
        # 录音相关
        self.vowel_layout.addLayout(self.vbox)
        # self.vowel_layout.addLayout(self.vowel_layout3)
        # self.vowel_layout.addLayout(self.vowel_layout4)

        # 连词成句按钮板块排版
        self.vowel_layout.setStretch(0, 3)
        self.vowel_layout.setStretch(1, 3)
        self.vowel_layout.setStretch(2, 3)
        self.vowel_layout.setStretch(3, 3)
        self.vowel_layout.setStretch(4, 1)
        self.contentLayout.addLayout(self.video_layout, 2)
        self.contentLayout.addLayout(self.vowel_layout, 3)
        self.playpause.clicked.connect(self.videoBtnClick)
        self.fullplay.clicked.connect(self.fullopenVedio)

        self.setLayout(self.layout)

    # 录音相关，在录音时控制翻页是否可用
    def setBtnsState(self, b_value):
        self.leftPageBtn.setEnabled(b_value)
        self.rightPageBtn.setEnabled(b_value)

    def IndexBtnClick(self):
        from t_main import IndexWindow
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def trainMissionBtnClick(self):
        if not (self.temp_pano == ""):
            from train import TrainWindow
            self.trainWindow = TrainWindow()
            self.trainWindow.showFullScreen()
            self.trainWindow.setNo(self.temp_pano)
            self.close()
        else:
            print(QMessageBox.warning(self, "警告", "请选择一名患者", QMessageBox.Yes, QMessageBox.Yes))

    def vowelBtnClick(self):
        self.audio_player.setVolume(80)
        self.audio_player.play()
        return

    def AssignVowel(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT COUNT(*) FROM vowel"
        query.exec_(sql)
        query.next()
        vowel_in_sql = int(query.value(0))
        if (vowel_in_sql < self.vowel_total):
            temp_num = vowel_in_sql
            self.vowel_total = temp_num
        else:
            temp_num = self.vowel_total
        if self.is_random==0:
            sql = "SELECT * FROM vowel ORDER BY vowel_no LIMIT '%s'" % (temp_num)
        else:
            sql = "SELECT * FROM vowel ORDER BY RANDOM() LIMIT '%s'" % (temp_num) # 随机
        query.exec_(sql)
        r = range(0, temp_num)
        for ele in r:
            query.next()
            self.vArray.append([])
            print(query.value(0))
            self.vArray[ele].append(query.value(0))  # vowel_no
            self.vArray[ele].append(query.value(1))  # vowel_name
            self.vArray[ele].append(query.value(2))  # vowel_audio
        #训练录制相关
        # 定义查询语句和插入语句
        select_sql = "SELECT trial_no FROM trial WHERE pa_no = ?"
        insert_sql = "INSERT INTO trial (pa_no, trial_no) VALUES (?, 0)"
        update_sql = "UPDATE trial SET trial_no = ? WHERE pa_no = ?"
        # 定义要查询的pa_no值
        pa_no = self.temp_pano
        # 执行查询操作
        query = QSqlQuery()
        query.prepare(select_sql)
        query.addBindValue(pa_no)
        query.exec_()
        if not query.next():
            # 如果查询结果为空，则插入新记录
            query.prepare(insert_sql)
            query.addBindValue(pa_no)
            query.exec_()
            db.commit()
            self.trial_no = 0
        else:
            # 如果查询结果不为空，则更新记录
            trial_no = query.value(0) + 1
            query.prepare(update_sql)
            query.addBindValue(trial_no)
            query.addBindValue(pa_no)
            query.exec_()
            db.commit()
            self.trial_no = trial_no

    def AssignBtns(self):
        try:
            # 录音相关
            self.vowel_no = self.vArray[self.current_v][0]
            self.train_str_no = "v" + str(self.vowel_no)
            self.audiorecorder.setTrainStr(self.train_str_no)
            self.audiorecorder.setTrialNo(self.trial_no)
            self.audiorecorder.setFilePath(self.trial_no, self.train_str_no)
            self.audiorecorder.setAuBtnsState(False)
            # 设置词语按钮
            vowel_name = self.vArray[self.current_v][1]
            self.vowelLabel.setText(vowel_name)
            self.vowelPicLabel.setText(vowel_name)
            # 设置播放
            self.media_path = "pa_video/pa" + str(self.temp_pano)+ "/pa" + str(self.temp_pano) + "_v" + str(self.vArray[self.current_v][0]) + ".mp4"
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_path)))
            audio_path = str(self.vArray[self.current_v][2])
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.videoBtnClick()
            print("change")
        except Exception as e:
            print(f'Error: {e}')

    def videoBtnClick(self):
        self.player.setVolume(80)
        self.player.play()

    def fullopenVedio(self):
        self.fsDialog.setMedia(self.media_path)
        self.fsDialog.showFullScreen()
        self.fsDialog.play()
        return

    def leftBtnClick(self):
        if (self.current_v > 0):
            self.current_v -= 1
            self.AssignBtns()

    def rightBtnClick(self):
        self.playflag = 0# 训练录制相关
        self.read_no = 0  # version2
        if (self.current_v < self.vowel_total - 1):
            self.current_v += 1
            self.AssignBtns()
        else:
            # 总结报告
            from train_log import TrainDialogue
            traindialogue = TrainDialogue(self)
            traindialogue.exec_()
            self.trainMissionBtnClick()

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

    def sysManageBtnClicked(self):
        from sys_management import SysManageWindow
        self.sysManageWindow=SysManageWindow()
        self.sysManageWindow.searchButtonClicked()
        self.sysManageWindow.showFullScreen()
        self.close()

    def setTaskNum(self, pano_value, num_value,is_random,is_auto):
        self.temp_pano = pano_value
        self.vowel_total = num_value
        self.is_random = is_random
        self.is_auto = is_auto

    def setTrainFile(self):#训练录制相关
        self.trainfolder="pa_train/pa_"+str(self.temp_pano)+"/trial"+str(self.trial_no)+"/"
        if not os.path.exists(self.trainfolder):
            os.makedirs(self.trainfolder)
        self.trainfile=self.trainfolder+self.train_str_no+"_"+str(self.read_no)+".mp4" #version2

    def on_state_changed(self, state):
        try:
            if self.is_auto == 0:
                if state == QMediaPlayer.StoppedState and self.playflag<=2:
                    self.read_no=self.read_no+1 # version2
                    self.duration = (self.player.duration() / 1000 * 2 + 4)
                    # 训练录制相关
                    self.setTrainFile()
                    print("录制中" + str(self.current_v))
                    recording_thread = RecordingThread(self.duration, self.trainfile)
                    recording_thread.start()
                    self.msgBox.setText("请在提示框消失之后对着视频跟读")
                    self.msgtimer.start(2000)  # 提示
                    self.msgBox.exec_()
                    self.playflag = self.playflag+1
                    time.sleep(self.duration)
                    temp_standard_audio="audio/vowel/"+str(self.vowel_no)+".mp3"
                    temp_user_audio="user_audio.mp3"
                    # 总结报告
                    score = self.audio_assess.set_file("",temp_standard_audio,temp_user_audio)
                    text=""
                    os.remove("user_audio.mp3")
                    temp_standard_text = self.vArray[self.current_v][1]
                    ques = "第" + str(self.read_no) + "遍：" + temp_standard_text
                    self.record_score_and_text(ques, score, text)
                    time.sleep(1)
                    if self.playflag==2:
                        self.rightBtnClick()
                    else:
                        self.videoBtnClick()
            # 手动
            elif self.is_auto==1:
                if state == QMediaPlayer.StoppedState:
                    self.read_no = self.read_no + 1  # version2
                    # 训练录制相关
                    self.setTrainFile()
                    print("录制中" + str(self.current_v))
                    self.recording_thread = RecordingThread(0, self.trainfile)
                    self.recording_thread.start()
                    self.msgBox.setText("请在提示框消失之后对着视频跟读，按 结束录制 结束跟读")
                    self.msgtimer.start(2000)  # 提示
                    self.msgBox.exec_()
                    self.playflag = self.playflag + 1

        except Exception as e:
            print(f'Error: {e}')
    # 手动
    def endRecordBtnClicked(self):
        try:
            self.recording_thread.set_vr_flag(True)
            time.sleep(1)
            temp_standard_audio = "audio/vowel/" + str(self.vowel_no) + ".mp3"
            temp_user_audio = "user_audio.mp3"
            # 总结报告
            score = self.audio_assess.set_file("", temp_standard_audio, temp_user_audio)
            text = ""
            os.remove("user_audio.mp3")
            temp_standard_text = self.vArray[self.current_v][1]
            ques = "第" + str(self.read_no) + "遍：" + temp_standard_text
            self.record_score_and_text(ques, score, text)
            time.sleep(1)
        except Exception as e:
            print(f'Error: {e}')

    # 总结报告
    def record_score_and_text(self, ques, score, text):
        self.ques_list.append(ques)
        self.score_list.append(score)
        self.text_list.append(text)

    # 展示图片
    # def showPaImage(self):
    #     # imageItem = QStandardItem(QIcon("pa_head/pa_0"))
    #     image_path="pa_head/pa_0"
    #     imageItem = QtGui.QPixmap(image_path).scaled(300, 300)
    #     img = mping.imread('path')  # 相对路径
    #     self.tableView.setItem(0, 6, imageItem)
    # 查询
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    temp_pano=0
    mainWindow = VowelWindow()
    mainWindow.setTaskNum(temp_pano, int(5))
    mainWindow.AssignVowel()
    mainWindow.AssignBtns()
    mainWindow.showFullScreen()
    # mainWindow.show()
    sys.exit(app.exec_())