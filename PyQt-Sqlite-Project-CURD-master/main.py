from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from addDialog import addPaDialog
from alterDialog import alterPaDialog
from adduser import addUserDialog
from alteruser import alterUserDialog
import random
import sys,sqlite3,time
import os

from fullPlayDialog import fullScreenVedioDialog


class TrainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrainWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 查询模型
        self.queryModel = None
        # 数据表
        self.tableView = None
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecord = 0
        # 每页数据数
        self.pageRecord = 10
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 当前患者编号
        self.temp_pano = "0"
        # 类型计数
        self.i = 0
        self.task_type_edit = QLineEdit()
        # 初始化修改窗口
        self.alterDialog = alterUserDialog()
        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.setFixedSize(960, 700)

        # 选择用户
        self.layout = QVBoxLayout()
        self.indexlayout = QHBoxLayout()
        self.pa_layout = QHBoxLayout()
        self.pa_btns_laylout = QHBoxLayout()

        # 导航栏
        # self.index_widget = QtWidgets.QWidget()  # 创建左侧部件
        # self.index_widget.setObjectName('index_widget')
        # self.index_widget.setLayout(self.indexlayout) # 设置左侧部件布局为网格

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
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)

        # 当前已选择用户

        self.selected_pa_label = QLabel("当前选择的患者为：无")
        self.pa_layout.addWidget(self.selected_pa_label)

        # 训练类型
        self.trainPackLayout = QHBoxLayout()
        self.train_mid_layout = QVBoxLayout()
        self.train_pic = QLabel()
        self.task_type_combo = QComboBox()
        self.searchCondision = ['元音训练', '词语训练', '配对训练', '连词成句训练']
        self.task_type_combo.setFixedHeight(50)
        self.task_type_combo.setFont(font)
        self.task_type_combo.addItems(self.searchCondision)
        self.task_type_combo.currentIndexChanged.connect(self.taskComboClick)
        self.changeTask()
        self.train_mid_layout.addWidget(self.train_pic)
        self.train_mid_layout.addWidget(self.task_type_combo)

        self.leftBtn = QPushButton("上一项")
        self.rightBtn = QPushButton("下一项")
        self.leftBtn.setFixedSize(300, 300)
        self.rightBtn.setFixedSize(300, 300)
        self.leftBtn.clicked.connect(self.leftBtnClick)
        self.rightBtn.clicked.connect(self.rightBtnClick)

        self.trainPackLayout.addWidget(self.leftBtn)
        self.trainPackLayout.addLayout(self.train_mid_layout)
        self.trainPackLayout.addWidget(self.rightBtn)
        self.trainPackLayout.setAlignment(Qt.AlignCenter)

        # 训练方案
        self.task_content_layout = QHBoxLayout()
        self.task_titleLabel = QLabel("训练方案")
        self.task_titleLabel.setFont(font)
        # 训练类型
        self.task_type_layout = QVBoxLayout()
        self.task_type_label = QLabel("训练类型")
        self.task_type_label.setFont(font)
        self.task_type_edit.setFixedWidth(400)
        self.task_type_edit.setFixedHeight(50)
        self.task_type_edit.setText(self.task_type_combo.currentText())
        self.task_type_edit.setEnabled(False)
        self.task_type_layout.addWidget(self.task_type_label)
        self.task_type_layout.addWidget(self.task_type_edit)
        # 题目数量
        self.quest_num_layout = QVBoxLayout()
        self.quest_num_label = QLabel("题目数量")
        self.quest_num_label.setFont(font)
        self.quest_num_edit = QLineEdit()
        self.quest_num_edit.setFixedWidth(200)
        self.quest_num_edit.setFixedHeight(50)
        self.quest_num_edit.setValidator(QtGui.QIntValidator())
        self.quest_num_layout.addWidget(self.quest_num_label)
        self.quest_num_layout.addWidget(self.quest_num_edit)
        # 题目顺序
        self.quest_order_layout = QVBoxLayout()
        self.quest_order_label = QLabel("题目顺序")
        self.quest_order_label.setFont(font)
        self.quest_order_combo = QComboBox()
        self.questCondision = ['正序', '乱序']
        self.quest_order_combo.setFixedHeight(50)
        self.quest_order_combo.addItems(self.questCondision)
        self.quest_order_layout.addWidget(self.quest_order_label)
        self.quest_order_layout.addWidget(self.quest_order_combo)
        # 进入训练
        self.trainBtn = QPushButton("开始训练")
        self.trainBtn.setFixedHeight(150)
        self.trainBtn.setFont(font)
        self.trainBtn.clicked.connect(self.trainBtnClick)
        # 加入排版
        self.task_content_layout.addWidget(self.task_titleLabel)
        self.task_content_layout.addLayout(self.task_type_layout)
        self.task_content_layout.addLayout(self.quest_num_layout)
        self.task_content_layout.addLayout(self.quest_order_layout)
        self.task_content_layout.addWidget(self.trainBtn)
        self.task_content_layout.setAlignment(Qt.AlignLeft)

        #

        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.pa_layout)
        self.layout.addLayout(self.trainPackLayout)
        self.layout.addLayout(self.task_content_layout)
        self.layout.setAlignment(Qt.AlignTop)
        # self.layout.addLayout(self.Hlayout1)
        # self.layout.addWidget(self.tableView)
        # self.layout.addLayout(self.pa_btns_laylout)
        # self.layout.addLayout(self.Hlayout2)
        self.setLayout(self.layout)

    def IndexBtnClick(self):
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def taskComboClick(self):
        self.i = self.task_type_combo.currentIndex()
        self.changeTask()

    def leftBtnClick(self):
        if self.i > 0:
            self.i -= 1
            self.task_type_combo.setCurrentIndex(self.i)
            self.changeTask()

    def rightBtnClick(self):
        if self.i < len(self.searchCondision) - 1:
            self.i += 1
            self.task_type_combo.setCurrentIndex(self.i)
        elif self.i == len(self.searchCondision) - 1:
            self.i = 0
            self.task_type_combo.setCurrentIndex(self.i)
            self.changeTask()

    def changeTask(self):
        image_path = "icon/" + self.task_type_combo.currentText() + ".jpg"
        temp_pic = QtGui.QPixmap(image_path)
        # w = temp_pic.width()
        # h = temp_pic.height()
        # if not w == 0:
        #     if (w / h > 1):
        #         temp_pic = temp_pic.scaledToWidth(800)
        #     else:
        temp_pic = temp_pic.scaledToHeight(700)
        self.train_pic.setPixmap(temp_pic)
        self.train_pic.setFixedWidth(700)
        self.train_pic.setScaledContents(True)
        self.task_type_edit.setText(self.task_type_combo.currentText())

    def trainBtnClick(self):
        if(self.quest_num_edit.text()==""):
            print(QMessageBox.warning(self,'警告','请输入一个数字', QMessageBox.Yes, QMessageBox.Yes))
            return
        elif(self.task_type_combo.currentText()=="元音训练"):
            self.vowelwindow = VowelWindow()
            self.vowelwindow.setTaskNum(self.temp_pano,int(self.quest_num_edit.text()))
            self.vowelwindow.AssignVowel()
            self.vowelwindow.AssignBtns()
            self.vowelwindow.showFullScreen()
            self.close()
        elif (self.task_type_combo.currentText() == "词语训练"):
            self.wordwindow = WordWindow()
            self.wordwindow.setTaskNum(self.temp_pano,int(self.quest_num_edit.text()))
            self.wordwindow.AssignWord()
            self.wordwindow.AssignBtns()
            self.wordwindow.showFullScreen()
            self.close()
        elif (self.task_type_combo.currentText() == "连词成句训练"):
            self.wswindow = WSWindow()
            self.wswindow.setTaskNum(self.temp_pano,int(self.quest_num_edit.text()))
            self.wswindow.AssignSentence()
            self.wswindow.AssignBtns()
            self.wswindow.showFullScreen()
            self.close()

    def setNo(self, no_value):
        self.temp_pano = str(no_value)
        self.selected_pa_label.setText(self.temp_pano)

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

class VowelWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(VowelWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 播放器
        self.videowidget = QVideoWidget()
        self.player = QMediaPlayer()
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

        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.resize(960, 700)

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
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.trainMissionBtn.clicked.connect(self.trainMissionBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)

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

    def IndexBtnClick(self):
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def trainMissionBtnClick(self):
        if not (self.temp_pano==""):
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
        sql = "SELECT * FROM vowel ORDER BY vowel_no LIMIT '%s'" % (temp_num)
        query.exec_(sql)
        r = range(0, temp_num)
        for ele in r:
            query.next()
            self.vArray.append([])
            print(query.value(0))
            self.vArray[ele].append(query.value(0))  # vowel_no
            self.vArray[ele].append(query.value(1))  # vowel_name
            self.vArray[ele].append(query.value(2))  # vowel_audio

    def AssignBtns(self):
        # 设置词语按钮
        vowel_name = self.vArray[self.current_v][1]
        audio_path = self.vArray[self.current_v][2]
        self.vowelLabel.setText(vowel_name)
        self.vowelPicLabel.setText(vowel_name)
        # 设置播放
        self.media_path = "pa_video/pa" + str(self.temp_pano) + "_v" + str(self.vArray[self.current_v][0]) + ".mp4"
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_path)))
        audio_path = str(self.vArray[self.current_v][2])
        self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
        self.videoBtnClick()

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
        if (self.current_v < self.vowel_total - 1):
            self.current_v += 1
            self.AssignBtns()

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

    def setTaskNum(self, pano_value, num_value):
        self.temp_pano = pano_value
        self.vowel_total = num_value
    # 展示图片
    # def showPaImage(self):
    #     # imageItem = QStandardItem(QIcon("pa_head/pa_0"))
    #     image_path="pa_head/pa_0"
    #     imageItem = QtGui.QPixmap(image_path).scaled(300, 300)
    #     img = mping.imread('path')  # 相对路径
    #     self.tableView.setItem(0, 6, imageItem)
    # 查询

class WordWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(WordWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        desktop = QApplication.desktop()
        self.setFixedWidth(desktop.width())
        self.setWindowTitle("欢迎使用康复训练系统")
        # 播放器
        self.videowidget = QVideoWidget()
        self.player = QMediaPlayer()
        self.audio_player = QMediaPlayer()
        self.fsDialog = fullScreenVedioDialog()
        self.media_path = ""
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 当前患者编号
        self.temp_pano = "0"
        #训练词语数
        self.word_total=10
        self.current_w=0
        self.wArray = []  # 词语列表

        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.resize(700, 500)

        # 选择用户
        self.layout = QVBoxLayout()
        self.indexlayout = QHBoxLayout()
        self.optionPackLayout=QHBoxLayout()
        self.optionLayout=QVBoxLayout()
        self.optionLayout1=QHBoxLayout()
        self.optionLayout2 = QHBoxLayout()
        self.contentLayout=QHBoxLayout()
        self.video_layout=QVBoxLayout()
        self.word_layout=QVBoxLayout()
        self.word_layout1 = QHBoxLayout()
        self.word_layout2 = QHBoxLayout()

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
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.trainMissionBtn.clicked.connect(self.trainMissionBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)

        # 选项按钮1-10
        r = range(1, 11)
        for ele in r:
            exec('self.optionBtn{} = QPushButton("{}")'.format(ele,ele))
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
        self.videowidget.resize(300,300)
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
        self.wordPicLabel = QLabel()
        self.wordBtn=QPushButton("发音")
        self.wordBtn.clicked.connect(self.wordBtnClick)
        self.wordLabel=QLabel("")
        font = QFont()
        font.setPixelSize(50)
        font.setBold(1)
        font.setFamily("黑体")
        self.wordLabel.setFont(font)

        # 总排版
        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.optionPackLayout)
        self.layout.addLayout(self.contentLayout)
        # 连词成句按钮板块
        self.word_layout1.addWidget(self.wordPicLabel,1,Qt.AlignCenter)
        self.word_layout2.addWidget(self.wordBtn)
        self.word_layout.addLayout(self.word_layout1)
        self.word_layout.addWidget(self.wordLabel,1,Qt.AlignCenter)
        self.word_layout.addLayout(self.word_layout2)
        # self.word_layout.addLayout(self.word_layout3)
        # self.word_layout.addLayout(self.word_layout4)

        # 连词成句按钮板块排版
        # self.word_layout.setStretch(0,3)
        # self.word_layout.setStretch(1, 3)
        # self.word_layout.setStretch(2, 3)
        # self.word_layout.setStretch(3, 3)
        #self.word_layout.setStretch(4, 1)
        self.contentLayout.addLayout(self.video_layout,1)
        self.contentLayout.addLayout(self.word_layout,2)
        self.playpause.clicked.connect(self.videoBtnClick)
        self.fullplay.clicked.connect(self.fullopenVedio)

        self.setLayout(self.layout)

    def IndexBtnClick(self):
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def trainMissionBtnClick(self):
        if not (self.temp_pano==""):
            self.trainWindow = TrainWindow()
            self.trainWindow.showFullScreen()
            self.trainWindow.setNo(self.temp_pano)
            self.close()
        else:
            print(QMessageBox.warning(self, "警告", "请选择一名患者", QMessageBox.Yes, QMessageBox.Yes))

    def wordBtnClick(self):
        self.audio_player.setVolume(80)
        self.audio_player.play()
        return

    def AssignWord(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT COUNT(*) FROM words"
        query.exec_(sql)
        query.next()
        word_in_sql = int(query.value(0))
        if(word_in_sql<self.word_total):
            temp_num=word_in_sql
            self.word_total=temp_num
        else:
            temp_num=self.word_total
        sql = "SELECT * FROM words ORDER BY RANDOM() LIMIT '%s'" % (temp_num)
        query.exec_(sql)
        r = range(0, temp_num)
        for ele in r:
            query.next()
            self.wArray.append([])
            print(query.value(0))
            self.wArray[ele].append(query.value(0)) # word_no
            self.wArray[ele].append(query.value(1)) # word_name
            self.wArray[ele].append(query.value(2)) # word_audio
            self.wArray[ele].append(query.value(3)) # word_image

    def AssignBtns(self):
        # 设置词语按钮
        word_name=self.wArray[self.current_w][1]
        audio_path=self.wArray[self.current_w][2]
        image_path=self.wArray[self.current_w][3]
        self.wordLabel.setText(word_name)
        temp_pic = QtGui.QPixmap(image_path)
        w = temp_pic.width()
        h=temp_pic.height()
        if not w==0:
            if(w/h>1):
                temp_pic=temp_pic.scaledToWidth(700)
            else:
                temp_pic = temp_pic.scaledToHeight(600)
        # temp_pic = QtGui.QPixmap(image_path).scaledToWidth(700)
        self.wordPicLabel.setPixmap(temp_pic)
        self.wordPicLabel.setFixedWidth(700)
        self.wordPicLabel.setScaledContents(True)
        # 设置播放
        self.media_path="pa_video/pa"+str(self.temp_pano)+"_w"+str(self.wArray[self.current_w][0])+".mp4"
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_path)))
        audio_path = str(self.wArray[self.current_w][2])
        self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
        self.videoBtnClick()

    def videoBtnClick(self):
        self.player.setVolume(80)
        self.player.play()

    def fullopenVedio(self):
        self.fsDialog.setMedia(self.media_path)
        self.fsDialog.showFullScreen()
        self.fsDialog.play()
        return

    def leftBtnClick(self):
        if(self.current_w>0):
            self.current_w-=1
            self.AssignBtns()

    def rightBtnClick(self):
        if(self.current_w<self.word_total-1):
            self.current_w+=1
            self.AssignBtns()
    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

    def setTaskNum(self,pano_value,num_value):
        self.temp_pano =pano_value
        self.vowel_total=num_value

class WSWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(WSWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 播放器
        self.videowidget = QVideoWidget()
        self.player = QMediaPlayer()
        self.audio_player = QMediaPlayer()
        self.fsDialog=fullScreenVedioDialog()
        self.media_path=""
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 当前患者编号
        self.temp_pano = "0"
        # 连词计数
        self.i = 1
        self.countflag = 0
        # 训练句子数
        self.sentence_total = 0
        self.sArray = []  # 句子列表
        self.current_s = 0
        self.wArray = []  # 词语列表
        self.w_btnArray = []  # 按钮表
        self.s_btnArray = []  # 句子按钮表
        # 句子按钮
        self.s_btn1 = QPushButton("")
        self.s_btn2 = QPushButton("")
        self.s_btn3 = QPushButton("")
        self.s_btn4 = QPushButton("")
        self.s_btn5 = QPushButton("")
        self.s_btn6 = QPushButton("")
        self.s_btn7 = QPushButton("")
        self.s_btn8 = QPushButton("")
        self.s_btn9 = QPushButton("")
        self.s_btn10 = QPushButton("")
        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.resize(960, 700)

        # 选择用户
        self.layout = QVBoxLayout()
        self.indexlayout = QHBoxLayout()
        self.optionPackLayout = QHBoxLayout()
        self.optionLayout = QVBoxLayout()
        self.optionLayout1 = QHBoxLayout()
        self.optionLayout2 = QHBoxLayout()
        self.contentLayout = QHBoxLayout()
        self.video_layout = QVBoxLayout()
        self.ws_layout = QVBoxLayout()
        self.ws_layout1 = QHBoxLayout()
        self.ws_layout2 = QHBoxLayout()
        self.ws_layout3 = QHBoxLayout()
        self.ws_layout4 = QHBoxLayout()

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
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.trainMissionBtn.clicked.connect(self.trainMissionBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)

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
        self.playLayout=QHBoxLayout()
        self.playpause = QPushButton("播放")
        self.fullplay=QPushButton("全屏播放")
        self.playLayout.addWidget(self.playpause)
        self.playLayout.addWidget(self.fullplay)
        self.video_layout.addWidget(self.videowidget)
        self.video_layout.addLayout(self.playLayout)
        self.video_layout.setStretch(0, 4)
        self.video_layout.setStretch(1, 1)

        # 连词成句
        # 定义1到11的区间(包含1,不包含11),创建w_btn(1-10)赋予w_btn点击事件
        # self.w_btn1= QPushButton("1")
        r = range(1, 11)
        for ele in r:
            exec('self.w_btn{}= QPushButton("")'.format(ele))
            exec('self.w_btn{}.clicked.connect(self.wsBtnClick)'.format(ele))
            exec('self.w_btnArray.append(self.w_btn{})'.format(ele))
            exec('self.s_btnArray.append(self.s_btn{})'.format(ele))
        # 加入排版
        self.ws_layout1.addWidget(self.w_btn1)
        self.ws_layout1.addWidget(self.w_btn2)
        self.ws_layout1.addWidget(self.w_btn3)
        self.ws_layout1.addWidget(self.w_btn4)
        self.ws_layout1.addWidget(self.w_btn5)
        self.ws_layout2.addWidget(self.w_btn6)
        self.ws_layout2.addWidget(self.w_btn7)
        self.ws_layout2.addWidget(self.w_btn8)
        self.ws_layout2.addWidget(self.w_btn9)
        self.ws_layout2.addWidget(self.w_btn10)

        self.ws_layout3.addWidget(self.s_btn1)
        self.ws_layout3.addWidget(self.s_btn2)
        self.ws_layout3.addWidget(self.s_btn3)
        self.ws_layout3.addWidget(self.s_btn4)
        self.ws_layout3.addWidget(self.s_btn5)
        self.ws_layout4.addWidget(self.s_btn6)
        self.ws_layout4.addWidget(self.s_btn7)
        self.ws_layout4.addWidget(self.s_btn8)
        self.ws_layout4.addWidget(self.s_btn9)
        self.ws_layout4.addWidget(self.s_btn10)

        self.checkBtn = QPushButton("确认")
        self.checkBtn.clicked.connect(self.checkClick)
        self.backBtn = QPushButton("回退")
        self.backBtn.clicked.connect(self.minus)

        # 总排版
        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.optionPackLayout)
        self.layout.addLayout(self.contentLayout)
        # 连词成句按钮板块
        self.ws_layout.addLayout(self.ws_layout1)
        self.ws_layout.addLayout(self.ws_layout2)
        self.ws_layout.addLayout(self.ws_layout3)
        self.ws_layout.addLayout(self.ws_layout4)
        # 确认和回退按钮
        self.ws_checkpack_layout = QHBoxLayout()
        self.ws_checkpack_layout.addWidget(self.checkBtn)
        self.ws_checkpack_layout.addWidget(self.backBtn)
        self.ws_checkpack_layout.setStretch(0, 3)
        self.ws_checkpack_layout.setStretch(1, 1)
        self.ws_layout.addLayout(self.ws_checkpack_layout)
        # 连词成句按钮板块排版
        self.ws_layout.setStretch(0, 3)
        self.ws_layout.setStretch(1, 3)
        self.ws_layout.setStretch(2, 3)
        self.ws_layout.setStretch(3, 3)
        self.ws_layout.setStretch(4, 1)
        self.contentLayout.addLayout(self.video_layout, 2)
        self.contentLayout.addLayout(self.ws_layout, 3)
        self.playpause.clicked.connect(self.openVideoFile)
        self.fullplay.clicked.connect(self.fullopenVedio)

        self.setLayout(self.layout)

    def IndexBtnClick(self):
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def trainMissionBtnClick(self):
        if not (self.temp_pano==""):
            self.trainWindow = TrainWindow()
            self.trainWindow.showFullScreen()
            self.trainWindow.setNo(self.temp_pano)
            self.close()
        else:
            print(QMessageBox.warning(self, "警告", "请选择一名患者", QMessageBox.Yes, QMessageBox.Yes))

    def AssignSentence(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT COUNT(*) FROM sentence"
        query.exec_(sql)
        query.next()
        sentence_in_sql = int(query.value(0))
        if (sentence_in_sql < self.sentence_total):
            temp_num = sentence_in_sql
            self.sentence_total = temp_num
        else:
            temp_num = self.sentence_total
        sql = "SELECT * FROM sentence ORDER BY RANDOM() LIMIT '%s'" % (temp_num)
        query.exec_(sql)
        r = range(0, temp_num)
        for ele in r:
            query.next()
            self.sArray.append([])
            print(query.value(0))
            self.sArray[ele].append(query.value(0))  # sentence_no
            self.sArray[ele].append(query.value(1))  # sentence_name
            self.sArray[ele].append(query.value(2))  # sentence_audio

    def AssignBtns(self):
        self.i = 1
        temp_s_no = self.sArray[self.current_s][0]
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName('database.db')
        db.open()
        query = QSqlQuery()
        sql = "SELECT word_name FROM sentence_word WHERE sentence_no= '%s'" % (temp_s_no)
        query.exec_(sql)
        # 添加词语到列表
        while (query.next()):
            self.wArray.append(query.value(0))
        random.shuffle(self.wArray)
        # 设置词语按钮
        temp_w_count = len(self.wArray)
        r = range(0, temp_w_count)
        for ele in r:
            temp_str = self.wArray[ele]
            self.w_btnArray[ele].setText(temp_str)
        r = range(temp_w_count, 10)
        for ele in r:
            self.w_btnArray[ele].setText("")
        r = range(0, 10)
        for ele in r:
            self.s_btnArray[ele].setText("")
        # 设置播放
        self.media_path = "pa_video/pa" + str(self.temp_pano) + "_s" + str(temp_s_no) + ".mp4"
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_path)))

    def openVideoFile(self):
        self.player.setVolume(80)
        self.player.play()

    def fullopenVedio(self):
        self.fsDialog.setMedia(self.media_path)
        self.fsDialog.showFullScreen()
        self.fsDialog.play()
        return

    def leftBtnClick(self):
        if (self.current_s > 0):
            self.current_s -= 1
            self.wArray.clear()
            self.AssignBtns()

    def rightBtnClick(self):
        if (self.current_s < self.sentence_total - 1):
            self.current_s += 1
            self.wArray.clear()
            self.AssignBtns()

    def wsBtnClick(self):
        sender = self.sender()
        senderText = str(sender.text())
        if not senderText == "" and self.i <= len(self.wArray):
            if self.countflag==2:
                self.i+=1
            exec('self.s_btn{}.setText(senderText)'.format(self.i))
            audio_path = "audio/word/" + senderText + ".mp3"
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
            self.audio_player.setVolume(80)
            self.audio_player.play()
            if self.i >= 0:
                self.i += 1  # 变量自增
                self.countflag = 1
        else:
            return

    def minus(self):
        print("i的值是"+str(self.i))
        print("array的长度为"+str(len(self.wArray)))
        exec('self.s_btn{}.setText("")'.format(self.i))
        if (self.countflag == 1):
            exec('self.s_btn{}.setText("")'.format(self.i))
            self.i -= 1
            self.countflag = 0
        exec('self.s_btn{}.setText("")'.format(self.i))
        if self.i > 1:
            self.i -= 1
        if not self.s_btn1.text() =="": #减了，但是没减到底
            self.countflag=2
        else:
            self.countflag=0
        print("coutflag="+str(self.countflag))
    def checkClick(self):
        temp_sentence = ""
        r = range(0, 10)
        for ele in r:
            temp_sentence = temp_sentence + self.s_btnArray[ele].text()
        if temp_sentence == self.sArray[self.current_s][1]:
            print({QMessageBox.information(self, "提示", "回答正确！", QMessageBox.Yes, QMessageBox.Yes)})
            self.rightBtnClick()
        else:
            print({QMessageBox.information(self, "提示", "回答错误！再试一遍吧！", QMessageBox.Yes, QMessageBox.Yes)})

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

    def setTaskNum(self, pano_value, num_value):
        self.temp_pano = pano_value
        self.sentence_total = num_value

class ManageWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(ManageWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 查询模型
        self.queryModel = None
        # 数据表
        self.tableView = None
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecord = 0
        # 每页数据数
        self.pageRecord = 10
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 初始化修改窗口
        self.alterDialog = alterUserDialog()
        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.setFixedSize(960, 700)

        # 选择用户
        self.layout = QVBoxLayout()
        self.indexlayout = QHBoxLayout()
        self.pa_layout = QHBoxLayout()
        self.Hlayout1 = QHBoxLayout()
        self.pa_btns_laylout = QHBoxLayout()
        self.Hlayout2 = QHBoxLayout()

        # 导航栏
        # self.index_widget = QtWidgets.QWidget()  # 创建左侧部件
        # self.index_widget.setObjectName('index_widget')
        # self.index_widget.setLayout(self.indexlayout) # 设置左侧部件布局为网格

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
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.IndexBtn.clicked.connect(self.IndexBtnClick)
        self.exitBtn.clicked.connect(self.exitBtnClick)

        # 当前已选择用户

        self.selected_pa_label = QLabel("当前选择的用户为：无")
        self.pa_layout.addWidget(self.selected_pa_label)

        # Hlayout1，查询功能
        self.searchEdit = QLineEdit()
        self.searchEdit.setFixedHeight(32)
        font = QFont()
        font.setPixelSize(15)
        self.searchEdit.setFont(font)

        self.searchButton = QPushButton("查询")
        self.searchButton.setFixedHeight(32)
        self.searchButton.setFont(font)
        self.searchButton.setIcon(QIcon(QPixmap("./images/search.png")))

        self.condisionComboBox = QComboBox()
        searchCondision = ['按用户名查询']
        self.condisionComboBox.setFixedHeight(32)
        self.condisionComboBox.setFont(font)
        self.condisionComboBox.addItems(searchCondision)

        self.Hlayout1.addWidget(self.searchEdit)
        self.Hlayout1.addWidget(self.searchButton)
        self.Hlayout1.addWidget(self.condisionComboBox)

        # 增删改
        self.addBtn = QPushButton("增加")
        self.deleteBtn = QPushButton("删除")
        self.alterBtn = QPushButton("查看")
        self.pa_btns_laylout.addWidget(self.addBtn)
        self.pa_btns_laylout.addWidget(self.deleteBtn)
        self.pa_btns_laylout.addWidget(self.alterBtn)
        self.addBtn.clicked.connect(self.addBtnClicked)
        self.deleteBtn.clicked.connect(self.deleteBtnClicked)
        self.alterBtn.clicked.connect(self.alterBtnClicked)

        # Hlayout2初始化，翻页功能
        self.jumpToLabel = QLabel("跳转到第")
        self.pageEdit = QLineEdit()
        self.pageEdit.setFixedWidth(30)
        s = "/" + str(self.totalPage) + "页"
        self.pageLabel = QLabel(s)
        self.jumpToButton = QPushButton("跳转")
        self.prevButton = QPushButton("前一页")
        self.prevButton.setFixedWidth(60)
        self.backButton = QPushButton("后一页")
        self.backButton.setFixedWidth(60)

        Hlayout = QHBoxLayout()
        Hlayout.addWidget(self.jumpToLabel)
        Hlayout.addWidget(self.pageEdit)
        Hlayout.addWidget(self.pageLabel)
        Hlayout.addWidget(self.jumpToButton)
        Hlayout.addWidget(self.prevButton)
        Hlayout.addWidget(self.backButton)
        widget = QWidget()
        widget.setLayout(Hlayout)
        widget.setFixedWidth(300)
        self.Hlayout2.addWidget(widget)

        # tableView
        # 用户信息
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('database.db')
        self.db.open()
        self.tableView = QTableView()
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只能选中整行
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.func_mappingSignal()
        # self.showPaImage()
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        # self.model = QStandardItemModel()
        # self.tableView.setModel(self.model)
        # self.model = QStandardItemModel(5, 3)  # 创建一个标准的数据源model
        # self.model.setHorizontalHeaderLabels(["id", "姓名", "年龄"])  # 设置表格的表头名称
        # model=self.tableView.model()
        # print(model.itemData(model.index(index.row(), 0)))
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.queryModel = QSqlQueryModel()
        self.tableView.setModel(self.queryModel)
        self.queryModel.setHeaderData(0, Qt.Horizontal, "姓名")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "性别")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "年龄")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "身份证号")

        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.pa_layout)
        self.layout.addLayout(self.Hlayout1)
        self.layout.addWidget(self.tableView)
        self.layout.addLayout(self.pa_btns_laylout)
        self.layout.addLayout(self.Hlayout2)
        self.setLayout(self.layout)
        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)
        self.searchEdit.returnPressed.connect(self.searchButtonClicked)

    def IndexBtnClick(self):
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def func_mappingSignal(self):
        self.tableView.clicked.connect(self.func_test)

    def func_test(self, item):
        # http://www.python-forum.org/viewtopic.php?f=11&t=16817
        cellContent = item.data()
        print(cellContent)  # test
        sf = "You clicked on {0}x{1}".format(item.column(), item.row())
        print(sf)
        # 获取用户名字
        NewIndex = self.tableView.currentIndex().siblingAtColumn(1)
        Name = NewIndex.data()
        self.selected_pa_label.setText("当前选择的用户为：" + Name)
        self.temp_username = Name
        # 获取用户编号
        user_no_index = self.tableView.currentIndex().siblingAtColumn(0)
        self.temp_userno = user_no_index.data()

    def addBtnClicked(self):
        addDialog = addUserDialog(self)
        # addDialog.add_pa_success_signal.connect(self.window.searchButtonClicked)
        addDialog.show()
        addDialog.exec_()
        self.searchButtonClicked()

    def deleteBtnClicked(self):
        if (self.temp_userno == ""):
            print(QMessageBox.warning(self, "警告", "请选择一名用户", QMessageBox.Yes, QMessageBox.Yes))
        else:
            ret = QMessageBox.information(self, "提示", "是否删除用户" + self.temp_username, QMessageBox.Yes, QMessageBox.No)
            if (ret == QMessageBox.Yes):
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName('database.db')
                db.open()
                query = QSqlQuery()
                # 如果已存在，则update Book表的现存量，剩余可借量，不存在，则insert Book表，同时insert buyordrop表
                sql = "SELECT * FROM users WHERE user_no='%s'" % (self.temp_userno)
                query.exec_(sql)
                # 提示不存在
                if not (query.next()):
                    print(QMessageBox.warning(self, "警告", "该用户不存在", QMessageBox.Yes, QMessageBox.Yes))
                    return
                else:
                    sql = "DELETE FROM users WHERE user_no='%s'" % (self.temp_userno)
                    query.exec_(sql)
                    db.commit()
                    print(QMessageBox.information(self, "提示", "删除成功，用户" + self.temp_username + "已删除", QMessageBox.Yes,
                                                  QMessageBox.Yes))
                    self.temp_userno = ""
                    self.temp_username = ""
                    self.selected_pa_label.setText("当前选择的用户为：")
        self.searchButtonClicked()

    def alterBtnClicked(self):
        # addDialog.add_pa_success_signal.connect(self.window.searchButtonClicked)
        self.alterDialog.setNo(self.temp_userno)
        self.alterDialog.fillContent()
        self.alterDialog.show()
        self.alterDialog.exec_()
        self.searchButtonClicked()

    # 展示图片
    # def showPaImage(self):
    #     # imageItem = QStandardItem(QIcon("pa_head/pa_0"))
    #     image_path="pa_head/pa_0"
    #     imageItem = QtGui.QPixmap(image_path).scaled(300, 300)
    #     img = mping.imread('path')  # 相对路径
    #     self.tableView.setItem(0, 6, imageItem)
    # 查询
    def recordQuery(self, index):
        queryCondition = ""
        conditionChoice = self.condisionComboBox.currentText()
        if (conditionChoice == "按用户名查询"):
            conditionChoice = 'user_name'

        if (self.searchEdit.text() == ""):
            queryCondition = "select * from users"
            self.queryModel.setQuery(queryCondition)
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "页"
            self.pageLabel.setText(label)
            queryCondition = (
                        "select * from users ORDER BY %s  limit %d,%d " % (conditionChoice, index, self.pageRecord))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return

        # 得到模糊查询条件
        temp = self.searchEdit.text()
        s = '%'
        for i in range(0, len(temp)):
            s = s + temp[i] + "%"
        queryCondition = ("SELECT * FROM users WHERE %s LIKE '%s' ORDER BY %s " % (
            conditionChoice, s, conditionChoice))
        self.queryModel.setQuery(queryCondition)
        self.totalRecord = self.queryModel.rowCount()
        # 当查询无记录时的操作
        if (self.totalRecord == 0):
            print(QMessageBox.information(self, "提醒", "查询无记录", QMessageBox.Yes, QMessageBox.Yes))
            queryCondition = "select * from users"
            self.queryModel.setQuery(queryCondition)
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "页"
            self.pageLabel.setText(label)
            queryCondition = (
                        "select * from users ORDER BY %s  limit %d,%d " % (conditionChoice, index, self.pageRecord))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        label = "/" + str(int(self.totalPage)) + "页"
        self.pageLabel.setText(label)
        queryCondition = ("SELECT * FROM users WHERE %s LIKE '%s' ORDER BY %s LIMIT %d,%d " % (
            conditionChoice, s, conditionChoice, index, self.pageRecord))
        self.queryModel.setQuery(queryCondition)
        self.setButtonStatus()
        return

    def setButtonStatus(self):
        if (self.currentPage == self.totalPage):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(False)
        if (self.currentPage == 1):
            self.backButton.setEnabled(True)
            self.prevButton.setEnabled(False)
        if (self.currentPage < self.totalPage and self.currentPage > 1):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(True)

    # 得到记录数
    def getTotalRecordCount(self):
        self.queryModel.setQuery("SELECT * FROM users")
        self.totalRecord = self.queryModel.rowCount()
        return

    # 得到总页数
    def getPageCount(self):
        self.getTotalRecordCount()
        # 上取整
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        return

    # 点击查询
    def searchButtonClicked(self):
        self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        self.getPageCount()
        s = "/" + str(int(self.totalPage)) + "页"
        self.pageLabel.setText(s)
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 向前翻页

    def prevButtonClicked(self):
        self.currentPage -= 1
        if (self.currentPage <= 1):
            self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 向后翻页

    def backButtonClicked(self):
        self.currentPage += 1
        if (self.currentPage >= int(self.totalPage)):
            self.currentPage = int(self.totalPage)
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 点击跳转

    def jumpToButtonClicked(self):
        if (self.pageEdit.text().isdigit()):
            self.currentPage = int(self.pageEdit.text())
            if (self.currentPage > self.totalPage):
                self.currentPage = self.totalPage
            if (self.currentPage <= 1):
                self.currentPage = 1
        else:
            self.currentPage = 1
        index = (self.currentPage - 1) * self.pageRecord
        self.pageEdit.setText(str(self.currentPage))
        self.recordQuery(index)
        return

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return

class LoginDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(LoginDialog, self).__init__(*args, **kwargs)

        self.resize(900,600)
        self.setWindowTitle("欢迎登陆康复系统")
        self.signUpLabel = QLabel("失语症康复训练系统")
        self.signUpLabel.setAlignment(Qt.AlignCenter)
        self.signUpLabel.setFixedWidth(400)
        self.signUpLabel.setFixedHeight(100)
        font = QFont()
        font.setPixelSize(36)
        lineEditFont = QFont()
        lineEditFont.setPixelSize(16)
        self.signUpLabel.setFont(font)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.signUpLabel, Qt.AlignHCenter)
        self.setLayout(self.layout)
        # table
        self.formlayout = QFormLayout()
        font.setPixelSize(18)

        # row 1
        self.namelabel=QLabel("姓    名: ")
        self.namelabel.setFont(font)
        self.nameinput = QLineEdit()
        self.nameinput.setFixedWidth(180)
        self.nameinput.setFixedHeight(32)
        self.nameinput.setFont(lineEditFont)
        self.nameinput.setMaxLength(10)
        self.formlayout.addRow(self.namelabel, self.nameinput)
        # row 2
        self.passlabel = QLabel("密    码: ")
        self.passlabel.setFont(font)
        self.passinput = QLineEdit()
        self.passinput.setEchoMode(QLineEdit.Password)
        self.passinput.setFixedWidth(180)
        self.passinput.setFixedHeight(32)
        self.passinput.setFont(lineEditFont)
        self.passinput.setMaxLength(20)
        self.formlayout.addRow(self.passlabel, self.passinput)

        self.QBtn = QPushButton("登 录")
        self.QBtn.setFixedWidth(120)
        self.QBtn.setFixedHeight(30)
        self.QBtn.setFont(font)
        self.QBtn.clicked.connect(self.login)
        self.formlayout.addRow("", self.QBtn)

        title = QLabel("Login")
        font = title.font()
        font.setPointSize(16)
        title.setFont(font)

        widget = QWidget()
        widget.setLayout(self.formlayout)
        widget.setFixedHeight(250)
        widget.setFixedWidth(300)
        self.Hlayout = QHBoxLayout()
        self.Hlayout.addWidget(widget, Qt.AlignCenter)
        widget = QWidget()
        widget.setLayout(self.Hlayout)
        self.layout.addWidget(widget, Qt.AlignHCenter)
        #layout.addWidget(title)
        #layout.addWidget(self.nameinput)
        #layout.addWidget(self.passinput)
        #layout.addWidget(self.QBtn)
        #self.setLayout(layout)

    def login(self):
        username = ""
        username = self.nameinput.text()
        password = ""
        password = self.passinput.text()
        exist=0
        try:
            self.conn = sqlite3.connect("database.db")
            self.c = self.conn.cursor()
            result = self.c.execute("SELECT * from users WHERE user_name=? AND user_pw=?" ,(username,password))
            row = result.fetchone()
            # print(row)
            if not row is None:
                self.accept()
            else:
                QMessageBox.warning(QMessageBox(), 'Error', 'Could not Find student from the database.')
            self.conn.commit()
            self.c.close()
            self.conn.close()
        except Exception:
            return

class IndexWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(IndexWindow, self).__init__(*args, **kwargs)
        self.resize(700, 500)
        self.setWindowTitle("欢迎使用康复训练系统")
        # 查询模型
        self.queryModel = None
        # 数据表
        self.tableView = None
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecord = 0
        # 每页数据数
        self.pageRecord = 10
        # 当前患者名字
        self.temp_paname=""
        # 当前患者编号
        self.temp_pano=""
        # 初始化修改窗口
        self.alterDialog=alterPaDialog()
        self.userManageWindow = ManageWindow()
        self.trainWindow =TrainWindow()
        self.setUpUI()

    def setUpUI(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        # 添加sql语句
        self.c.close()
        self.setFixedSize(960, 700)

        #选择患者
        self.layout = QVBoxLayout()
        self.indexlayout=QHBoxLayout()
        self.pa_layout=QHBoxLayout()
        self.Hlayout1 = QHBoxLayout()
        self.pa_btns_laylout=QHBoxLayout()
        self.Hlayout2 = QHBoxLayout()

        self.titlelabel=QLabel("康复训练")
        font = self.titlelabel.font()
        font.setPointSize(25)
        font.setBold(1)
        font.setFamily("黑体")
        self.titlelabel.setFont(font)
        index_btn_len=150
        self.IndexBtn = QtWidgets.QPushButton("首页")
        self.IndexBtn.setObjectName('index_button')
        self.IndexBtn.setFixedWidth(index_btn_len)
        self.trainMissionBtn = QtWidgets.QPushButton("训练任务")
        self.trainMissionBtn.setObjectName('index_button')
        self.trainMissionBtn.setFixedWidth(index_btn_len)
        self.user_manage_btn = QtWidgets.QPushButton("用户管理")
        self.user_manage_btn.setObjectName('index_button')
        self.user_manage_btn.setFixedWidth(index_btn_len)
        self.index_btn_4 = QtWidgets.QPushButton("系统管理")
        self.index_btn_4.setObjectName('index_button')
        self.index_btn_4.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.exitBtn = QtWidgets.QPushButton("退出系统")
        self.exitBtn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.index_btn_4)
        self.indexlayout.addWidget(self.exitBtn)
        # 导航栏按钮
        self.exitBtn.clicked.connect(self.exitBtnClick)
        self.trainMissionBtn.clicked.connect(self.trainMissionBtnClick)
        
        # 添加导航栏按钮功能
        self.user_manage_btn.clicked.connect(self.userManageBtnClicked)
        # 当前已选择患者

        self.selected_pa_label=QLabel("当前选择的患者为：无")
        self.pa_layout.addWidget(self.selected_pa_label)

        # Hlayout1，查询功能
        self.searchEdit = QLineEdit()
        self.searchEdit.setFixedHeight(32)
        font = QFont()
        font.setPixelSize(15)
        self.searchEdit.setFont(font)

        self.searchButton = QPushButton("查询")
        self.searchButton.setFixedHeight(32)
        self.searchButton.setFont(font)
        self.searchButton.setIcon(QIcon(QPixmap("./images/search.png")))

        self.condisionComboBox = QComboBox()
        searchCondision = ['按姓名查询', '按身份证号查询']
        self.condisionComboBox.setFixedHeight(32)
        self.condisionComboBox.setFont(font)
        self.condisionComboBox.addItems(searchCondision)

        self.Hlayout1.addWidget(self.searchEdit)
        self.Hlayout1.addWidget(self.searchButton)
        self.Hlayout1.addWidget(self.condisionComboBox)

        # 增删改
        self.addBtn=QPushButton("增加")
        self.deleteBtn = QPushButton("删除")
        self.alterBtn = QPushButton("查看")
        self.pa_btns_laylout.addWidget(self.addBtn)
        self.pa_btns_laylout.addWidget(self.deleteBtn)
        self.pa_btns_laylout.addWidget(self.alterBtn)
        self.addBtn.clicked.connect(self.addBtnClicked)
        self.deleteBtn.clicked.connect(self.deleteBtnClicked)
        self.alterBtn.clicked.connect(self.alterBtnClicked)

        # Hlayout2初始化，翻页功能
        self.jumpToLabel = QLabel("跳转到第")
        self.pageEdit = QLineEdit()
        self.pageEdit.setFixedWidth(30)
        s = "/" + str(self.totalPage) + "页"
        self.pageLabel = QLabel(s)
        self.jumpToButton = QPushButton("跳转")
        self.prevButton = QPushButton("前一页")
        self.prevButton.setFixedWidth(60)
        self.backButton = QPushButton("后一页")
        self.backButton.setFixedWidth(60)

        Hlayout = QHBoxLayout()
        Hlayout.addWidget(self.jumpToLabel)
        Hlayout.addWidget(self.pageEdit)
        Hlayout.addWidget(self.pageLabel)
        Hlayout.addWidget(self.jumpToButton)
        Hlayout.addWidget(self.prevButton)
        Hlayout.addWidget(self.backButton)
        widget = QWidget()
        widget.setLayout(Hlayout)
        widget.setFixedWidth(300)
        self.Hlayout2.addWidget(widget)

        # tableView
        # 患者信息
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('database.db')
        self.db.open()
        self.tableView = QTableView()
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)  # 设置只能选中整行
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置只能选中一行
        self.func_mappingSignal()
        # self.showPaImage()
        index = self.tableView.currentIndex()  # 取得当前选中行的index
        # self.model = QStandardItemModel()
        # self.tableView.setModel(self.model)
        # self.model = QStandardItemModel(5, 3)  # 创建一个标准的数据源model
        # self.model.setHorizontalHeaderLabels(["id", "姓名", "年龄"])  # 设置表格的表头名称
        # model=self.tableView.model()
        # print(model.itemData(model.index(index.row(), 0)))
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.queryModel = QSqlQueryModel()
        self.tableView.setModel(self.queryModel)
        self.queryModel.setHeaderData(0, Qt.Horizontal, "姓名")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "性别")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "年龄")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "身份证号")


        self.layout.addLayout(self.indexlayout)
        self.layout.addLayout(self.pa_layout)
        self.layout.addLayout(self.Hlayout1)
        self.layout.addWidget(self.tableView)
        self.layout.addLayout(self.pa_btns_laylout)
        self.layout.addLayout(self.Hlayout2)
        self.setLayout(self.layout)
        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)
        self.searchEdit.returnPressed.connect(self.searchButtonClicked)

    def userManageBtnClicked(self):
        self.userManageWindow.showMaximized()
        self.userManageWindow.searchButtonClicked()
        self.close()

    def trainMissionBtnClick(self):
        if not (self.temp_pano==""):
            self.trainWindow.showFullScreen()
            self.trainWindow.setNo(self.temp_pano)
            self.close()
        else:
            print(QMessageBox.warning(self, "警告", "请选择一名患者", QMessageBox.Yes, QMessageBox.Yes))

    def func_mappingSignal(self):
        self.tableView.clicked.connect(self.func_test)

    def func_test(self, item):
        # http://www.python-forum.org/viewtopic.php?f=11&t=16817
        cellContent = item.data()
        print(cellContent)  # test
        sf = "You clicked on {0}x{1}".format(item.column(), item.row())
        print(sf)
        # 获取患者名字
        NewIndex = self.tableView.currentIndex().siblingAtColumn(1)
        Name = NewIndex.data()
        self.selected_pa_label.setText("当前选择的患者为：" + Name)
        self.temp_paname =Name
        # 获取患者编号
        pa_no_index = self.tableView.currentIndex().siblingAtColumn(0)
        self.temp_pano = pa_no_index.data()

    def addBtnClicked(self):
        addDialog = addPaDialog(self)
        # addDialog.add_pa_success_signal.connect(self.window.searchButtonClicked)
        addDialog.show()
        addDialog.exec_()
        self.searchButtonClicked()
    def deleteBtnClicked(self):
        if(self.temp_pano==""):
            print(QMessageBox.warning(self, "警告", "请选择一名患者", QMessageBox.Yes, QMessageBox.Yes))
        else:
            ret=QMessageBox.information(self, "提示", "是否删除患者"+self.temp_paname, QMessageBox.Yes, QMessageBox.No)
            if(ret==QMessageBox.Yes):
                db = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName('database.db')
                db.open()
                query = QSqlQuery()
                # 如果已存在，则update Book表的现存量，剩余可借量，不存在，则insert Book表，同时insert buyordrop表
                sql = "SELECT * FROM patient WHERE pa_no='%s'" % (self.temp_pano)
                query.exec_(sql)
                # 提示不存在
                if not (query.next()):
                    print(QMessageBox.warning(self, "警告", "该患者不存在", QMessageBox.Yes, QMessageBox.Yes))
                    return
                else:
                    sql = "DELETE FROM patient WHERE pa_no='%s'" % (self.temp_pano)
                    query.exec_(sql)
                    db.commit()
                    print(QMessageBox.information(self, "提示", "删除成功，患者"+self.temp_paname+"已删除", QMessageBox.Yes, QMessageBox.Yes))
                    self.temp_pano=""
                    self.temp_paname=""
                    self.selected_pa_label.setText("当前选择的患者为：")
        self.searchButtonClicked()
    def alterBtnClicked(self):
        # addDialog.add_pa_success_signal.connect(self.window.searchButtonClicked)
        self.alterDialog.setNo(self.temp_pano)
        self.alterDialog.fillContent()
        self.alterDialog.show()
        self.alterDialog.exec_()
        self.searchButtonClicked()
    #展示图片
    # def showPaImage(self):
    #     # imageItem = QStandardItem(QIcon("pa_head/pa_0"))
    #     image_path="pa_head/pa_0"
    #     imageItem = QtGui.QPixmap(image_path).scaled(300, 300)
    #     img = mping.imread('path')  # 相对路径
    #     self.tableView.setItem(0, 6, imageItem)
    # 查询
    def recordQuery(self, index):
        queryCondition = ""
        conditionChoice = self.condisionComboBox.currentText()
        if (conditionChoice == "按姓名查询"):
            conditionChoice = 'pa_name'
        elif (conditionChoice == "按身份证号查询"):
            conditionChoice = 'pa_id'

        if (self.searchEdit.text() == ""):
            queryCondition = "select * from patient"
            self.queryModel.setQuery(queryCondition)
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "页"
            self.pageLabel.setText(label)
            queryCondition = ("select * from patient ORDER BY %s  limit %d,%d " % (conditionChoice,index, self.pageRecord))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return

        # 得到模糊查询条件
        temp = self.searchEdit.text()
        s = '%'
        for i in range(0, len(temp)):
            s = s + temp[i] + "%"
        queryCondition = ("SELECT * FROM patient WHERE %s LIKE '%s' ORDER BY %s " % (
            conditionChoice, s,conditionChoice))
        self.queryModel.setQuery(queryCondition)
        self.totalRecord = self.queryModel.rowCount()
        # 当查询无记录时的操作
        if(self.totalRecord==0):
            print(QMessageBox.information(self,"提醒","查询无记录",QMessageBox.Yes,QMessageBox.Yes))
            queryCondition = "select * from patient"
            self.queryModel.setQuery(queryCondition)
            self.totalRecord = self.queryModel.rowCount()
            self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
            label = "/" + str(int(self.totalPage)) + "页"
            self.pageLabel.setText(label)
            queryCondition = ("select * from patient ORDER BY %s  limit %d,%d " % (conditionChoice,index, self.pageRecord))
            self.queryModel.setQuery(queryCondition)
            self.setButtonStatus()
            return
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        label = "/" + str(int(self.totalPage)) + "页"
        self.pageLabel.setText(label)
        queryCondition = ("SELECT * FROM patient WHERE %s LIKE '%s' ORDER BY %s LIMIT %d,%d " % (
            conditionChoice, s, conditionChoice,index, self.pageRecord))
        self.queryModel.setQuery(queryCondition)
        self.setButtonStatus()
        return

    def setButtonStatus(self):
        if (self.currentPage == self.totalPage):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(False)
        if (self.currentPage == 1):
            self.backButton.setEnabled(True)
            self.prevButton.setEnabled(False)
        if (self.currentPage < self.totalPage and self.currentPage > 1):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(True)

    # 得到记录数
    def getTotalRecordCount(self):
        self.queryModel.setQuery("SELECT * FROM patient")
        self.totalRecord = self.queryModel.rowCount()
        return

    # 得到总页数
    def getPageCount(self):
        self.getTotalRecordCount()
        # 上取整
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        return

    # 点击查询
    def searchButtonClicked(self):
        self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        self.getPageCount()
        s = "/" + str(int(self.totalPage)) + "页"
        self.pageLabel.setText(s)
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 向前翻页

    def prevButtonClicked(self):
        self.currentPage -= 1
        if (self.currentPage <= 1):
            self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 向后翻页

    def backButtonClicked(self):
        self.currentPage += 1
        if (self.currentPage >= int(self.totalPage)):
            self.currentPage = int(self.totalPage)
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

        # 点击跳转

    def jumpToButtonClicked(self):
        if (self.pageEdit.text().isdigit()):
            self.currentPage = int(self.pageEdit.text())
            if (self.currentPage > self.totalPage):
                self.currentPage = self.totalPage
            if (self.currentPage <= 1):
                self.currentPage = 1
        else:
            self.currentPage = 1
        index = (self.currentPage - 1) * self.pageRecord
        self.pageEdit.setText(str(self.currentPage))
        self.recordQuery(index)
        return

    def exitBtnClick(self):
        ret = QMessageBox.information(self, "提示", "是否退出系统?", QMessageBox.Yes, QMessageBox.No)
        if (ret == QMessageBox.Yes):
            sys.exit(app.exec_())
        else:
            return


app = QApplication(sys.argv)
passdlg = LoginDialog()
if(passdlg.exec_() == QDialog.Accepted):
    window = IndexWindow()
    window.showFullScreen()
    window.searchButtonClicked()
    sys.exit(app.exec_())
# window = WordWindow()
# window.showFullScreen()
# sys.exit(app.exec_())