# -*- coding: utf-8 -*-
import random
import sys
import time
import json
from datetime import datetime
from os.path import split, isfile, dirname, realpath, exists
from os import makedirs
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QMessageBox,\
                        QPixmap, QPen, QTableWidgetItem, QPushButton, QAction, QFont
from PyQt4.QtCore import Qt, QObject, QSize, SIGNAL
import cv2

from eliteOCRGUI import Ui_MainWindow
from customqlistwidgetitem import CustomQListWidgetItem
from calibrate import CalibrateDialog
from busydialog import BusyDialog
from settingsdialog import SettingsDialog
from editordialog import EditorDialog
from settings import Settings
from ocr import OCR
from qimage2ndarray import array2qimage

from openpyxl import Workbook
from ezodf import newdoc, Sheet

#plugins
import imp
#from plugins.BPC_Feeder.bpcfeeder_wrapper import BPC_Feeder

class EliteOCR(QMainWindow, Ui_MainWindow):
    def __init__(self):            
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setupTable()
        self.settings = Settings(self)
        self.ocr_all_set = False
        self.color_image = None
        self.preview_image = None
        self.current_result = None
        self.zoom = False
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
        self.export_button.clicked.connect(self.export)
        self.clear_table.clicked.connect(self.clearTable)
        self.zoom_button.clicked.connect(self.drawOCRPreview)
        
        QObject.connect(self.actionHow_to_use, SIGNAL('triggered()'), self.howToUse)
        QObject.connect(self.actionAbout, SIGNAL('triggered()'), self.About)
        QObject.connect(self.actionOpen, SIGNAL('triggered()'), self.addFiles)
        QObject.connect(self.actionPreferences, SIGNAL('triggered()'), self.openSettings)
        QObject.connect(self.actionCommodity_Editor, SIGNAL('triggered()'), self.openEditor)
        
        self.error_close = False
        if not isfile("./tessdata/big.traineddata"):
            QMessageBox.critical(self,"Error", "OCR training data not found!\n"+\
            "Make sure tessdata directory exists and contains big.traineddata.")
            self.error_close = True

        #set up required items for nn
        self.training_image_dir = self.settings.app_path +"\\nn_training_images\\"
        
        self.loadPlugins()
    
    def loadPlugins(self):
        """Load known plugins"""
        #Trade Dangerous Export by gazelle (bgol)    
        if isfile(self.settings.app_path+"\\plugins\\TD_Export\\TD_Export.py"):
            plugin2 = imp.load_source('TD_Export', self.settings.app_path+\
                                     "\\plugins\\TD_Export\\TD_Export.py")
            self.tdexport = plugin2.TD_Export(self, self.settings.app_path.decode('windows-1252'))
            self.tdexport_button = QPushButton(self.centralwidget)
            self.tdexport_button.setText("Trade Dangerous Export")
            self.tdexport_button.setEnabled(False)
            self.horizontalLayout_2.addWidget(self.tdexport_button)
            self.tdexport_button.clicked.connect(lambda: self.tdexport.run(self.tableToList()))
    
    def enablePluginButtons(self):
        if 'tdexport' in dir(self):
            if self.tdexport != None:
                self.tdexport_button.setEnabled(True)
        
    def disablePluginButtons(self):
        if 'tdexport' in dir(self):
            if self.tdexport != None:
                self.tdexport_button.setEnabled(False)

    def howToUse(self):
        QMessageBox.about(self, "How to use", "Click \"+\" and select your screenshots. Select "+\
            "multiple files by holding CTRL or add them one by one. Select one file and click "+\
            "the OCR button. Check if the values have been recognised properly. Optionally "+\
            "correct them and click on \"Add and Next\" to continue to next line. You can edit "+\
            "the values in the table by double clicking on the entry.\n\nAfter processing one "+\
            "screenshot you can "+\
            "click on the next file on the list and click the ORC Button again. Should there be r"+\
            "epeated entry, you can click \"Skip\" to continue to next line without adding curren"+\
            "t one to the list.\n\nWhen finished click on \"Export\" to save your results.")

    def About(self):
        QMessageBox.about(self,"About", "EliteOCR\nVersion 0.3.6\n\n"+\
        "Contributors:\n"+\
        "Seeebek, CapCap, Gazelle\n\n"+\
        "EliteOCR is capable of reading the entries in Elite: Dangerous markets screenshots.\n\n"+\
        "Best results are achieved with screenshots of 3840 by 2160 pixel (4K) or more. "+\
        "You can make screenshots in game by pressing F10. You find them usually in\n"+\
        "C:\Users\USERNAME\Pictures\Frontier Developments\Elite Dangerous\n"+\
        "Screenshots made with ALT+F10 have lower recognition rate!\n\n"+\
        "Owners of Nvidia video cards can use DSR technology to increase the resolution "+\
        "for screenshots and revert it back to normal without leaving the game.")
        
    def setupTable(self):
        """Add columns and column names to the table"""
        self.result_table.setColumnCount(10)
        self.result_table.setHorizontalHeaderLabels(['station', 'commodity', 'sell', 'buy',
                                                     'demand', 'dem', 'supply',
                                                     'sup', 'timestamp','system'])
        self.result_table.setColumnHidden(8, True)
        
    def openSettings(self):
        """Open settings dialog and reload settings"""
        settingsDialog = SettingsDialog(self.settings)
        settingsDialog.exec_()
    
    def openEditor(self):
        editorDialog = EditorDialog(self.settings)
        editorDialog.exec_()
        
    def addFiles(self):
        """Add files to the file list."""
        files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'])
        if files == []:
            return
        first_item = None
        for file in files:
            file1 = unicode(file).encode('windows-1252')
            item = CustomQListWidgetItem(split(file1)[1], file1, self.settings)
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
            self.zoom_button.setEnabled(False)
        if self.file_list.count() < 2:
            self.ocr_all.setEnabled(False)
    
    def selectFile(self, item):
        """Select clicked file and shows prewiev of the selected file."""
        self.color_image = item.loadColorImage()
        self.preview_image = item.loadPreviewImage(self.color_image)
        self.ocr_all_set = False
        font = QFont()
        font.setPointSize(11)
        self.system_not_found.setText("")
        if len(item.system) == 0:
            self.system_not_found.setText("System name not found in log files. Make sure log directory path is set up correctly or add system name manually in the field below. Note: System name is necessary for BPC import!")
        self.system_name.setText(item.system)
        self.system_name.setFont(font)
        self.file_list.setCurrentItem(item)
        self.file_label.setText(item.text())
        self.setPreviewImage(self.preview_image)
        if not item.valid_market:
            self.system_not_found.setText("File was not recognized as a valid market screenshot. If the file is valid please report the issue in the forum.")
            return
        self.remove_button.setEnabled(True)
        self.ocr_button.setEnabled(True)
        self.zoom_button.setEnabled(True)
        if self.file_list.count() > 1:
            self.ocr_all.setEnabled(True)
    
    def setPreviewImage(self, image):
        """Show image in self.preview."""
        factor = self.factor.value()
        pix = image.scaled(QSize(self.preview.size().width()*factor,self.preview.size().height()*factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self.OCRline = 0
        busyDialog = BusyDialog(self)
        busyDialog.show()
        QApplication.processEvents()
        if self.file_list.currentItem().valid_market:
            self.current_result = OCR(self.color_image)
            """
            try:
                self.current_result = OCR(self.color_image)
            except:
                QMessageBox.critical(self,"Error", "Error while performing OCR.\nPlease report the "+\
                "problem to the developers through github, sourceforge or forum and provide the "+\
                "screenshot which causes the problem.")
                return
            if self.current_result.station == None:
                QMessageBox.critical(self,"Error", "Screenshot not recognized.\n"+\
                    "Make sure you use a valid screenshot from the commodieties market. Should the "+\
                    "problem persist, please recalibrate the OCR areas with Settings->Calibrate.")
                return
            """
            self.drawOCRPreview()
            self.markCurrentRectangle()
            self.drawStationName()
            self.skip_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.processOCRLine()
        else:
            self.nextFile()
        
    def addItemToTable(self):
        """Adds items from current OCR result line to the result table."""
        tab = self.result_table
        res_station = unicode(self.station_name.currentText()).title()
        row_count = tab.rowCount()
        self.export_button.setEnabled(True)
        self.enablePluginButtons()
        self.clear_table.setEnabled(True)
        #check for duplicates
        duplicate = False
        if self.settings["remove_dupli"]:
            for i in range(row_count):
                station = unicode(tab.item(i, 0).text()).title()
                com1 = unicode(tab.item(i, 1).text()).title()
                com2 = unicode(self.fields[0].currentText()).replace(',', '').title()
                if station == res_station and com1 == com2:
                    duplicate = True
        
        if not duplicate:
            if not self.current_result.commodities[self.OCRline].items[0] is None:
                if self.current_result.commodities[self.OCRline].items[0].confidence < 0.8:
                    self.addCommodityToDictionary(self.name.currentText())
            self.current_result.station.name.value = self.station_name.currentText()
            tab.insertRow(row_count)
            newitem = QTableWidgetItem(unicode(res_station).title().replace("'S", "'s"))
            tab.setItem(row_count, 0, newitem)
            for n, field in enumerate(self.fields):
                newitem = QTableWidgetItem(unicode(field.currentText()).replace(',', '').title())
                tab.setItem(row_count, n+1, newitem)
            newitem = QTableWidgetItem(self.file_list.currentItem().timestamp)
            tab.setItem(row_count, 8, newitem)
            newitem = QTableWidgetItem(self.system_name.text())
            tab.setItem(row_count, 9, newitem)
            tab.resizeColumnsToContents()
            tab.resizeRowsToContents()
            if self.settings['create_nn_images']:
                self.saveValuesForTraining()
        self.nextLine()
    
    def addCommodityToDictionary(self, text):
        try:
            file = open(self.settings.app_path + "\\commodities.json", 'r')
            file_content = file.read()
            comm_list = json.loads(file_content)
            file.close()
        except:
            comm_list = ['BEER']
        comm_list.append(unicode(text))
        comm_list = list(set(comm_list))
        comm_list.sort()
        file = open(self.settings.app_path + "\\commodities.json", 'w')
        file.write(json.dumps(comm_list,indent=2, separators=(',', ': ')))
        file.close()
    
    def saveValuesForTraining(self):
        """Get OCR image/user values and save them away for later processing, and training
        neural net"""
        cres = self.current_result
        res = cres.commodities[self.OCRline]
        if not exists(self.training_image_dir):
            makedirs(self.training_image_dir)
        w = len(self.current_result.contrast_commodities_img)
        h = len(self.current_result.contrast_commodities_img[0])
        for index, field, canvas, item in zip(range(0, len(self.canvases) - 1),
                                              self.fields, self.canvases, res.items):

            val = unicode(field.currentText()).replace(',', '')
            if val:
                snippet = self.cutImage(cres.contrast_commodities_img, item)
                #cv2.imshow('snippet', snippet)
                imageFilepath = self.training_image_dir + val + '_' + unicode(w) + 'x' + unicode(h) +\
                                '-' + unicode(int(time.time())) + '-' +\
                                unicode(random.randint(10000, 100000)) + '.png'
                cv2.imwrite(imageFilepath, snippet)

    def nextLine(self):
        """Process next OCR result line."""
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
        """OCR next file"""
        if self.file_list.currentRow() < self.file_list.count()-1:
            self.file_list.setCurrentRow(self.file_list.currentRow() + 1)
            self.color_image = self.file_list.currentItem().loadColorImage()
            self.preview_image = self.file_list.currentItem().loadPreviewImage(self.color_image)
            self.performOCR()
            font = QFont()
            font.setPointSize(11)
            if self.OCRline == 0:
                if len(self.file_list.currentItem().system) > 0:
                    self.system_not_found.setText("")
                    self.system_name.setText(self.file_list.currentItem().system)
                    self.system_name.setFont(font)
                else:
                    self.system_name.setText("")
                    self.system_name.setFont(font)
                    self.system_not_found.setText("System name not found in log files. Make sure log directory path is set up correctly or add system name manually in the field below. Note: System name is necessary for BPC import!")
                self.system_name.setFocus()
                self.system_name.selectAll()
            
    def clearTable(self):
        """Empty the result table."""
        self.result_table.setRowCount(0)
        self.clear_table.setEnabled(False)
        self.export_button.setEnabled(False)
        self.disablePluginButtons()
    
    def processOCRLine(self):
        """Process current OCR result line."""
        if len(self.current_result.commodities) > self.OCRline:
            font = QFont()
            font.setPointSize(11)
            res = self.current_result.commodities[self.OCRline]
            if self.OCRline > 0:
                autofill = True
            else:
                autofill = False
            if self.settings["auto_fill"]:
                for item in res.items:
                    if item == None:
                        continue
                    if not item.confidence > 0.83:
                        autofill = False
                if res.items[0] is None:
                    autofill = False
                if res.items[1] is None:
                    autofill = False
                        
            for field, canvas, item in zip(self.fields, self.canvases, res.items):
                if item != None:
                    field.clear()
                    field.addItems(item.optional_values)
                    field.setEditText(item.value)
                    field.lineEdit().setFont(font)
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
        if c > 0.83:
            color  = "#ffffff"
        if c <= 0.83 and c >0.67:
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

    def xdrawOCRPreview(self):
        """Draw processed file preview and show recognised areas."""
        res = self.current_result
        name = res.station
        img = self.preview_image
        
        old_h = img.height()
        old_w = img.width()
        
        #pix = img.scaled(QSize(self.preview.size().width()*2,self.preview.size().height()*2), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pix = img.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        new_h = pix.height()
        new_w = pix.width()
        
        ratio_h = old_h/float(new_h)
        ratio_w = old_w/float(new_w)
        
        self.scene = QGraphicsScene()
        self.scene.addPixmap(pix)
        #self.scene.addPixmap(img)
        
        self.previewRects = []
        pen = QPen(Qt.green)
        rect = self.addRect(self.scene, name, ratio_w, ratio_h, pen)
        
        pen = QPen(Qt.yellow)
        redpen = QPen(Qt.red)
        for line in res.commodities:
            if line.w < (0.02*old_w):
                rect = self.addRect(self.scene, line, ratio_w, ratio_h, redpen)
            else:
                rect = self.addRect(self.scene, line, ratio_w, ratio_h, pen)
            self.previewRects.append(rect)
            
        self.previewSetScene(self.scene)
        
    def drawOCRPreview(self):
        if self.current_result is None:
            self.setPreviewImage(self.preview_image)
            return
        factor = self.factor.value()
        res = self.current_result
        name = res.station
        img = self.preview_image
        
        old_h = img.height()
        old_w = img.width()
        
        pix = img.scaled(QSize(self.preview.size().width()*factor,self.preview.size().height()*factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #pix = img.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        new_h = pix.height()
        new_w = pix.width()
        
        ratio_h = old_h/float(new_h)
        ratio_w = old_w/float(new_w)
        
        self.scene = QGraphicsScene()
        self.scene.addPixmap(pix)
        #self.scene.addPixmap(img)
        
        self.previewRects = []

        pen = QPen(Qt.yellow)
        redpen = QPen(Qt.red)
        bluepen = QPen(Qt.blue)
        greenpen = QPen(Qt.green)
        
        rect = self.addRect(self.scene, name, ratio_w, ratio_h, greenpen)
        
        counter = 0
        for line in res.commodities:
            if counter < self.OCRline:
                rect = self.addRect(self.scene, line, ratio_w, ratio_h, greenpen)
            elif counter == self.OCRline:
                rect = self.addRect(self.scene, line, ratio_w, ratio_h, bluepen)
            else:
                if line.w < (0.02*old_w):
                    rect = self.addRect(self.scene, line, ratio_w, ratio_h, redpen)
                else:
                    rect = self.addRect(self.scene, line, ratio_w, ratio_h, pen)
            
            counter += 1
            self.previewRects.append(rect)
            
        self.previewSetScene(self.scene)
        
    def addRect(self, scene, item, ratio_w, ratio_h, pen):
        """Adds a rectangle to scene and returns it."""
        rect = scene.addRect(item.x1/ratio_w -3, item.y1/ratio_h -3,
                              item.w/ratio_w +7, item.h/ratio_h +6, pen)
        return rect
    
    def markCurrentRectangle(self, pen=QPen(Qt.blue)):
        self.previewRects[self.OCRline].setPen(pen)
    
    def cutImage(self, image, item):
        """Cut image snippet from a big image using points from item."""
        snippet = image[item.y1 - 5:item.y2 + 5,
                        item.x1 - 5:item.x2 + 5]
        return snippet
    
    def drawSnippet(self, graphicsview, item):
        """Draw single result item to graphicsview"""
        res = self.current_result
        snippet = self.cutImage(res.contrast_commodities_img, item)
        #cv2.imwrite('snippets/'+unicode(self.currentsnippet)+'.png',snippet)
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
        self.station_name.addItems(name.optional_values)
        self.station_name.setEditText(name.value)
        font = QFont()
        font.setPointSize(11)
        self.station_name.lineEdit().setFont(font)
        self.setConfidenceColor(self.station_name, name)
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
        
    def tableToList(self, allow_horizontal = False):
        all_rows = self.result_table.rowCount()
        all_cols = self.result_table.columnCount()
        result_list = [["System","Station","Commodity","Sell","Buy","Demand","","Supply","","Date"]]
        for row in xrange(0, all_rows):
            line = [self.safeStrToList(self.result_table.item(row,9).text()),
                    self.safeStrToList(self.result_table.item(row,0).text()),
                    self.safeStrToList(self.result_table.item(row,1).text()),
                    self.safeStrToList(self.result_table.item(row,2).text()),
                    self.safeStrToList(self.result_table.item(row,3).text()),
                    self.safeStrToList(self.result_table.item(row,4).text()),
                    self.safeStrToList(self.result_table.item(row,5).text()),
                    self.safeStrToList(self.result_table.item(row,6).text()),
                    self.safeStrToList(self.result_table.item(row,7).text()),
                    self.safeStrToList(self.result_table.item(row,8).text())]
            result_list.append(line)
        if self.settings['horizontal_exp'] and allow_horizontal:
            result_list = map(list, zip(*result_list))
        return result_list
    
    def safeStrToList(self, input):
        try:
            return int(input)
        except:
            return unicode(input)
    
    def exportToCsv(self, result, file):
        for row in result:
            if len(row[0]) == 0:
                QMessageBox.warning(self,"No System Name", "There are rows missing system name! \nThe exported CSV file is incompatible with some tools like BPC.")
                break
        towrite = ""
        for row in result:
            for cell in row:
                towrite += unicode(cell)+";"
            towrite += "\n"
        csv_file = open(file, "w")
        csv_file.write(towrite)
        csv_file.close()

    def exportToOds(self, result, file):
        ods = newdoc(doctype='ods', filename=unicode(file))
        sheet = Sheet('Sheet 1', size=(len(result)+1, len(result[0])+1))
        ods.sheets += sheet
        
        for i in xrange(len(result)):
            for j in xrange(len(result[0])):
                sheet[i,j].set_value(result[i][j])
        ods.save()

    def exportToXlsx(self, result, file):
        wb = Workbook()
        ws = wb.active

        for i in xrange(1,len(result)+1):
            for j in xrange(1,len(result[0])+1):
                ws.cell(row = i, column = j).value = result[i-1][j-1]
        wb.save(unicode(file))
            
    def export(self):
        if self.settings['last_export_format'] == "":
            self.settings.setValue('last_export_format', "csv")
            self.settings.sync()
            
        if self.settings['last_export_format'] == "xlsx":
            filter = "Excel Workbook (*.xlsx)"
        elif self.settings['last_export_format'] == "ods":
            filter = "OpenDocument Spreadsheet (*.ods)"
        elif self.settings['last_export_format'] == "csv":
            filter = "CSV-File (*.csv)"
            
        name = self.current_result.station.name.value
        dir = self.settings["export_dir"]+"/"+unicode(name).title().replace("'S", "'s")+'.'+self.settings['last_export_format']+'"'
        file = QFileDialog.getSaveFileName(self, 'Save', dir, "CSV-File (*.csv);;OpenDocument Spreadsheet (*.ods);;Excel Workbook (*.xlsx)", filter)
        if not file:
            return
            
        if file.split(".")[-1] == "csv":
            self.settings.setValue('last_export_format', "csv")
            self.settings.sync()
            self.exportToCsv(self.tableToList(True), file)
        elif file.split(".")[-1] == "ods":
            self.settings.setValue('last_export_format', "ods")
            self.settings.sync()
            self.exportToOds(self.tableToList(True), file)
        elif file.split(".")[-1] == "xlsx":
            self.settings.setValue('last_export_format', "xlsx")
            self.settings.sync()
            self.exportToXlsx(self.tableToList(True), file)

def main():
    app = QApplication(sys.argv)
    window = EliteOCR()
    if window.error_close:
       sys.exit() 
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    sys.exit(main()) 