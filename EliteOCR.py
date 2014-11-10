import sys
import cv2
import numpy as np
import tesseract
import time, datetime
from os.path import isfile, getctime
from time import gmtime, strftime
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, QString

from eliteOCRGUI import Ui_eliteOCR
from qimage2ndarray import array2qimage
from ocr import *
    
def contBright(value, in_min, in_max):
    """ Adjust brightness and contrast of image provided as array
    in value. Comparable to "Levels" in GIMP.
    """
    value = np.divide(np.subtract(value, in_min), (in_max-in_min))
    value = np.multiply(value, 255.0)
    value = np.clip(value, 0, 255)
    value = value.astype(np.uint8)
    return value
    
def adjustTableImg(img):
    """ Cuts the image of commodities table in three pieces and 
    adjusts brightness and contrast of all pieces to
    aprox. the same level.
    """
    h, w = img.shape
    left = img[0:h, 0:intR(0.4341*w)]
    left = contBright( left, 84.0, 171.0)
    mid = img[0:h, intR(0.4346*w):intR(0.5193*w)]
    mid = contBright( mid, 155.0, 193.0)
    right = img[0:h, intR(0.5198*w):w]
    right = contBright( right, 84.0, 171.0)
    h1, w1 = left.shape
    h2, w2 = mid.shape
    h3, w3 = right.shape
    new = np.zeros((h, w), np.uint8)
    new[:h1, :w1] = left
    new[:h2, w1:w1+w2] = mid
    new[:h3, w1+w2:w1+w2+w3] = right
    return new

