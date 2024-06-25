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
    QDesktopWidget, QFileDialog, QSizePolicy, QDialog
from skimage.viewer.qt import Qt
import os

from PyQt5.QtCore import QThread

class PreCameraWindow(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        # # 获取桌面的大小
        # desktop_size = QDesktopWidget().availableGeometry().size()
        # # 将窗口大小设置为桌面大小
        # self.resize(desktop_size)
        # self.resizeEvent(self.resize(desktop_size))
        self.setWindowTitle('校准摄像头')
        self.pic_height=500*1.7
        self.pic_width=self.pic_height*2
        self.cap_height=350*1.7
        self.cap_width=350*1.7
        self.current_image=None
        font = QFont()
        font.setPixelSize(30)
        # 创建一个垂直布局管理器
        self.layout = QVBoxLayout()

        # 创建一个水平布局管理器，用于放置摄像头按钮和拍照按钮
        self.button_layout = QHBoxLayout()
        # 创建一个确认按钮，并将其添加到水平布局管理器中
        self.import_button = QPushButton('确认已校准摄像头')
        self.import_button.clicked.connect(lambda: self.close_clicked())
        self.import_button.setFont(font)
        self.button_layout.addWidget(self.import_button)

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


        self.tip_label=QLabel("请校准摄像头，使头像完整地出现在画面中！")
        font=QFont()
        font.setPixelSize(40)
        font.setBold(1)
        self.tip_label.setFont(font)
        self.tip_label.setStyleSheet("color: red;")
        #self.image_label.setFixedWidth()
        self.layout.addWidget(self.tip_label)
        self.layout.addLayout(self.image_layout)
        # 将水平布局管理器添加到垂直布局管理器中
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)
        self.showMaximized()
        self.open_camera()

    def closeEvent(self, event=None):
        # 在关闭摄像头窗口时返回主窗口
        self.main_window.show()
        self.camera.stop()
        if event:
            event.accept()

    def close_clicked(self):
        self.camera.stop()
        self.closeEvent()
        self.close()

    def open_camera(self):
        # 打开摄像头
        try:
            camera_info = QCameraInfo.defaultCamera()
            if camera_info:
                self.camera.setCaptureMode(QCamera.CaptureStillImage)
                self.camera.start()

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

    def set_main_window(self, main_window):
        self.main_window = main_window

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PreCameraWindow()
    window.show()
    sys.exit(app.exec_())


