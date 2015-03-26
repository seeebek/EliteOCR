# -*- coding: utf-8 -*-
import random
import logging
import traceback
import sys
import getopt
#import time
import json
import codecs
from functools import partial
from datetime import datetime, timedelta
from time import strftime, strptime, time
from calendar import timegm
from os.path import split, splitext, isfile, isdir, dirname, realpath, exists, join
from os import makedirs, listdir, remove
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QMessageBox,\
                        QPixmap, QPen, QTableWidgetItem, QPushButton, QAction, QFont
from PyQt4.QtCore import Qt, QObject, QSize, QPoint, QSettings, QString, QTranslator, QTimer, SIGNAL
import cv2

from eliteOCRGUI import Ui_MainWindow
from customqlistwidgetitem import CustomQListWidgetItem
from help import HelpDialog
from update import UpdateDialog
from busydialog import BusyDialog
from settingsdialog import SettingsDialog
from editordialog import EditorDialog
from settings import Settings
from ocr import OCR
from qimage2ndarray import array2qimage
from eddnexport import EDDNExport
from threadworker import Worker
from export import Export
from info import InfoDialog
from xmloutput import XMLOutput

from ocrmethods import OCRAreasFinder

from openpyxl import Workbook
from ezodf import newdoc, Sheet

#plugins
import imp
#from plugins.BPC_Feeder.bpcfeeder_wrapper import BPC_Feeder

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

appversion = "0.5.4.1"
gui = False
logging.basicConfig(format='%(asctime)s %(levelname)s:\n%(message)s',filename='errorlog.txt',level=logging.WARNING)

def exception_handler(ex_cls, ex, tb):
    fulltb = ''.join(traceback.format_tb(tb))
    fulltb = fulltb.replace("<string>", "EliteOCR")
    fulltb = fulltb.replace("C:\\Users\\SEBAST~1\\Desktop\\RFACTO~2\\build\\EliteOCR\\out00-PYZ.pyz\\", "")
    fulltb = fulltb.replace("C:\\Users\\SEBAST~1\\Desktop\\RFACTO~2\\build\\EliteOCRcmd\\out00-PYZ.pyz\\", "")
    logging.critical(fulltb+'\n{0}: {1}\n'.format(ex_cls, ex))
    print "An error was encountered. Please read errorlog.txt"
    print gui
    if gui:
        QMessageBox.critical(None,"Error", "An error was encountered. Please read errorlog.txt")
    

sys.excepthook = exception_handler

