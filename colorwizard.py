# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import QWizard, QFileDialog, QListWidgetItem
from PyQt4.QtCore import QObject, SIGNAL
from colorwizardUI import Ui_ColorCalibrationWizard
from settings import Settings
from calibrator import Calibrator

class ColorCalibrationWizard(QWizard, Ui_ColorCalibrationWizard):
    def __init__(self, settings):
        QWizard.__init__(self)
        self.setupUi(self)
        self.settings = settings
        
        self.add_screenshots.clicked.connect(self.AddFiles)
        self.wizardPage2.pageCreated.connect(self.AnalyzeImg)
        self.contrast = 0.0
    
    def accept(self):
        self.settings.setValue('contrast', self.contrast)
        self.settings.sync()
        self.close()
    
    def AddFiles(self):
        files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'])
        if files == []:
            return
        first_item = None
        for file in files:
            if self.screenshot_list.count() >= 5:
                break
            file1 = unicode(file).encode(sys.getfilesystemencoding())
            item = QListWidgetItem(file1)
            self.screenshot_list.addItem(item)
            
        if self.screenshot_list.count() >= 3:
            self.wizardPage1.fullfilled = True
            self.wizardPage1.completeChanged.emit()
            
    def threadFinished(self, result, errors, result_list):
        self.contrast = result
        rel_error = errors/self.screenshot_list.count()
        
        information = "Calibration finished.\nResulting optimal contrast value for your HUD color settings: "+unicode(result) +"\n"
        information += "OCR Errors: "+unicode(errors)+"\n\n"
        if rel_error == 0:
            information += "Your screenshots seem to have perfect size and contrast. OCR accuracy should be almost 100%.\n\n"
        elif rel_error < 4:
            information += "Your screenshots seem to have good size and contrast. OCR accuracy should be high enough for numbers, possible inaccuracies in the text will be corrected by dictionary comparison.\n\n"
        elif rel_error < 10:
            information += "Your screenshots seem to have sufficient size and contrast. You should check your results for possible errors. Especially 6,8 and 9 could get mixed up. Please consider using higher resolution, lower FOV or higher contrast HUD color.\n\n"
        else:
            information += "Your screenshots are not usable for OCR. Use higher resolution, lower FOV or higher contrast HUD colors and perform the calibration again.\n\n"

        for i in range(len(result_list)):
            information += "Image "+unicode(i+1)+"\n"
            information += "Valid market screenshot: "+unicode(result_list[i][0])+"\n"
            information += "Resolution: "+unicode(result_list[i][1])+"x"+unicode(result_list[i][2])+"\n"
            information += "Market width: "+unicode(result_list[i][3])+"\n\n"
        
        self.scr_result.setPlainText(information)
        self.wizardPage2.fullfilled = True
        self.wizardPage2.completeChanged.emit()
    
    def updateSteps(self, steps):
        self.analyzing_progress.setMaximum(steps)
        self.repaint()
    
    def updateProgress(self, time_left):
        self.time_left.setText(unicode(time_left)+"s")
        self.analyzing_progress.setValue(self.analyzing_progress.value()+1)
        self.repaint()
    
    def AnalyzeImg(self):
        imglist = []
        for i in range(self.screenshot_list.count()):
            item = self.screenshot_list.item(i)
            imglist.append(unicode(item.text()))
        language = unicode(self.ocr_language.currentText())
        self.calibratorthread = Calibrator(self, imglist, language)
        QObject.connect(self.calibratorthread, SIGNAL('finished(float, int, PyQt_PyObject)'), self.threadFinished)
        QObject.connect(self.calibratorthread, SIGNAL('steps(int)'), self.updateSteps)
        QObject.connect(self.calibratorthread, SIGNAL('progress(int)'), self.updateProgress)
        self.calibratorthread.execute()