class EliteOCR(QMainWindow, Ui_eliteOCR):
    def __init__(self):            
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setupTable()
        self.fields = [self.name, self.sell, self.buy, self.demand_num,
                       self.demand, self.supply_num, self.supply]
        self.canvases = [self.name_img, self.sell_img, self.buy_img,
                         self.demand_img, self.demand_text_img,
                         self.supply_img, self.supply_text_img]
        
        #setup buttons
        self.image_button.clicked.connect(self.selectFile)
        self.save_button.clicked.connect(self.addItemToTable)
        self.skip_button.clicked.connect(self.skipItem)
        self.save_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.export_button.clicked.connect(self.exportTable)
        self.export_button.setEnabled(False)
        
        self.rowcount = 0
        self.OCRline = 0
        self.tablerowcount = 0
    
    def setupTable(self):
        self.result_table.setColumnCount(8)
        self.result_table.setHorizontalHeaderLabels(['name', 'sell', 'buy',
                                                     'demand', 'dem', 'supply',
                                                     'sup', 'timestamp'])
        self.result_table.setColumnHidden(7, True)
        self.result_table.show()
    
    def selectFile(self):
        if not (isfile("./tessdata/big.traineddata") and
                isfile("./tessdata/small.traineddata")):
            QMessageBox.critical(self,"Error", "OCR data not found!"+\
            "\nMake sure the directory tessdata existis and "+\
            "contains big.traineddata and small.traineddata")
            self.close()
            return
        self.path_to_image.setText(QFileDialog.getOpenFileName())
        tmstmp = gmtime(getctime(str(self.path_to_image.text())))
        self.file_tmstmp = str(strftime("%Y-%m-%dT%H:%M", tmstmp))
        if self.makeImages( str(self.path_to_image.text())) == 0:
            return
        self.station = ocr(self.contrast_station_name, "UTF8").strip()
        self.drawStationName()
        self.station_name.setText(self.station)
        self.goods = ocr(self.contrast_table, "HOCR")
        self.rowcount = 0
        self.OCRline = 0
        self.drawPreview()
        if len(self.goods) < 1:
            return
        self.previewRects[self.rowcount].setPen(QPen(Qt.blue))
        self.drawRow(self.OCRline)
        self.save_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        
    def makeImages(self, imagepath):
        """ Creates image pieces for the use in OCR and display in the
        tool.
        """
        origimg = cv2.imread(imagepath, 0)
        h, w = origimg.shape
        if w < 1920 or h <1080:
            QMessageBox.critical(self, "Error",
                                 "Invalid or too small picture.\n"+\
                                 "Screenshots must be at least 1920"+\
"                                 pixel wide and 1080 pixel hight.")
            return 0
        if int((float(w)/h)*100) != 177:
            QMessageBox.critical(self, "Error", "At the moment only"+\
                                 " Screenshots in format 16:9 are "+\
                                 "supported.\n e.g. 1920x1080, "+\
                                 "2351x1323, 2715x1527, ...")
            return 0
        offset = 10
        sttnimg = origimg[intR(0.0583*h):intR(0.0851*h),
                          intR(0.0427*w):intR(0.5703*w)]
        sttnimg = cv2.copyMakeBorder(sttnimg,offset,offset,
                                     offset,offset,
                                     cv2.BORDER_CONSTANT,value=(0)) 
        self.tblimg = origimg[intR(0.2287*h):intR(0.8587*h),
                                   intR(0.0664*w):intR(0.5703*w)]
        self.tblimg = cv2.copyMakeBorder(self.tblimg,
                                         offset,offset,offset,offset,
                                         cv2.BORDER_CONSTANT,value=(0))
        # contrast_station_name is used in OCR
        self.contrast_station_name = contBright(255.0 - sttnimg,
                                                76.0, 179.0)
        # contrast_table is used in OCR
        self.contrast_table = adjustTableImg(255.0 - self.tblimg)
        self.table_h, self.table_w = self.contrast_table.shape
        
    def drawPreview(self):
        self.previewRects = []
        old_h, old_w = self.tblimg.shape
        processedimage = array2qimage(self.tblimg)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        pix = pix.scaled(self.preview.size(),
                         Qt.KeepAspectRatio,
                         Qt.SmoothTransformation)
        new_h = pix.height()
        new_w = pix.width()
        ratio_h = old_h/float(new_h)
        ratio_w = old_w/float(new_w)
        self.scene = QGraphicsScene()
        self.scene.addPixmap(pix)
        pen = QPen(Qt.yellow)
        for line in self.goods:
            rect = self.scene.addRect(line.x1/ratio_w - 4.0,
                                      line.y1/ratio_h - 4.0,
                                      line.w/ratio_w + 7.0,
                                      line.h/ratio_h + 5.0, pen)
            self.previewRects.append(rect)
        self.preview.setScene(self.scene)
        self.preview.show()
        
    def drawRow(self, num):
        if len(self.goods) <= num:
            self.cleanAllFields()
            self.cleanAllCanvases()
            self.save_button.setEnabled(False)
            self.skip_button.setEnabled(False)
        else:
            for field, canvas, item in zip(self.fields, self.canvases,
                                           self.goods[num].items):
                if item != None:
                    field.setText(item.value)
                    self.drawSnippet(canvas, item)
                else:
                    self.cleanImage(canvas)
                    self.cleanField(field)

            self.OCRline += 1
    
    def drawSnippet(self, graphicsview, item):
        snippet = self.contrast_table[item.y1-5:item.y2+5,
                                      item.x1-5:item.x2+5]
        processedimage = array2qimage(snippet)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        if graphicsview.height() < pix.height():
            pix = pix.scaled(graphicsview.size(), Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        graphicsview.setScene(scene)
        graphicsview.show()

    
    def drawStationName(self):
        processedimage = array2qimage(self.contrast_station_name)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        if self.station_name_img.height() < pix.height():
            pix = pix.scaled(self.station_name_img.size(),
                             Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        self.station_name_img.setScene(scene)
        self.station_name_img.show()
    
    def cleanAllFields(self):
        for field in self.fields:
            field.setText('')
        self.station_name.setText('')
    
    def cleanField(self, field):
        field.setText('')
            
    def cleanAllCanvases(self):
        scene = QGraphicsScene()
        for field in self.canvases:
            field.setScene(scene)
            #field.show()
        self.station_name_img.setScene(scene)
    
    def cleanImage(self, graphicsview):
        scene = QGraphicsScene()
        graphicsview.setScene(scene)
        #field.show()
    
    def addItemToTable(self):
        self.export_button.setEnabled(True)
        self.result_table.insertRow(self.tablerowcount)
        for n, field in enumerate(self.fields):
            newitem = QTableWidgetItem(str(field.text()).replace(',',
                                                                 ''))
            self.result_table.setItem(self.tablerowcount, n, newitem)
        newitem = QTableWidgetItem(self.file_tmstmp)
        self.result_table.setItem(self.tablerowcount, 7, newitem)
        self.result_table.resizeColumnsToContents()
        self.result_table.resizeRowsToContents()
        self.updatePreview()
        self.rowcount += 1
        self.tablerowcount += 1
        self.drawRow(self.OCRline)
        
    def skipItem(self):
        self.updatePreview()
        self.rowcount += 1
        self.drawRow(self.OCRline)
        
    def updatePreview(self):
        self.previewRects[self.rowcount].setPen(QPen(Qt.green))
        if len(self.previewRects)>(self.rowcount+1):
            self.previewRects[self.rowcount+1].setPen(QPen(Qt.blue))
            
    def exportTable(self):
        dir = QString('"./'+self.station.strip().title()+'.csv"')
        file = QFileDialog.getSaveFileName(self, QString('Save'), dir)
        if not file:
            return
        allRows = self.result_table.rowCount()
        towrite = ''
        for row in xrange(0, allRows):
            line = self.station + ";"+\
                   self.result_table.item(row,0).text()+";"+\
                   self.result_table.item(row,1).text()+";"+\
                   self.result_table.item(row,2).text()+";"+\
                   self.result_table.item(row,4).text()+";"+\
                   self.result_table.item(row,6).text()+";"+\
                   self.result_table.item(row,7).text()+";\n"
            towrite += line
        csv_file = open(file, "w")
        csv_file.write(towrite)
        csv_file.close()

def main():
    app = QApplication(sys.argv)
    window = EliteOCR()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    sys.exit(main()) 
