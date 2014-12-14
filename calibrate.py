import cv2
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QString, QSettings
from calibrateUI import Ui_Calibrate
from qimage2ndarray import array2qimage
import res_rc

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class CalibrateDialog(QDialog, Ui_Calibrate):
    def __init__(self, parent, image):
        QDialog.__init__(self)
        self.setupUi(self)
        self.showImage(image)
        self.cross1 = None
        self.cross2 = None
        self.name_area = None
        self.column_areas = []
        self.showAreas = False
        self.x = 4.0
        self.y = 4.0
        self.current = 0
        self.points = [[4.0,4.0],[4.0,4.0],[4.0,4.0],[4.0,4.0]]
        self.exampleimages = [":/ico/p1.png",":/ico/p2.png",":/ico/p3.png",":/ico/p4.png"]
        self.save.clicked.connect(self.saveCalibration)
        self.prev.setEnabled(False)
        self.next.clicked.connect(self.nextPoint)
        self.prev.clicked.connect(self.prevPoint)
        self.label_y.setText("Point 1 of 4")

        pen = QPen(Qt.yellow)
        self.cross1 = self.scene.addLine(self.x-4.0, self.y, self.x+4.0, self.y, pen)
        self.cross2 = self.scene.addLine(self.x, self.y-4.0, self.x, self.y+4.0, pen)
        self.clickarea.ensureVisible(1,1,5,5)
        
        self.ex = []
        for ex in self.exampleimages:
            example = QGraphicsScene()
            example.addPixmap(QPixmap(_fromUtf8(ex)))
            self.ex.append(example)
        
        self.example.setScene(self.ex[0])
        self.example.show()

    def getAreas(self):
        areas = [[0.0, 0.297],
                 [0.300, 0.370],
                 [0.373, 0.442],
                 [0.520, 0.607],
                 [0.609, 0.665],
                 [0.670, 0.758],
                 [0.760, 0.832]]
        new_areas = []
        x = self.points[3][0]/self.imgw - self.points[2][0]/self.imgw
        for area in areas:
            new_areas.append([(area[0]*x + self.points[2][0]/self.imgw)*self.imgw,
                              (area[1]*x + self.points[2][0]/self.imgw)*self.imgw])
        return new_areas
    
    def toggleAreas(self):
        if self.name_area:
            self.scene.removeItem(self.name_area)
            self.name_area = None
            for item in self.column_areas:
                self.scene.removeItem(item)
                item = None
            self.column_areas = []
            
        self.points[self.current][0] = self.x
        self.points[self.current][1] = self.y
        pen = QPen(QColor(255, 128, 0, 255))
        self.name_area = self.scene.addRect(self.points[0][0], self.points[0][1], self.points[3][0]-self.points[0][0], self.points[1][1]-self.points[0][1], pen)
        self.name_area.setOpacity(0.5)
        
        for area in self.getAreas():
            item = self.scene.addRect(area[0], self.points[2][1], area[1]-area[0], self.points[3][1]-self.points[2][1], pen)
            item.setOpacity(0.5)
            self.column_areas.append(item)

    def saveCalibration(self):
        self.points[self.current][0] = self.x
        self.points[self.current][1] = self.y
        
        res = []
        
        for i in self.points:
            res.append(i[0]/self.imgw)
            res.append(i[1]/self.imgh)
        
        settings = QSettings('seeebek', 'eliteOCR')
        settings.setValue('img_res', [self.imgw, self.imgh])
        settings.setValue('cal_points', res)
        del settings
        self.close()
    
    def nextPoint(self):
        self.points[self.current][0] = self.x
        self.points[self.current][1] = self.y
        self.current += 1

            
        if self.current < len(self.points):
            if self.cross1:
                self.scene.removeItem(self.cross1)
                self.scene.removeItem(self.cross2)
                self.cross1 = None
                self.cross2 = None
            self.x = self.points[self.current][0]
            self.y = self.points[self.current][1]
            pen = QPen(Qt.yellow)
            self.cross1 = self.scene.addLine(self.x-4.0, self.y, self.x+4.0, self.y, pen)
            self.cross2 = self.scene.addLine(self.x, self.y-4.0, self.x, self.y+4.0, pen)
        
        if self.current == len(self.points) - 1:
            self.next.setEnabled(False)
        else:
            self.next.setEnabled(True)
        if self.current > 0:
            self.prev.setEnabled(True)
        else:
            self.prev.setEnabled(False)

        self.label_y.setText("Point %d of 4" % (self.current + 1))
        self.example.setScene(self.ex[self.current])


    def prevPoint(self):
        self.points[self.current][0] = self.x
        self.points[self.current][1] = self.y
        self.current -= 1
        
        if self.current < len(self.points):
            if self.cross1:
                self.scene.removeItem(self.cross1)
                self.scene.removeItem(self.cross2)
                self.cross1 = None
                self.cross2 = None
            self.x = self.points[self.current][0]
            self.y = self.points[self.current][1]
            pen = QPen(Qt.yellow)
            self.cross1 = self.scene.addLine(self.x-4.0, self.y, self.x+4.0, self.y, pen)
            self.cross2 = self.scene.addLine(self.x, self.y-4.0, self.x, self.y+4.0, pen)
        
        if self.current == len(self.points) - 1:
            self.next.setEnabled(False)
        else:
            self.next.setEnabled(True)
        if self.current > 0:
            self.prev.setEnabled(True)
        else:
            self.prev.setEnabled(False)

        self.label_y.setText("Point %d of 4" % (self.current + 1))
        self.example.setScene(self.ex[self.current])
    
    def showImage(self, image):
        origimg = cv2.imread(unicode(image), 0)
        self.imgh, self.imgw = origimg.shape
        
        #cut image if too long to prevent memory errors
        aspect_ratio = float(self.imgw) / (self.imgh)
        if aspect_ratio > 1.78:
            new_w = int(1.77778*self.imgh)
            origimg = origimg[0:self.imgh, (self.imgw - new_w)/2:(self.imgw - new_w)/2 + new_w]
            self.imgh, self.imgw = origimg.shape
        
        self.imgh, self.imgw = origimg.shape
        processedimage = array2qimage(origimg)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        
        self.scene = QGraphicsScene()
        self.pixMapItem = QGraphicsPixmapItem(pix, None, self.scene)
        self.clickarea.setScene(self.scene)
        self.clickarea.show()
        self.pixMapItem.mousePressEvent = self.getPos
    
    def getPos(self, event):
        if self.cross1:
            self.scene.removeItem(self.cross1)
            self.scene.removeItem(self.cross2)
            self.cross1 = None
            self.cross2 = None

        self.x = event.pos().x()
        self.y = event.pos().y()
        
        pen = QPen(Qt.yellow)
        self.cross1 = self.scene.addLine(self.x-4.0, self.y, self.x+4.0, self.y, pen)
        self.cross2 = self.scene.addLine(self.x, self.y-4.0, self.x, self.y+4.0, pen)
        
        if not self.next.isEnabled():
            self.showAreas = True
        
        if self.showAreas:
            self.toggleAreas()