class EliteOCR(QMainWindow, Ui_MainWindow):
    def __init__(self, app):            
        QMainWindow.__init__(self) #QMainWindow.__init__(self, None, Qt.FramelessWindowHint)
        self.setupUi(self)
        self.app = app
        self.settings = Settings(self)
        
        self.resizeElements()
        
        self.darkstyle = self.genDarkStyle()
        self.def_style = """
                    QWidget { font-size: 10pt; font-family: Consolas}
                    QLineEdit { font-size: 13pt; font-family: Consolas}
        """
        if self.settings["theme"] == "dark":
            self.dark_theme = True
            self.style = self.darkstyle
        else:
            self.dark_theme = False
            self.style = self.def_style
        self.app.setStyleSheet(self.style)
        
        self.appversion = appversion
        self.setupTable()
        self.export = Export(self)
        self.actionPublic_Mode.setChecked(self.settings["public_mode"])
        
        self.factor.setValue(self.settings["zoom_factor"])
        
        self.ocr_all_set = False
        self.color_image = None
        self.preview_image = None
        self.current_result = None
        self.newupd = None
        self.zoom = False
        self.minres = 0
        self.busyDialog = None
        self.fields = [self.name, self.sell, self.buy, self.demand_num, self.demand,
                       self.supply_num, self.supply]
        self.canvases = [self.name_img, self.sell_img, self.buy_img, self.demand_img,
                         self.demand_text_img, self.supply_img, self.supply_text_img]
        #setup buttons
        self.add_button.clicked.connect(self.addFiles)
        self.remove_button.clicked.connect(self.removeFile)
        self.remove_all_button.clicked.connect(self.removeAllFiles)
        self.add_all_button.clicked.connect(self.addAllScreenshots)
        self.save_button.clicked.connect(self.addItemToTable)
        self.skip_button.clicked.connect(self.nextLine)
        self.continue_button.clicked.connect(self.continueOCR)
        self.ocr_button.clicked.connect(self.performOCR)
        self.ocr_all.clicked.connect(self.runOCRAll)
        self.export_button.clicked.connect(self.export.exportToFile)
        self.bpc_button.clicked.connect(self.export.bpcExport)
        self.eddn_button.clicked.connect(self.export.eddnExport)
        self.clear_table.clicked.connect(self.clearTable)
        self.zoom_button.clicked.connect(self.drawOCRPreview)
        
        QObject.connect(self.actionHelp, SIGNAL('triggered()'), self.openHelp)
        QObject.connect(self.actionUpdate, SIGNAL('triggered()'), self.openUpdate)
        QObject.connect(self.actionAbout, SIGNAL('triggered()'), self.About)
        QObject.connect(self.actionOpen, SIGNAL('triggered()'), self.addFiles)
        QObject.connect(self.actionPreferences, SIGNAL('triggered()'), self.openSettings)
        QObject.connect(self.actionPublic_Mode, SIGNAL('triggered()'), self.toggleMode)
        QObject.connect(self.actionCommodity_Editor, SIGNAL('triggered()'), self.openEditor)
        
        self.error_close = False

        #set up required items for nn
        self.training_image_dir = unicode(self.settings.app_path.decode('windows-1252'))+u"\\nn_training_images\\"
        
        self.loadPlugins()
        self.restorePos()
        
        self.eddnthread = EDDNExport(self)
        QObject.connect(self.eddnthread, SIGNAL('finished(QString)'), self.export.eddnFinished)
        QObject.connect(self.eddnthread, SIGNAL('update(int,int)'), self.export.eddnUpdate)
        
        self.thread = Worker()
        self.connect(self.thread, SIGNAL("output(QString, QString)"), self.showUpdateAvailable)
        self.thread.check(self.appversion)
            
        if not self.settings.reg.contains('info_accepted'):
            self.infoDialog = InfoDialog()
            self.infoDialog.exec_()
        else:
            if not self.settings['info_accepted']:
                self.infoDialog = InfoDialog()
                self.infoDialog.exec_()
        
        self.checkAppConfigXML()
                
    def checkAppConfigXML(self):
        path = unicode(self.settings['log_dir']).encode('windows-1252')+"\\..\\AppConfig.xml"
        if isfile(path):
            file = codecs.open(path, 'r', "utf-8")
            file_content = file.read()
            file.close()
            start = file_content.find("<Network")
            end = file_content.find("</Network>")
            position = file_content.lower().find('verboselogging="1"', start, end)
            
            if position == -1:
                msg = _translate("EliteOCR","You don't have \"Verbose Logging\" enabled in your AppConfig.xml. It is necessary for automatic system name recognition. Do you want EliteOCR to enable it for you?", None)
                reply = QMessageBox.question(self, 'Change File', msg, _translate("EliteOCR","Yes", None), _translate("EliteOCR","No", None))
                if reply == 0:
                    file = codecs.open(unicode(self.settings['log_dir']).encode('windows-1252')+"\\..\\AppConfig_backup.xml", 'w', "utf-8")
                    file.write(file_content)
                    file.close()
                    
                    newfile = file_content[:start+8] + '\n      VerboseLogging="1"' + file_content[start+8:]

                    file = codecs.open(path, 'w', "utf-8")
                    file.write(newfile)
                    file.close()
                    QMessageBox.information(self,"Restart the Game", "Please restart the game to apply the change in AppConfig.xml")
                else:
                    return
    
    def resizeElements(self):
        fields = [self.system_name, self.station_name, self.name, self.sell, self.buy, self.demand_num, self.demand, self.supply_num, self.supply, self.label_12, self.file_label, self.system_not_found]
        for field in fields:
            field.setMinimumSize(QSize(0, self.settings['input_size']))
            field.setMaximumSize(QSize(16777215, self.settings['input_size']))
        canvases = [self.station_name_img, self.name_img, self.sell_img, self.buy_img, self.demand_img, self.demand_text_img, self.supply_img, self.supply_text_img]
        for canvas in canvases:
            canvas.setMinimumSize(QSize(0, self.settings['snippet_size']))
            canvas.setMaximumSize(QSize(16777215, self.settings['snippet_size']))
    
    def genDarkStyle(self):
        style = """
                    QWidget {{ background-color: #000; font-size: 10pt; font-family: Consolas}}
                    QLabel {{ color: {0};}}
                    QCheckBox {{ color: {0}; }}
                    QPushButton {{color: {2};
                                 background-color: #000;
                                 border: 1px solid {3};
                                 min-height: 13px;
                                 padding: 2px;}}
                    QToolButton {{color: {2};
                                 background-color: #000;
                                 border: 1px solid {3};
                                 min-height: 12px;
                                 padding: 2px;}}
                    QPushButton[enabled="false"]{{color: #555; border: 1px solid #555;}}
                    QToolButton[enabled="false"]{{color: #555; border: 1px solid #555;}}

                    QStatusBar {{ background-color: #000; color: {0};}}

                    QMenuBar {{ background-color: #000; color: {0};}}
                    QMenuBar::item {{ background-color: #000; color: {0};}}
                    QMenuBar::item:selected {{ background-color: #888; color: {0};}}

                    QMenu {{ background-color: #000; color: {0};}}
                    QMenu::item {{ background-color: #000; color: {0};}}
                    QMenu::item:selected {{ background-color: #888; color: {0};}}

                    QListWidget {{ background-color: #000; min-width: 150px}}
                    QFrame[frameShape="4"] {{ background-color: #888; }}
                    QFrame[frameShape="5"] {{ background-color: #888; }}

                    QGraphicsView {{ background-color: #000; border: 1px solid {4}}}
                    QTableWidget {{ background-color: #000; color: {0}; border: 1px solid {4}}}
                    QLineEdit {{ background-color: #000; border: 1px solid {4}; color: {1}; font-size: 13pt; font-family: Consolas}}
                    QComboBox {{  background-color: #000; border: 1px solid {4}; color: {1};}}
                    QComboBox:editable {{color: {1}; font-size: 11pt}}
                    QComboBox::down-arrow {{ image: url(:/ico/arrow.png); }}
                    QComboBox::drop-down:editable {{color: {1};}}
                    QHeaderView::section {{  background-color: #000; color: {0}; border: 1px solid {4}; padding: 2px; }}
                    QTableView QTableCornerButton::section {{ background: #000;}}
                    QSplitter {{ background-color: #0a0; color: #a00; }}
                    QProgressBar {{ border: 1px solid {4}; background-color: #000;}}
                    QProgressBar::chunk {{ background-color: #0a0; width: 20px; }}
                    QDoubleSpinBox {{ background-color: #888;}}
                    QSpinBox {{ background-color: #888;}}
                    QWebView {{ background-color: #888;}}
                    QTreeView {{ color: {0}; border: 1px solid {4}}}
                    QTabBar::tab {{ background-color: #000; color:{0}; border: 1px solid {4}; padding: 4px;}}
                    QListView {{ color: {1}; border: 1px solid {4}}}
        """.format(str(self.settings['label_color']),str(self.settings['input_color']),str(self.settings['button_color']),str(self.settings['button_border_color']),str(self.settings['border_color']))
        
        return style
    
    def showUpdateAvailable(self, dir, appversion):
        self.newupd = (dir, appversion)
        self.statusbar.showMessage(unicode(_translate("EliteOCR","New version of EliteOCR available: %s To download it go to Help > Update", None)) % appversion, 0)
    
    def restorePos(self):
        self.settings.reg.beginGroup("MainWindow")
        self.resize(self.settings.reg.value("size", QSize(400, 400)).toSize())
        self.move(self.settings.reg.value("pos", QPoint(200, 200)).toPoint())
        if self.settings.reg.value("maximized", False, type=bool):
            self.showMaximized()
        self.settings.reg.endGroup()
    
    def closeEvent(self, event):
        self.settings.reg.beginGroup("MainWindow")
        self.settings.reg.setValue("size", self.size())
        self.settings.reg.setValue("pos", self.pos())
        if self.windowState() == Qt.WindowMaximized:
            self.settings.reg.setValue("maximized", True)
        else:
            self.settings.reg.setValue("maximized", False)
        self.settings.reg.endGroup()
        self.settings.reg.setValue("public_mode", self.actionPublic_Mode.isChecked())
        self.settings.reg.setValue("zoom_factor", self.factor.value())
        self.settings.reg.sync()
        if not self.busyDialog is None:
            self.busyDialog.close()
        event.accept()
    
    def toggleMode(self):
        if self.actionPublic_Mode.isChecked():
            msg = _translate("EliteOCR","Switching to public mode will clear the result table! Are you sure you want to do it?", None)
            reply = QMessageBox.question(self, 'Mode', msg, _translate("EliteOCR","Yes", None), _translate("EliteOCR","No", None))

            if reply == 0:
                self.clearTable()
                self.cleanAllFields()
                self.cleanAllSnippets()
            else:
                self.actionPublic_Mode.setChecked(False)
        else:
            msg = _translate("EliteOCR","Switching to private mode will disable BPC and EDDN Export! Are you sure you want to do it?", None)
            reply = QMessageBox.question(self, 'Mode', msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.enableButton(self.bpc_button, False)
                self.enableButton(self.eddn_button,False)
            else:    
                self.actionPublic_Mode.setChecked(True)
    
    def loadPlugins(self):
        """Load known plugins"""
        #Trade Dangerous Export by gazelle (bgol)    
        if isfile(self.settings.app_path+"\\plugins\\TD_Export\\TD_Export.py"):
            plugin2 = imp.load_source('TD_Export', self.settings.app_path+\
                                     "\\plugins\\TD_Export\\TD_Export.py")
            self.tdexport = plugin2.TD_Export(self, self.settings.app_path.decode('windows-1252'))
            self.tdexport_button = QPushButton(self.centralwidget)
            self.tdexport_button.setText("Trade Dangerous Export")
            self.enableButton(self.tdexport_button, False)
            self.horizontalLayout_4.addWidget(self.tdexport_button)
            self.tdexport_button.clicked.connect(lambda: self.tdexport.run(self.export.tableToList(False, True)))
    
    def enablePluginButtons(self):
        if 'tdexport' in dir(self):
            if self.tdexport != None:
                self.enableButton(self.tdexport_button, True)
        
    def disablePluginButtons(self):
        if 'tdexport' in dir(self):
            if self.tdexport != None:
                self.enableButton(self.tdexport_button, False)

    def About(self):
        QMessageBox.about(self,"About", "EliteOCR\nVersion "+self.appversion+"\n\n"+\
        "Contributors:\n"+\
        "Seeebek, CapCap, Gazelle, GMib, Ph.Baumann\n\n"+\
        "EliteOCR is capable of reading the entries in Elite: Dangerous markets screenshots.\n\n")
        
    def setupTable(self):
        """Add columns and column names to the table"""
        """
        "self.result_table.setColumnCount(11)
        self.result_table.setHorizontalHeaderLabels(['station', 'commodity', 'sell', 'buy',
                                                     'demand', 'dem', 'supply',
                                                     'sup', 'timestamp','system','img_height'])
        """
        self.result_table.setColumnHidden(8, True)
        self.result_table.setColumnHidden(10, True)
        #self.result_table.setColumnHidden(11, True)
        pass

    def openHelp(self):
        
        self.helpDialog = HelpDialog(self.settings.app_path.decode('windows-1252'))
        self.helpDialog.setModal(False)
        self.helpDialog.show()
        
    def openUpdate(self):
        
        self.updateDialog = UpdateDialog(self.settings.app_path.decode('windows-1252'), self.appversion, self.newupd)
        self.updateDialog.setModal(False)
        self.updateDialog.show()
    
    def openSettings(self):
        """Open settings dialog and reload settings"""
        settingsDialog = SettingsDialog(self.settings)
        settingsDialog.exec_()
        if self.settings["theme"] == "dark":
            self.dark_theme = True
            self.darkstyle = self.genDarkStyle()
            self.style = self.darkstyle
        else:
            self.dark_theme = False
            self.style = self.def_style
        #self.app.setStyleSheet("")
        self.app.setStyleSheet(self.style)
        self.resizeElements()
    
    def openEditor(self):
        editorDialog = EditorDialog(self.settings)
        editorDialog.exec_()

    def addAllScreenshots(self):
        dir = unicode(self.settings['screenshot_dir']).encode('windows-1252')
        #gen = (join(dir, file).decode('windows-1252') for file in listdir(dir) if isfile(join(dir, file)))
        gen = [join(dir, file).decode('windows-1252') for file in listdir(dir) if file.endswith('.bmp')]
        files = []
        for file in gen:
            files.append(file)
        self.addFiles(files)
    
    def addFiles(self, screenshots = None):
        """Add files to the file list."""
        if screenshots:
            files = screenshots
        else:
            if self.settings["native_dialog"]:
                files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'])
            else:
                files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'], options = QFileDialog.DontUseNativeDialog)

        if files == []:
            return
        first_item = None
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)
        counter = 0
        for file in files:
            file1 = unicode(file).encode('windows-1252')
            item = CustomQListWidgetItem(split(file1)[1], file1, self.settings)
            if first_item == None:
                first_item = item
            self.file_list.addItem(item)
            counter+=1
            self.progress_bar.setValue(counter)
        self.progress_bar.setValue(0)
        self.file_list.itemClicked.connect(self.selectFile)
        self.save_button.setEnabled(False)
        self.enableButton(self.skip_button, False)
        #self.cleanAllFields()
        #self.cleanAllSnippets()
        if first_item !=None:
            self.selectFile(first_item)
        if self.ocr_button.isEnabled() and self.file_list.count() > 1:
            self.enableButton(self.ocr_all, True)
        self.cleanAllFields()
        self.cleanAllSnippets()
        
    def removeAllFiles(self):
        files = self.file_list.count()
        for i in xrange(files):
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
        self.remove_button.setEnabled(False)
        self.remove_all_button.setEnabled(False)
        self.ocr_button.setEnabled(False)
        self.enableButton(self.zoom_button, False)
    
    def softRemoveFile(self):
        item = self.file_list.currentItem()
        self.file_list.takeItem(self.file_list.currentRow())
        del item
    
    def removeFile(self):
        """Remove selected file from file list."""
        item = self.file_list.currentItem()
        self.file_list.takeItem(self.file_list.currentRow())
        del item
        self.file_label.setText("-")
        scene = QGraphicsScene()
        self.previewSetScene(scene)
        self.save_button.setEnabled(False)
        self.enableButton(self.skip_button, False)
        self.cleanAllFields()
        self.cleanAllSnippets()
        if self.file_list.currentItem():
            self.selectFile(self.file_list.currentItem())
        if self.file_list.count() == 0:
            self.remove_button.setEnabled(False)
            self.remove_all_button.setEnabled(False)
            self.ocr_button.setEnabled(False)
            self.enableButton(self.zoom_button, False)
        if self.file_list.count() < 2:
            self.enableButton(self.ocr_all, False)
    
    def selectFile(self, item):
        """Select clicked file and shows prewiev of the selected file."""
        self.cleanAllFields()
        self.cleanAllSnippets()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(20)
        self.progress_bar.setValue(0)
        self.color_image = item.loadColorImage()
        self.progress_bar.setValue(10)
        self.preview_image = item.loadPreviewImage(self.color_image, self)
        self.progress_bar.setValue(20)
        self.ocr_all_set = False
        #font = QFont("Consolas", 11)
        self.system_not_found.setText("")
        if len(item.system) == 0:
            self.system_not_found.setText(_translate("EliteOCR","System name not found in log files. Please read Help for more info.", None))
        self.system_name.setText(item.system)
        if not item.station is None:
            self.station_name.setText(item.station)
        #self.system_name.setFont(font)
        self.file_list.setCurrentItem(item)
        self.file_label.setText(item.text())
        self.setPreviewImage(self.preview_image)
        self.remove_button.setEnabled(True)
        self.remove_all_button.setEnabled(True)
        self.enableButton(self.continue_button, False)
        if not item.valid_market:
            self.system_not_found.setText(_translate("EliteOCR","File was not recognized as a valid market screenshot. Please read Help for more info.", None))
            self.progress_bar.setValue(0)
            return
        self.ocr_button.setEnabled(True)
        self.enableButton(self.zoom_button, True)
        if self.file_list.count() > 1:
            self.enableButton(self.ocr_all, True)
        self.progress_bar.setValue(0)
    
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
        self.busyDialog = BusyDialog(self)
        self.busyDialog.show()
        QApplication.processEvents()
        if self.file_list.currentItem().valid_market:
            self.current_result = OCR(self, self.color_image, self.file_list.currentItem().ocr_areas, self.settings["ocr_language"], self.file_list.currentItem())
            self.busyDialog.close()
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
            if len(self.current_result.commodities) < 1:
                QMessageBox.critical(self,"Error", "No results found!\nYou might be using an unsupported HUD color. Please read help for more information.")
                return 
            self.drawOCRPreview()
            self.markCurrentRectangle()
            self.drawStationName()
            self.skip_button.setEnabled(True)
            self.enableButton(self.save_button, True)
            self.processOCRLine()
            self.system_name.setFocus()
            if self.settings['create_nn_images']:
                self.saveStationForTraining()
        else:
            self.nextFile()
        
    def addItemToTable(self):
        """Adds items from current OCR result line to the result table."""
        tab = self.result_table
        res_station = unicode(self.station_name.text()).title()
        row_count = tab.rowCount()
        self.export_button.setEnabled(True)
        if self.actionPublic_Mode.isChecked():
            self.bpc_button.setEnabled(True)
            self.eddn_button.setEnabled(True)
        self.enablePluginButtons()
        self.enableButton(self.clear_table, True)
        # check if no stock and not purchased
        if self.demand_num.text() == "" and self.supply_num.text() == "":
            self.nextLine()
            return
        #check for duplicates
        duplicate = False
        if self.settings["remove_dupli"]:
            for i in range(row_count):
                station = unicode(tab.item(i, 0).text()).title()
                com1 = unicode(tab.item(i, 1).text()).title()
                com2 = unicode(self.fields[0].text()).replace(',', '').title()
                if station == res_station and com1 == com2:
                    duplicate = True
        
        if not duplicate:
            self.current_result.station.name.value = self.station_name.text()
            tab.insertRow(row_count)
            newitem = QTableWidgetItem(unicode(res_station).title().replace("'S", "'s"))
            tab.setItem(row_count, 0, newitem)
            for n, field in enumerate(self.fields):
                newitem = QTableWidgetItem(unicode(field.text()).replace(',', '').title())
                tab.setItem(row_count, n+1, newitem)
            newitem = QTableWidgetItem(self.file_list.currentItem().timestamp)
            tab.setItem(row_count, 8, newitem)
            newitem = QTableWidgetItem(self.system_name.text())
            tab.setItem(row_count, 9, newitem)
            newitem = QTableWidgetItem(unicode(self.file_list.currentItem().market_width))
            tab.setItem(row_count, 10, newitem)
            tab.resizeColumnsToContents()
            tab.resizeRowsToContents()
            if self.settings['create_nn_images']:
                self.saveValuesForTraining()
        self.nextLine()

    def saveValuesForTraining(self):
        """Get OCR image/user values and save them away for later processing, and training
        neural net"""
        cres = self.current_result
        res = cres.commodities[self.OCRline]
        if not exists(self.training_image_dir):
            makedirs(self.training_image_dir)
        if not exists(self.training_image_dir+"\\text"):
            makedirs(self.training_image_dir+"\\text")
        if not exists(self.training_image_dir+"\\numbers"):
            makedirs(self.training_image_dir+"\\numbers")
        w = len(self.current_result.contrast_commodities_img)
        h = len(self.current_result.contrast_commodities_img[0])
        for index, field, canvas, item in zip(range(0, len(self.canvases) - 1),
                                              self.fields, self.canvases, res.items):

            val = unicode(field.text())#.replace(',', '')
            if field in [self.sell, self.buy, self.demand_num, self.supply_num]:
                if val:
                    snippet = self.cutImage(cres.contrast_commodities_img, item)
                    #cv2.imshow('snippet', snippet)
                    imageFilepath = self.training_image_dir + u'\\numbers\\' + unicode(val) + u'_' + unicode(w) + u'x' + unicode(h) +\
                                    u'-' + unicode(int(time())) + u'-' +\
                                    unicode(random.randint(10000, 100000)) + u'.png'
                    cv2.imwrite(imageFilepath.encode('windows-1252'), snippet)
            elif field in [self.name]:
                if val:
                    snippet = self.cutImage(cres.contrast_commodities_img, item)
                    #cv2.imshow('snippet', snippet)
                    imageFilepath = self.training_image_dir + u'\\text\\' + unicode(val) + u'_' + unicode(w) + u'x' + unicode(h) +\
                                    u'-' + unicode(int(time())) + u'-' +\
                                    unicode(random.randint(10000, 100000)) + u'.png'
                    cv2.imwrite(imageFilepath.encode('windows-1252'), snippet)
        
        
    def saveStationForTraining(self):
        cres = self.current_result
        if not exists(self.training_image_dir):
            makedirs(self.training_image_dir)
        if not exists(self.training_image_dir+"\\text"):
            makedirs(self.training_image_dir+"\\text")
        w = len(self.current_result.contrast_commodities_img)
        h = len(self.current_result.contrast_commodities_img[0])
        snippet = self.cutImage(cres.contrast_station_img, cres.station.name)
        val = self.station_name.text()
        imageFilepath = self.training_image_dir + u'\\text\\' + unicode(val) + u'_' + unicode(w) + u'x' + unicode(h) +\
                                u'-' + unicode(int(time())) + u'-' +\
                                unicode(random.randint(10000, 100000)) + u'.png'
        cv2.imwrite(imageFilepath.encode('windows-1252'), snippet)
    
    def cutImageForTraining(self, image, item):
        """Cut image snippet from a big image using points from item."""
        snippet = image[item.y1:item.y2,
                        item.x1:item.x2]
        return snippet
    
    def continueOCR(self):
        if self.ocr_all_set:
            self.nextFile()
        else:
            if self.settings['delete_files']:
                print "Deleted (continueOCR 458):"
                print self.file_list.currentItem().text()
                remove(self.file_list.currentItem().hiddentext)
                self.removeFile()
        self.enableButton(self.continue_button, False)
    
    def nextLine(self):
        """Process next OCR result line."""
        self.markCurrentRectangle(QPen(Qt.green))
        self.OCRline += 1
        if len(self.previewRects) > self.OCRline:
            self.markCurrentRectangle()
            self.processOCRLine()
            self.name.setFocus()
        else:
            self.save_button.setEnabled(False)
            self.enableButton(self.skip_button, False)
            self.cleanAllFields()
            self.cleanAllSnippets()
            if self.ocr_all_set:
                if self.settings['pause_at_end']:
                    self.enableButton(self.continue_button, True)
                else:
                    self.nextFile()
            else:
                if self.settings['delete_files']:
                    if self.settings['pause_at_end']:
                        self.enableButton(self.continue_button, True)
                    else:
                        print "Deleted (nextLine 486):"
                        print self.file_list.currentItem().text()
                        remove(self.file_list.currentItem().hiddentext)
                        self.removeFile()
                
                
    def nextFile(self):
        """OCR next file"""
        if self.file_list.currentRow() < self.file_list.count()-1:
            if self.settings['delete_files']:
                print "Deleted (nextFile 496):"
                print self.file_list.currentItem().text()
                remove(self.file_list.currentItem().hiddentext)
                self.softRemoveFile()
            else:
                self.file_list.setCurrentRow(self.file_list.currentRow() + 1)
            self.color_image = self.file_list.currentItem().loadColorImage()
            self.preview_image = self.file_list.currentItem().loadPreviewImage(self.color_image, self)
            self.performOCR()
            #font = QFont("Consolas", 11)
            if self.OCRline == 0:
                if len(self.file_list.currentItem().system) > 0:
                    self.system_not_found.setText("")
                    self.system_name.setText(self.file_list.currentItem().system)
                    if not self.file_list.currentItem().station is None:
                        self.station_name.setText(self.file_list.currentItem().station)
                    #self.system_name.setFont(font)
                else:
                    self.system_name.setText("")
                    #self.system_name.setFont(font)
                    self.system_not_found.setText(_translate("EliteOCR","System name not found in log files. Make sure log directory path is set up correctly or add system name manually in the field below. Note: System name is necessary for BPC import!",None))
                #self.system_name.setFocus()
                #self.system_name.selectAll()
        else:
            if self.settings['delete_files']:
                print "Deleted (nextFile 520):"
                print self.file_list.currentItem().text()
                remove(self.file_list.currentItem().hiddentext)
                self.softRemoveFile()
            
    def clearTable(self):
        """Empty the result table."""
        self.result_table.setRowCount(0)
        self.clear_table.setEnabled(False)
        self.export_button.setEnabled(False)
        self.bpc_button.setEnabled(False)
        self.enableButton(self.eddn_button, False)
        self.disablePluginButtons()
    
    def processOCRLine(self):
        """Process current OCR result line."""
        if len(self.current_result.commodities) > self.OCRline:
            #font = QFont("Consolas", 11)
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
            if self.file_list.currentItem().market_width < 1065 and self.actionPublic_Mode.isChecked():
                autofill = False
                self.save_button.setEnabled(False)
                self.enableButton(self.skip_button, True)
                QTimer.singleShot(1200, partial(self.enableButton, self.save_button, True));
                #QTimer.singleShot(1500, partial(self.skip_button.setEnabled, True));
                        
            for field, canvas, item in zip(self.fields, self.canvases, res.items):
                if item != None:
                    #field.clear()
                    #field.addItems(item.optional_values)
                    field.setText(item.value)
                    #field.lineEdit().setFont(font)
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
        #c = random.random()
        if self.dark_theme:
            if c > 0.83:
                color  = "#000"
            if c <= 0.83 and c >0.67:
                color = "#666600"
            if c <= 0.67 and c >0.5:
                color = "#665100"
            if c <= 0.5 and c >0.34:
                color = "#663e00"
            if c <= 0.34 and c >0.17:
                color = "#662900"
            if c <= 0.17:
                color = "#661500"
        else:
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
        field.setStyleSheet("background: "+color+";")


        
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
        if self.dark_theme: 
            snippet = 255 - snippet
        #cv2.imwrite('snippets/'+unicode(self.currentsnippet)+'.png',snippet)
        #self.currentsnippet += 1
        processedimage = array2qimage(snippet)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        
        pix = pix.scaled(graphicsview.width(), graphicsview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        scene = QGraphicsScene()
        scene.addPixmap(pix)
        graphicsview.setScene(scene)
        graphicsview.show()
    
    def drawStationName(self):
        """Draw station name snippet to station_name_img"""
        res = self.current_result
        name = res.station.name
        #self.station_name.setText('')
        #self.station_name.clear()
        #self.station_name.addItems(name.optional_values)
        if not self.file_list.currentItem().station is None:
                self.station_name.setText(self.file_list.currentItem().station)
        else:
            self.station_name.setText(name.value)
        #font = QFont("Consolas", 11)
        #self.station_name.lineEdit().setFont(font)
        #self.setConfidenceColor(self.station_name, name)
        img = self.cutImage(res.contrast_station_img, name)
        if self.dark_theme: 
            img = 255 - img
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
        self.save_button.setEnabled(False)
        self.enableButton(self.skip_button, False)
    
    def cleanField(self, field):
        field.setText('')
        if self.dark_theme:
            field.setStyleSheet("background: #000;")
        else:
            field.setStyleSheet("background: #fff;")
        #field.lineEdit().setStyleSheet("")
        #field.clear()
            
    def cleanAllSnippets(self):
        for field in self.canvases:
            self.cleanSnippet(field)
        self.cleanSnippet(self.station_name_img)
    
    def cleanSnippet(self, graphicsview):
        scene = QGraphicsScene()
        graphicsview.setScene(scene)
        
    def enableButton(self, button, switch):
        button.setEnabled(switch)
        if self.dark_theme:
            self.app.setStyleSheet("")
            self.app.setStyleSheet(self.style)
            self.repaint()

def translateApp(app, qtTranslator):
    if getattr(sys, 'frozen', False):
        application_path = dirname(sys.executable)
    elif __file__:
        application_path = dirname(__file__)
    else:
        application_path = "./"
    settings = QSettings('seeebek', 'eliteOCR')
    ui_language = str(settings.value('ui_language', 'en', type=QString))
    #application_path = unicode(application_path).encode('windows-1252')
    
    if not ui_language == 'en':
        path = application_path+"\\translations\\"
        if isdir(path):
            qtTranslator.load("EliteOCR_"+ui_language, path.decode('windows-1252'))
            app.installTranslator(qtTranslator)
            """
            dir = listdir(path)
            translators = translator_list
            for file in dir:
                qtTranslator = QTranslator()
                if qtTranslator.load(application_path+"\\translations\\de\\"+splitext(file)[0]):
                    translators.append(qtTranslator)
            for translator in translators:
                app.installTranslator(translator)
            """
def usage():
    print """Usage: EliteOCR -i input [-o output] [-s system] [-l lang] [-t]
    
    -i --input:     path to an image file
    -o --output:    defines where results should be written, default output.xml
    -s --system:    overrides the system name from log files
    -l --lang:      OCR language, must be one from this list: eng, deu, fra
    -h --help:      shows this help page
    -t --translate: translate results to english
    -v --version:   version info
    
Example: EliteOCR.exe -i Screenshot_0014.bmp -o result.xml -s "Test System" -l fra -t
    """
def ocr(language, input, output, system, translate):
    settings = Settings()
    if isfile(input):
        sys.stdout.write("\r[=         ]")
        sys.stdout.flush()
        item = CustomQListWidgetItem(split(input)[1], input, settings)
        color_img = item.loadColorImage()
        h, w, c = color_img.shape
        item.img_height = h
        item.ocr_areas = OCRAreasFinder(color_img)
        sys.stdout.write("\r[==        ]")
        sys.stdout.flush()
        item.market_width = item.ocr_areas.market_width
        item.hud_color = item.ocr_areas.hud_color
        points = item.ocr_areas.market_table
        item.valid_market = item.ocr_areas.valid
        if item.market_width < 1065:
            print "Image too small! Minimum market width required: 1065px, given: "+str(item.market_width)+"px"
            return 1
        result = OCR(None, color_img, item.ocr_areas, language, item)
        sys.stdout.write("\r")
        sys.stdout.flush()
        XMLOutput(language, input, output, item, result, system, w, h, translate)
        return 0
    else:
        print "Input file not found!"
        return 1
            
def main(argv):
    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv,"hvtl:i:o:s:",["help","version","translate","lang=","input=","output=","system="])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        ocr_lang = "eng"
        inputfile = ""
        outputfile = "output.xml"
        translate = False
        system = None
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-v", "--version"):
                print 'EliteOCR version: '+str(appversion)
                sys.exit()
            elif opt in ("-t", "--translate"):
                translate = True
            elif opt in ("-l", "--lang"):
                ocr_lang = arg
            elif opt in ("-i", "--input"):
                inputfile = arg
            elif opt in ("-o", "--output"):
                outputfile = arg
            elif opt in ("-s", "--system"):
                system = arg
        ocr(ocr_lang, inputfile, outputfile, system, translate)
    else:
        global gui
        gui = True
        app = QApplication(sys.argv)
        qtTranslator = QTranslator()
        translateApp(app, qtTranslator)

              
        window = EliteOCR(app)
        if window.error_close:
           sys.exit() 
        window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
