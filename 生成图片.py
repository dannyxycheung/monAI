#todo：1、中文语义分析，直接用整句来拆分分析，降低数据库字段复杂度，用jieba，已简单使用，待继续完善
# 3、搜索分析出的词，看词中是否带有背景两个字，如果有，从结果中随机选一个
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,  QLabel, QWidget, QGridLayout, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import jieba
import logging
jieba.setLogLevel(logging.INFO)
import sqlite3
conn = sqlite3.connect('picdb')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("monAI-生成图片")
        self.resize(825, 687)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
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

        self.lineEdit_req = QLineEdit(self)
        self.lineEdit_req.setPlaceholderText("你要画什么呢？")
        self.lineEdit_req.textChanged.connect(self.reqtext)

        self.button_submit = QPushButton("开始作画", self)
        self.button_submit.clicked.connect(self.submit)
        self.button_submit.setDisabled(True)

        layout = QGridLayout()

        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.lineEdit_req, 1, 0)
        layout.addWidget(self.button_submit, 1, 1)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def cut(self):
        req = self.lineEdit_req.text()
        result = jieba.lcut(req)
        return result

#先读出背景，取背景图，再读出前景，取前景图，然后就合并
    def submit(self):
        req = self.cut()
        #取背景
        for word_back in req:
            cursor = conn.cursor()
            entities = (word_back,)
            try:
                cursor.execute('select * from pic where name = ?||\'背景\' ORDER BY RANDOM() LIMIT 1',
                           entities)
            except sqlite3.Error as e:
                # 如果有异常，输出错误信息
                print(f"Error: {e.args[0]}")
            finally:
                results = cursor.fetchone()
                cursor.close()
                conn.commit()
            if results:
                file_back_name = ".\\pic\\" + results[0] + "-" + results[1] + ".png"
                #数组中删除该元素，跳出循环
                req.remove(entities[0])
                break

        for word in req:
            cursor = conn.cursor()
            entities = (word,)
            try:
                cursor.execute('select * from pic where name = ? ORDER BY RANDOM() LIMIT 1', entities)
            except sqlite3.Error as e:
                # 如果有异常，输出错误信息
                print(f"Error: {e.args[0]}")
            finally:
                results = cursor.fetchone()
                cursor.close()
                conn.commit()
            if results:
                file_name = ".\\pic\\" + results[0] + "-" + results[1] + ".png"
                # 数组中删除该元素，跳出循环
                #req.remove(entities[0])
                break

        if 'file_back_name' in locals() and 'file_name' in locals():
            img1 = cv2.imdecode(np.fromfile(file_back_name, dtype=np.uint8), -1)
            img2 = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), -1)

            rows1, cols1 = img1.shape[:2]
            rows2, cols2 = img2.shape[:2]
            roi = img1[:rows2, :cols2]

            # 创建掩膜
            img2gray = cv2.cvtColor(img2, cv2.COLOR_BGRA2GRAY)
            ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            # 保留除前景外的背景
            img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

            dst = cv2.addWeighted(img1_bg, 1, img2, 1, 0)
            cv2.imwrite('result.png', dst)
            dst1 = cv2.cvtColor(dst, cv2.COLOR_RGBA2RGB)

            height, width, channel = dst1.shape
            bytesPerLine = 3 * width
            qImg = QImage(dst1.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            self.label.setPixmap(QPixmap.fromImage(qImg))

        else:
            if 'file_back_name' not in locals() and 'file_name' not in locals():
                reply = QMessageBox.question(self, '不知道画什么了', '这主意不错，但我理解不了啊，我不知道该画什么了', QMessageBox.Ok)
                return
            if 'file_back_name' in locals():
                img = cv2.imdecode(np.fromfile(file_back_name, dtype=np.uint8), -1)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            if 'file_name' in locals():
                img = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), -1)
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            height, width, channel = img.shape
            bytesPerLine = 3 * width
            qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            self.label.setPixmap(QPixmap.fromImage(qImg))


    def reqtext(self):
        req = self.lineEdit_req.text()
        if req:
            self.button_submit.setEnabled(True)
        else:
            self.button_submit.setDisabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())