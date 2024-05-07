#约定：背景>=800X600 前景<=800X600

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QWidget, QGridLayout, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import os
import shutil
import time
from rembg import remove
import sqlite3
conn = sqlite3.connect('picdb')
conn.execute('CREATE TABLE IF NOT EXISTS pic(name text,timestamp text)')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("monAI-识图训练")
        self.resize(1628, 794)

        self.button = QPushButton("打开图片", self)
        self.button.clicked.connect(self.open_image)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setEnabled(False)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lineEdit_tell = QLineEdit(self)
        self.lineEdit_tell.setPlaceholderText("请告诉我这是什么吧")
        self.lineEdit_tell.textChanged.connect(self.telltext)

        self.buttonbg_submit = QPushButton("点击提交原图/背景", self)
        self.buttonbg_submit.clicked.connect(self.submitbg)
        self.buttonbg_submit.setDisabled(True)

        self.setStyleSheet("QPushButton {"
                         "  background-color: #44CEF6;"
                         "  color: white;"
                         "  border: 1px solid #000000;"
                         "  padding: 10px;"
                         "  font-size: 24px;"
                         "  font-family: 'Microsoft YaHei';"
                         "}"
                         "QPushButton:hover {"
                         "  background-color: #70F3FF;"
                         "}"
                         "QPushButton:pressed {"
                         "  background-color: #4B5CC4;"
                         "  border-style: inset;"
                         "}"
                         "QLabel{background-color:white}"
                         "QLineEdit{font-size: 24px; font-family: 'Microsoft YaHei';}")
        self.button_submit = QPushButton("点击提交去掉背景的图片", self)
        self.button_submit.clicked.connect(self.submit)
        self.button_submit.setDisabled(True)

        layout = QGridLayout()

        layout.addWidget(self.lineEdit, 0, 0)
        layout.addWidget(self.button, 0, 1)
        layout.addWidget(self.label,3,0,1,2)
        layout.addWidget(self.lineEdit_tell, 4, 0, 1, 2)
        layout.addWidget(self.buttonbg_submit, 5, 0)
        layout.addWidget(self.button_submit, 5, 1)
        #设置列宽一致
        colSize = 100
        for col in range(layout.columnCount()):
            layout.setColumnStretch(col, 1)
            layout.setColumnMinimumWidth(col, colSize)


        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "",
                                                   "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.lineEdit.setText(file_name)
            img1 = cv2.imread(file_name)
            img2_ori = cv2.imread(file_name)
            #边界填充
            height, width = img2_ori.shape[:2]
            print(height)
            print(width)
            if height<600 and width <800:
                top, bottom, left, right = int((600-height)/2), int((600-height)/2), int((800-width)/2), int((800-width)/2)
                img1 = cv2.copyMakeBorder(img1, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                img2_ori = cv2.copyMakeBorder(img2_ori, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

            #rembg去掉背景后的图片是4通道，含透明度，转成一致的通道才能堆叠
            img2_2 = remove(img2_ori)
            img2_3 = cv2.cvtColor(img2_2, cv2.COLOR_RGBA2RGB)
            #原图创建4通道副本

            img1_2 = cv2.cvtColor(img1, cv2.COLOR_BGR2BGRA)

            cv2.imwrite('tmpbg.png', img1_2)
            cv2.imwrite("tmp.png", img2_2)
            if img1 is not None:
                # 水平堆叠
                img = np.hstack((img1, img2_3))
                height, width, channel = img.shape
                bytesPerLine = 3 * width
                qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                self.label.setPixmap(QPixmap.fromImage(qImg))




    def telltext(self):
        tell = self.lineEdit_tell.text()
        if tell:
            self.button_submit.setEnabled(True)
            self.buttonbg_submit.setEnabled(True)
        else:
            self.button_submit.setDisabled(True)
            self.buttonbg_submit.setDisabled(True)

    def submit(self):
        tell = self.lineEdit_tell.text()
        timestamp = str(int(time.time()))
        if tell :
            path = "pic"
            if os.path.exists(path):
                print("")
            else:
                os.makedirs(path)
            shutil.copyfile("tmp.png", ".\\pic\\" + tell + "-" + timestamp + ".png")
            entities = (tell, timestamp)
            self.sql_insert(conn,entities)
            reply = QMessageBox.question(self, '提交成功', '好的，知道了', QMessageBox.Ok)

    def submitbg(self):
        tell = self.lineEdit_tell.text()
        tellbg = tell + "背景"
        timestamp = str(int(time.time()))
        if tell :
            path = "pic"
            if os.path.exists(path):
                print("")
            else:
                os.makedirs(path)
            shutil.copyfile("tmpbg.png", ".\\pic\\" + tellbg + "-" + timestamp + ".png")
            entities = (tellbg, timestamp)
            self.sql_insert(conn,entities)
            reply = QMessageBox.question(self, '提交成功', '好的，知道了', QMessageBox.Ok)


    def sql_insert(self,conn,entities):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pic(name, timestamp) VALUES(?, ?)',entities)
        cursor.close()
        conn.commit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())