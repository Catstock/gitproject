import subprocess
import sys
import time

import numpy as np
import cv2
from PyQt5.QtCore import QUrl, QRect
from PyQt5.QtGui import QImage, QPixmap, QRegion, QPainter, QFont
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, \
    QDesktopWidget, QFileDialog
from skimage.viewer.qt import Qt
import os

from PyQt5.QtCore import QThread

class CroppingThread(QThread):
    def __init__(self, parent=None,filepath=""):
        super().__init__(parent)
        self.main_window = parent
        self.file_path = filepath

    def run(self):
        self.main_window.setCropping()
        self.main_window.cropPic()
        self.main_window.setCropped(self.file_path)

class CameraWindow(QMainWindow):
    def __init__(self,parent=None,pano=""):
        super().__init__(parent)
        # # 获取桌面的大小
        # desktop_size = QDesktopWidget().availableGeometry().size()
        # # 将窗口大小设置为桌面大小
        # self.resize(desktop_size)
        # self.resizeEvent(self.resize(desktop_size))
        self.pa_no=pano
        self.setWindowTitle('拍照')
        self.image_path = '../pa_head/pa_2.jpg'
        self.pic_height=500
        self.pic_width=self.pic_height*2
        self.cap_height=350
        self.cap_width=350
        self.current_image=None
        font = QFont()
        font.setPixelSize(50)
        # 创建一个垂直布局管理器
        self.layout = QVBoxLayout()

        # 创建一个水平布局管理器，用于放置摄像头按钮和拍照按钮
        self.button_layout = QHBoxLayout()
        # 创建一个摄像头按钮，并将其添加到水平布局管理器中
        self.import_button = QPushButton('从本地导入')
        self.import_button.setFont(font)
        self.import_button.clicked.connect(self.import_image)
        self.button_layout.addWidget(self.import_button)
        # 创建一个拍照按钮，并将其添加到水平布局管理器中
        self.capture_button = QPushButton('拍照')
        self.capture_button.setFont(font)
        self.capture_button.clicked.connect(self.capture_image)
        self.button_layout.addWidget(self.capture_button)
        # 创建一个保存按钮，并将其添加到水平布局管理器中
        self.save_button = QPushButton('保存并裁剪照片')
        self.save_button.setFont(font)
        self.save_button.clicked.connect(self.save_image)
        self.button_layout.addWidget(self.save_button)

        # 创建一个QLabel控件，并将其添加到垂直布局管理器中
        self.image_layout=QHBoxLayout()
        self.image_label = QLabel()
        self.image_label.setFixedWidth(self.pic_width)
        self.image_label.setFixedHeight(self.pic_height)
        # 创建一个QCamera对象和一个QCameraImageCapture对象
        self.camera = QCamera()
        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.process_image)
        # 将QCameraViewfinder设置为QCamera的视图查看器
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.setFixedHeight(self.pic_height)
        self.viewfinder.setFixedWidth(self.pic_width)
        self.camera.setViewfinder(self.viewfinder)
        self.image_layout.addWidget(self.viewfinder)
        self.image_layout.addWidget(self.image_label)

        # Qlabel用作放截图
        self.cap_layout = QHBoxLayout()
        self.cap_label = QLabel()
        self.cap_label.setFixedWidth(self.pic_width)
        self.cap_label.setFixedHeight(self.pic_height)
        self.cap_layout.addWidget(self.cap_label)
        # 保存状态
        self.save_label=QLabel("未保存")
        self.save_label.setFont(font)

        #包含imagelayout和caplayout
        self.ic_layout=QHBoxLayout()
        self.ic_layout.addLayout(self.image_layout)
        self.ic_layout.addLayout(self.cap_layout)

        #self.image_label.setFixedWidth()
        self.layout.addLayout(self.ic_layout)
        self.layout.addWidget(self.save_label)

        # 将水平布局管理器添加到垂直布局管理器中
        self.layout.addLayout(self.button_layout)

        # 创建一个QWidget对象，并将垂直布局管理器添加到其中
        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        # 将QWidget对象设置为QMainWindow的中央窗口部件
        self.setCentralWidget(self.widget)
        self.showMaximized()
        self.open_camera()

    def set_main_window(self, main_window):
        self.main_window = main_window

    def closeEvent(self, event):
        self.camera.stop()
        print("close")
        # 在关闭摄像头窗口时返回主窗口
        self.main_window.show()
        event.accept()

    def open_camera(self):
        # 打开摄像头
        try:
            camera_info = QCameraInfo.defaultCamera()
            if camera_info:
                self.camera.setCaptureMode(QCamera.CaptureStillImage)
                self.camera.start()
                #self.setCentralWidget(self.viewfinder)

                viewport_rect = QRect((self.pic_width-self.cap_width)/2, (self.pic_height-self.cap_height)/2, self.cap_width, self.cap_height)
                mask = QRegion(viewport_rect, QRegion.Rectangle)
                self.viewfinder.setMask(mask)
                # 将背景设置为透明
                self.viewfinder.setStyleSheet("background-color: transparent;")

                # 获取mask之后的截图
                pixmap = self.viewfinder.grab()

                # 将截图设置为QLabel的背景
                self.image_label.setStyleSheet(f"background-image: url({pixmap.toImage()});")

                # 设置QCameraViewfinder的大小为mask后的大小
                self.viewfinder.resize(mask.boundingRect().size())

                # 计算image_label的大小
                image_size = self.image_label.sizeHint()
                image_size.setWidth(self.pic_width)
                image_size.setHeight(self.pic_height)
                self.image_label.resize(image_size)

                # 设置layout的大小约束为QLayout.SetFixedSize
                self.image_layout.setSizeConstraint(self.image_layout.SetFixedSize)

                # 使用布局管理器调整QCameraViewfinder的大小
                self.image_layout.removeWidget(self.image_label)
                self.viewfinder.setParent(None)
                self.viewfinder.setParent(self)
                self.image_layout.addWidget(self.viewfinder)
                # self.viewfinder.setGeometry(viewport_rect)
                self.showMaximized()
        except Exception as e:
            print(f'Error: {e}')

    def import_image(self):
        try:
            # 打开文件选择对话框并返回选中的文件路径
            file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '',
                                                       'Images (*.png *.xpm *.jpg *.bmp)')
            if file_path:
                # 加载图片到QLabel控件中
                pixmap = QPixmap(file_path)
                self.cap_label.setPixmap(pixmap)
                self.setUnSave()
        except Exception as e:
            print(f'Error: {e}')

    def capture_image(self):
        # 拍摄照片
        try:
            pixmap = QPixmap(self.viewfinder.size())
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            mask = self.viewfinder.mask()
            painter.setClipRegion(mask)
            painter.drawPixmap(self.viewfinder.rect(), self.viewfinder.grab())
            painter.end()

            # 使用 copy 方法获取 mask 区域的图像
            rect = mask.boundingRect()
            pixmap = pixmap.copy(rect)
            pixmap.save("pa_head/temp.jpg")

            self.cap_label.setStyleSheet(f"background-image: url({pixmap.toImage()});")
            self.cap_label.setPixmap(pixmap)
            self.setUnSave()
        except Exception as e:
            print(f'Error: {e}')

    def process_image(self):
        # 在QLabel控件中显示拍摄的照片
        try:
            image = self.image_capture.availableImageData()
            print(image)
            # 将图像数据转换为NumPy数组
            np_image = np.frombuffer(image.data, dtype=np.uint8)
            # 如果数据不是NumPy数组，则将其转换为NumPy数组
            if not isinstance(np_image, np.ndarray):
                np_image = np.array(np_image)
            # 检查图像数据的形状是否为 (height, width, channel)
            if len(np_image.shape) != 3 or np_image.shape[2] != 3:
                raise ValueError('Invalid image shape')
            # 输出图像格式
            print(f"Image format: {np_image.shape}")
            # 将图像从BGR颜色空间转换为RGB颜色空间
            self.current_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f'Error: {e}')

    def save_image(self):
        try:
            # file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.bmp)")
            # 连接数据库
            folder_path="pa_head\pa_"+str(self.pa_no)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # 如果文件夹不存在，则创建文件夹
            file_path=folder_path+"\\000000.jpg"
            if file_path:
                pixmap = self.cap_label.pixmap()
                pixmap.save(file_path)
                self.setSave(file_path)
            self.thread = CroppingThread(self,file_path)
            self.thread.start()
            # self.setCropping()
            # self.cropPic()
            # self.setCropped()
        except Exception as e:
            print(f'Error: {e}')

    def resizeEvent(self, event):
        try:
            # 当窗口大小发生变化时，重新计算QWidget和QCameraViewfinder的大小
            self.widget.resize(self.widget.sizeHint())
            self.viewfinder.updateGeometry()
            QMainWindow.resizeEvent(self, event)
        except Exception as e:
            print(f'Error: {e}')

    def setPaNo(self,new_no):
        self.PaNo=new_no
    def setSave(self,file_path):
        self.save_label.setText("已保存至："+file_path)
    def setUnSave(self):
        self.save_label.setText("未保存")
    def setCropping(self):
        self.save_label.setText("裁剪中...")
    def setCropped(self,file_path):
        self.save_label.setText("裁剪完成,已保存至："+file_path)

    def cropPic(self):

        cmd = "python ../Talking-Face_PC-AVS-main/scripts/align_68.py --folder_path ../PyQt-Sqlite-Project-CURD-master/pa_head/pa_"+self.pa_no
        subprocess.run(cmd, shell=True, check=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())


