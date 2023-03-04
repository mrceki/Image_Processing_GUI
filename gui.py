import cv2
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('mainwindow.ui', self)  # UI dosyasının adı

        self.original_pixmap = None
        self.color_filter = None
        
        self.image_label.setScaledContents(True)
        self.image_label_2.setScaledContents(True)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = cv2.VideoCapture(0)
        self.timer.start(1)

        self.lower_hue = 0
        self.upper_hue = 10

        self.start_button.clicked.connect(self.start_webcam)
        self.stop_button.clicked.connect(self.stop_webcam)

        self.image_label.mousePressEvent = self.get_pixel_color

        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)

        self.image_label.setScaledContents(True)

    def start_webcam(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(1)

        self.stop_button.setEnabled(True)
        self.start_button.setEnabled(False)

    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)




    def get_pixel_color(self, event):
        x = event.pos().x()
        y = event.pos().y()
        pixmap = self.image_label.pixmap()
        if pixmap is not None:
            image = pixmap.toImage()
            color = QColor(image.pixel(x, y))
            self.color_filter = [color.red(), color.green(), color.blue()]
            print("%d ,%d, %d", color.red(), color.green(), color.blue())
            self.update_frame()

    def update_image(self):
        pixmap = self.original_pixmap.copy()
        if self.color_filter is not None:
            red, green, blue = self.color_filter
            image = pixmap.toImage()
            for i in range(pixmap.width()):
                for j in range(pixmap.height()):
                    pixel_color = QColor(image.pixel(i, j))
                    if (pixel_color.red() != red or pixel_color.green() != green or pixel_color.blue() != blue):
                        pixmap.setPixelColor(i, j, QColor(0, 0, 0))
        self.image_label.setPixmap(pixmap)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame  # frame'i self.frame içinde sakla

            # Daire tespiti
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_color = np.array([self.lower_hue, 0, 0])  # renk filtresi için lower_color değeri
            upper_color = np.array([self.upper_hue, 255, 255])  # renk filtresi için upper_color değeri
            mask = cv2.inRange(hsv, lower_color, upper_color)
            res = cv2.bitwise_and(frame, frame, mask=mask)

            # Daire tespiti ve çizimi
            gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                                       param1=200, param2=50, minRadius=0, maxRadius=0)

            # Çemberleri çiz
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

            # Frame'i image_label üzerine yazdır
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qImg))

            # Renk filtresi için frame'i hazırla ve image_label_2 üzerine yazdır
            mask = cv2.inRange(cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV), lower_color, upper_color)
            res = cv2.bitwise_and(self.frame, self.frame, mask=mask)
            res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
            height, width, channel = res.shape
            bytesPerLine = 3 * width
            qImg = QImage(res.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.image_label_2.setPixmap(QPixmap.fromImage(qImg))



app = QApplication([])
window = MainWindow()
window.show()
app.exec_()