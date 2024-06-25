from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtPrintSupport import *
import sys, sqlite3, time

from qtpy import QtGui

from addDialog import addPaDialog
from alterDialog import alterPaDialog
from adduser import addUserDialog
from alteruser import alterUserDialog

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
        #随机
        self.is_random=0 # 正序
        #自动
        self.is_auto=0 # 自动
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
        self.sys_manage_btn = QtWidgets.QPushButton("系统管理")
        self.sys_manage_btn.setObjectName('index_button')
        self.sys_manage_btn.setFixedWidth(index_btn_len)
        self.indexlayout.addWidget(self.titlelabel)
        self.indexlayout.addWidget(self.IndexBtn)
        self.indexlayout.addWidget(self.trainMissionBtn)
        self.indexlayout.addWidget(self.user_manage_btn)
        self.indexlayout.addWidget(self.sys_manage_btn)
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
        self.exitBtn.clicked.connect(self.exitBtnClick)
        self.user_manage_btn.clicked.connect(self.userManageBtnClicked)
        self.sys_manage_btn.clicked.connect(self.sysManageBtnClicked)

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
        # 操作方式
        self.mode_layout = QVBoxLayout()
        self.mode_label = QLabel("操作方式")
        self.mode_label.setFont(font)
        self.mode_combo = QComboBox()
        self.modeCondision = ['自动', '手动']
        self.mode_combo.setFixedHeight(50)
        self.mode_combo.addItems(self.modeCondision)
        self.mode_layout.addWidget(self.mode_label)
        self.mode_layout.addWidget(self.mode_combo)
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
        self.task_content_layout.addLayout(self.mode_layout)
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
        from t_main import IndexWindow
        self.mainwindow = IndexWindow()
        self.mainwindow.showFullScreen()
        self.mainwindow.searchButtonClicked()
        self.close()

    def sysManageBtnClicked(self):
        from sys_management import SysManageWindow
        self.sysManageWindow=SysManageWindow()
        self.sysManageWindow.searchButtonClicked()
        self.sysManageWindow.showFullScreen()
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
        if (self.quest_num_edit.text() == ""):
            print(QMessageBox.warning(self, '警告', '请输入一个数字', QMessageBox.Yes, QMessageBox.Yes))
            return
        conditionChoice = self.quest_order_combo.currentText()
        if (conditionChoice == "正序"):
            self.is_random = 0
        elif (conditionChoice == "乱序"):
            self.is_random = 1
        conditionChoice = self.mode_combo.currentText()
        if (conditionChoice == "自动"):
            self.is_auto = 0
        elif (conditionChoice == "手动"):
            self.is_auto = 1
        if (self.task_type_combo.currentText() == "元音训练"):
            from vowel import VowelWindow
            self.vowelwindow = VowelWindow()
            self.vowelwindow.setTaskNum(self.temp_pano, int(self.quest_num_edit.text()),self.is_random,self.is_auto)
            self.vowelwindow.AssignVowel()
            self.vowelwindow.AssignBtns()
            self.vowelwindow.showFullScreen()
            self.close()
        elif (self.task_type_combo.currentText() == "词语训练"):
            from word import WordWindow
            self.wordwindow = WordWindow()
            self.wordwindow.setTaskNum(self.temp_pano, int(self.quest_num_edit.text()),self.is_random,self.is_auto)
            self.wordwindow.AssignWord()
            self.wordwindow.AssignBtns()
            self.wordwindow.showFullScreen()
            self.close()
        elif (self.task_type_combo.currentText() == "连词成句训练"):
            from wordsentence import WSWindow
            self.wswindow = WSWindow()
            self.wswindow.setTaskNum(self.temp_pano, int(self.quest_num_edit.text()),self.is_random,self.is_auto)
            self.wswindow.AssignSentence()
            self.wswindow.AssignBtns()
            self.wswindow.showFullScreen()
            self.close()

    def userManageBtnClicked(self):
        from user_management import ManageWindow
        self.userManageWindow = ManageWindow()
        self.userManageWindow.showFullScreen()
        self.userManageWindow.searchButtonClicked()
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    mainWindow = TrainWindow()
    mainWindow.showFullScreen()
    # mainWindow.show()
    sys.exit(app.exec_())