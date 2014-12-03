import random
import sys
import time
from os.path import split, isfile, dirname, realpath, exists
from os import makedirs
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QMessageBox,\
                        QPixmap, QPen, QTableWidgetItem
from PyQt4.QtCore import Qt, QObject, SIGNAL
import cv2

from eliteOCRGUI import Ui_MainWindow
from customqlistwidgetitem import CustomQListWidgetItem
from calibrate import CalibrateDialog
from settingsdialog import SettingsDialog
from settings import loadSettings
from ocr import OCR
from qimage2ndarray import array2qimage

class EliteOCR(QMainWindow, Ui_MainWindow):
    def __init__(self):            
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setupTable()
        self.settings = loadSettings(self)
        self.ocr_all_set = False
        self.fields = [self.name, self.sell, self.buy, self.demand_num, self.demand,
                       self.supply_num, self.supply]
        self.canvases = [self.name_img, self.sell_img, self.buy_img, self.demand_img,
                         self.demand_text_img, self.supply_img, self.supply_text_img]
        #setup buttons
        self.add_button.clicked.connect(self.addFiles)
        self.remove_button.clicked.connect(self.removeFile)
        self.save_button.clicked.connect(self.addItemToTable)
        self.skip_button.clicked.connect(self.nextLine)
        self.ocr_button.clicked.connect(self.performOCR)
        self.ocr_all.clicked.connect(self.runOCRAll)
        self.export_button.clicked.connect(self.exportTable)
        self.clear_table.clicked.connect(self.clearTable)
        
        QObject.connect(self.actionHow_to_use, SIGNAL('triggered()'), self.howToUse)
        QObject.connect(self.actionAbout, SIGNAL('triggered()'), self.About)
        QObject.connect(self.actionOpen, SIGNAL('triggered()'), self.addFiles)
        QObject.connect(self.actionPreferences, SIGNAL('triggered()'), self.openSettings)
        QObject.connect(self.actionCalibrate, SIGNAL('triggered()'), self.openCalibrate)
        self.error_close = False
        if not isfile("./tessdata/big.traineddata"):
            QMessageBox.critical(self,"Error", "OCR training data not found!\n"+\
            "Make sure tessdata directory exists and contains big.traineddata.")
            self.error_close = True

        #set up required items for nn
        self.training_image_dir = './nn_training_images/' #dirname(realpath(__file__)) + "\\nn_training_images\\"


    def howToUse(self):
        QMessageBox.about(self, "How to use", "Click \"+\" and select your screenshots. Select "+\
            "multiple files by holding CTRL or add them one by one. Select one file and click "+\
            "the OCR button. Check if the values have been recognised properly. Optionally "+\
            "correct them and click on \"Add and Next\" to continue to next line. You can edit "+\
            "the values in the table by double clicking on the entry.\n\nAfter processing one "+\
            "screenshot you can "+\
            "click on the next file on the list and click the ORC Button again. Should there be r"+\
            "epeated entry, you can click \"Skip\" to continue to next line without adding curren"+\
            "t one to the list.\n\nWhen finished click on \"Export\" to save your results to a cs"+\
            "v-file(separated by ; ). CSV can be opened by most spreadsheet editors like Excel, L"+\
            "ibreOffice Calc etc.")

    def About(self):
        QMessageBox.about(self,"About", "EliteOCR by CMDR SEEEBEK\nVersion 0.3.1.1\n\n"
        "EliteOCR is capable of reading the entries in Elite: Dangerous markets screenshots.\n\n"+\
        "Best results are achieved with screenshots of 3840 by 2160 pixel (4K) or more. "+\
        "You can make screenshots in game by pressing F10. You find them usually in\n"+\
        "C:\Users\USERNAME\Pictures\Frontier Developments\Elite Dangerous\n"+\
        "Screenshots made with ALT+F10 have lower recognition rate!\n\n"+\
        "Owners of Nvidia video cards can use DSR technology to increase the resolution "+\
        "for screenshots and revert it back to normal without leaving the game.")
        
    def setupTable(self):
        """Add columns and column names to the table"""
        self.result_table.setColumnCount(9)
        self.result_table.setHorizontalHeaderLabels(['station', 'commodity', 'sell', 'buy',
                                                     'demand', 'dem', 'supply',
                                                     'sup', 'timestamp'])
        self.result_table.setColumnHidden(8, True)
        
    def openSettings(self):
        """Open settings dialog and reload settings"""
        settingsDialog = SettingsDialog(self)
        settingsDialog.exec_()
        self.settings = loadSettings(self)
    
    def openCalibrate(self, dir=None):
        """Open calibrate dialog and reload settings"""
        if dir == None:
            image = QFileDialog.getOpenFileName(self, "Open", self.settings['screenshot_dir'])
        else:
            image = QFileDialog.getOpenFileName(self, "Open", dir)
        if image != "":
            calibrateDialog = CalibrateDialog(self, image)
            calibrateDialog.exec_()
            self.settings = loadSettings(self)
            self.file_list.settings = loadSettings(self)
        
    def addFiles(self):
        """Add files to the file list."""
        files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'])
        if files == []:
            return
        first_item = None
        for file in files:
            item = CustomQListWidgetItem(split(str(file))[1], file)
            if first_item == None:
                first_item = item
            self.file_list.addItem(item)
        
        self.file_list.itemClicked.connect(self.selectFile)
        self.save_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        #self.cleanAllFields()
        #self.cleanAllSnippets()
        if first_item !=None:
            self.selectFile(first_item)
        if self.ocr_button.isEnabled() and self.file_list.count() > 1:
            self.ocr_all.setEnabled(True)
        self.cleanAllFields()
        self.cleanAllSnippets()

    def removeFile(self):
        """Remove selected file from file list."""
        item = self.file_list.currentItem()
        self.file_list.takeItem(self.file_list.currentRow())
        del item
        self.file_label.setText("-")
        scene = QGraphicsScene()
        self.previewSetScene(scene)
        self.save_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.cleanAllFields()
        self.cleanAllSnippets()
        if self.file_list.currentItem():
            self.selectFile(self.file_list.currentItem())
        if self.file_list.count() == 0:
            self.remove_button.setEnabled(False)
            self.ocr_button.setEnabled(False)
        if self.file_list.count() < 2:
            self.ocr_all.setEnabled(False)
    
    def selectFile(self, item):
        """Select clicked file and shows prewiev of the selected file."""
        self.ocr_all_set = False
        self.file_list.setCurrentItem(item)
        self.file_label.setText(item.text())
        self.setPreviewImage(item.preview_image)
        self.remove_button.setEnabled(True)
        self.ocr_button.setEnabled(True)
        if self.file_list.count() > 1:
            self.ocr_all.setEnabled(True)
        
    def setPreviewImage(self, image):
        """Show image in self.preview."""
        pix = image.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        self.previewSetScene(scene)
        
    def previewSetScene(self, scene):
        """Shows scene in preview"""
        self.preview.setScene(scene)
        self.preview.show()
        
    def runOCRAll(self):
        self.ocr_all_set = True
        self.performOCR()
        
    def performOCR(self):
        """Send image to OCR and process the results"""
        #start_time = time.time()
        self.OCRline = 0
        self.current_result = OCR(self.file_list.currentItem().color_image, self.file_list.currentItem().image)
        if self.current_result.station == None:
            QMessageBox.critical(self,"Error", "Screenshot not recognized.\n"+\
                "Make sure you use a valid screenshot from the commodieties market. Should the "+\
                "problem persist, please recalibrate the OCR areas with Settings->Calibrate.")
            return
        self.drawOCRPreview()
        self.markCurrentRectangle()
        self.drawStationName()
        self.processOCRLine()
        self.skip_button.setEnabled(True)
        self.save_button.setEnabled(True)
        #print(time.time() - start_time)
        
    def addItemToTable(self):
        """Adds items from current OCR result line to the result table."""
        tab = self.result_table
        res_station = self.current_result.station.name.value
        row_count = tab.rowCount()
        self.export_button.setEnabled(True)
        self.clear_table.setEnabled(True)
        #check for duplicates
        duplicate = False
        if self.settings["remove_dupli"]:
            for i in range(row_count):
                station = tab.item(i, 0).text()
                com1 = tab.item(i, 1).text()
                com2 = self.fields[0].currentText().replace(',', '')
                if station == res_station and com1 == com2:
                    duplicate = True
        
        if not duplicate:
            tab.insertRow(row_count)
            newitem = QTableWidgetItem(res_station)
            tab.setItem(row_count, 0, newitem)
            for n, field in enumerate(self.fields):
                newitem = QTableWidgetItem(str(field.currentText()).replace(',', ''))
                tab.setItem(row_count, n+1, newitem)
            newitem = QTableWidgetItem(self.file_list.currentItem().timestamp)
            tab.setItem(row_count, 8, newitem)
            tab.resizeColumnsToContents()
            tab.resizeRowsToContents()
            if self.settings['create_nn_images']:
                self.saveValuesForTraining()
        self.nextLine()

    def saveValuesForTraining(self):
        """Get OCR image/user values and save them away for later processing, and training neural net"""
        cres = self.current_result
        res = cres.commodities[self.OCRline]
        if not exists(self.training_image_dir):
            makedirs(self.training_image_dir)
        w = len(self.current_result.contrast_commodities_img)
        h = len(self.current_result.contrast_commodities_img[0])
        for index, field, canvas, item in zip(range(0, len(self.canvases) - 1), self.fields, self.canvases, res.items):
            if index in [1, 2, 3, 5]:
                val = str(field.currentText()).replace(',', '')
                if val:
                    snippet = self.cutImage(cres.contrast_commodities_img, item)
                    #cv2.imshow('snippet', snippet)
                    imageFilepath = self.training_image_dir + val + '_' + str(w) + 'x' + str(h) + '-' + str(int(time.time())) + '-' + str(random.randint(10000, 100000)) + '.png'
                    cv2.imwrite(imageFilepath, snippet)

    def nextLine(self):
        """Skip current OCR result line."""
        self.markCurrentRectangle(QPen(Qt.green))
        self.OCRline += 1
        if len(self.previewRects) > self.OCRline:
            self.markCurrentRectangle()
            self.processOCRLine()
        else:
            self.save_button.setEnabled(False)
            self.skip_button.setEnabled(False)
            self.cleanAllFields()
            self.cleanAllSnippets()
            if self.ocr_all_set:
                self.nextFile()
                
    def nextFile(self):
        if self.file_list.currentRow() < self.file_list.count()-1:
            self.file_list.setCurrentRow(self.file_list.currentRow() + 1)
            self.performOCR()
            
    def clearTable(self):
        """Empty the result table."""
        self.result_table.setRowCount(0)
        self.clear_table.setEnabled(False)
        self.export_button.setEnabled(False)
    
    def processOCRLine(self):
        """Process current OCR result line."""
        if len(self.current_result.commodities) > self.OCRline:
            res = self.current_result.commodities[self.OCRline]
            autofill = True
            if self.settings["auto_fill"]:
                for item in res.items:
                    if item == None:
                        continue
                    if not item.confidence > 0.84:
                        autofill = False
                        
            for field, canvas, item in zip(self.fields, self.canvases, res.items):
                if item != None:
                    field.clear()
                    field.addItems(item.optional_values)
                    field.setEditText(item.value)
                    if not(self.settings["auto_fill"] and autofill):
                        self.setConfidenceColor(field, item)
                        self.drawSnippet(canvas, item)
                else:
                    self.cleanSnippet(canvas)
                    self.cleanField(field)
            if self.settings["auto_fill"] and autofill:
                self.addItemToTable()
    
    def setConfidenceColor(self, field, item):
        c = item.confidence
        if c > 0.84:
            color  = "#ffffff"
        if c <= 0.84 and c >0.67:
            color = "#ffffbf"
        if c <= 0.67 and c >0.5:
            color = "#fff2bf"
        if c <= 0.5 and c >0.34:
            color = "#ffe6bf"
        if c <= 0.34 and c >0.17:
            color = "#ffd9bf"
        if c <= 0.17:
            color = "#ffccbf"
        field.lineEdit().setStyleSheet("QLineEdit{background: "+color+";}")

    def drawOCRPreview(self):
        """Draw processed file preview and show recognised areas."""
        res = self.current_result
        name = res.station.name
        img = self.file_list.currentItem().preview_image
        
        old_h = img.height()
        old_w = img.width()
        
        pix = img.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        new_h = pix.height()
        new_w = pix.width()
        
        ratio_h = old_h/float(new_h)
        ratio_w = old_w/float(new_w)
        
        self.scene = QGraphicsScene()
        self.scene.addPixmap(pix)
        
        self.previewRects = []
        pen = QPen(Qt.green)
        rect = self.addRect(self.scene, name, ratio_w, ratio_h, pen)
        
        pen = QPen(Qt.yellow)
        for line in res.commodities:
            rect = self.addRect(self.scene, line, ratio_w, ratio_h, pen)
            self.previewRects.append(rect)
            
        self.previewSetScene(self.scene)
        
    def addRect(self, scene, item, ratio_w, ratio_h, pen):
        """Adds a rectangle to scene and returns it."""
        rect = scene.addRect((item.x1/item.scale)/ratio_w -3,(item.y1/item.scale)/ratio_h - 3,
                              item.w/item.scale/ratio_w +7, item.h/item.scale/ratio_h +6, pen)
        return rect
    
    def markCurrentRectangle(self, pen=QPen(Qt.blue)):
        self.previewRects[self.OCRline].setPen(pen)
    
    def cutImage(self, image, item):
        """Cut image snippet from a big image using points from item."""
        snippet = image[item.y1/item.scale - 5:item.y2/item.scale + 5,
                        item.x1/item.scale - 5:item.x2/item.scale + 5]
        return snippet
    
    def drawSnippet(self, graphicsview, item):
        """Draw single result item to graphicsview"""
        res = self.current_result
        snippet = self.cutImage(res.contrast_commodities_img, item)
        #cv2.imwrite('snippets/'+str(self.currentsnippet)+'.png',snippet)
        #self.currentsnippet += 1
        processedimage = array2qimage(snippet)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        if graphicsview.height() < pix.height():
            pix = pix.scaled(graphicsview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        graphicsview.setScene(scene)
        graphicsview.show()
    
    def drawStationName(self):
        """Draw station name snippet to station_name_img"""
        res = self.current_result
        name = res.station.name
        self.station_name.setEditText(name.value)
        img = self.cutImage(res.contrast_station_img, name)
        processedimage = array2qimage(img)
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
            self.cleanField(field)
        self.cleanField(self.station_name)
    
    def cleanField(self, field):
        field.setEditText('')
        field.lineEdit().setStyleSheet("")
        field.clear()
            
    def cleanAllSnippets(self):
        for field in self.canvases:
            self.cleanSnippet(field)
        self.cleanSnippet(self.station_name_img)
    
    def cleanSnippet(self, graphicsview):
        scene = QGraphicsScene()
        graphicsview.setScene(scene)
    
    def exportTable(self):
        res = self.current_result
        name = res.station.name.value
        dir = self.settings["export_dir"]+"/"+name.title()+'.csv"'
        file = QFileDialog.getSaveFileName(self, 'Save', dir)
        if not file:
            return
        allRows = self.result_table.rowCount()
        towrite = ''
        for row in xrange(0, allRows):
            line = self.result_table.item(row,0).text()+";"+\
                   self.result_table.item(row,1).text()+";"+\
                   self.result_table.item(row,2).text()+";"+\
                   self.result_table.item(row,3).text()+";"+\
                   self.result_table.item(row,4).text()+";"+\
                   self.result_table.item(row,5).text()+";"+\
                   self.result_table.item(row,6).text()+";"+\
                   self.result_table.item(row,7).text()+";"+\
                   self.result_table.item(row,8).text()+";\n"
            towrite += line
        csv_file = open(file, "w")
        csv_file.write(towrite)
        csv_file.close()
        
def main():
    app = QApplication(sys.argv)
    window = EliteOCR()
    if window.error_close:
       sys.exit() 
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    sys.exit(main()) 