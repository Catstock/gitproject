from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys,sqlite3



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
        self.pageRecord = 20
        # 当前用户名字
        self.temp_username = ""
        # 当前用户编号
        self.temp_userno = ""
        # 初始化修改窗口
        from alteruser import alterUserDialog
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
        self.trainMissionBtn.hide()
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
        self.sys_manage_btn.clicked.connect(self.sysManageBtnClicked)

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
        from t_main import IndexWindow
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
        from adduser import addUserDialog
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
        if (self.temp_userno == ""):
            print(QMessageBox.warning(self, "警告", "请选择一名用户", QMessageBox.Yes, QMessageBox.Yes))
        else:
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

    def sysManageBtnClicked(self):
        from sys_management import SysManageWindow
        self.sysManageWindow=SysManageWindow()
        self.sysManageWindow.searchButtonClicked()
        self.sysManageWindow.showFullScreen()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManageWindow()
    window.showFullScreen()
    window.searchButtonClicked()
    sys.exit(app.exec_())