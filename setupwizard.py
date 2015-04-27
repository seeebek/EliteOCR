# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWizard, QFileDialog, QListWidgetItem
from PyQt4.QtCore import QObject, SIGNAL
from setupwizardUI import Ui_SetupWizard
from platform import system
import os
from os import environ, listdir
from os.path import isdir, isfile
from settings import Settings
import codecs
from engine import OCRAreasFinder

#from mmcq import get_palette

class SetupWizard(QWizard, Ui_SetupWizard):
    def __init__(self, settings):
        QWizard.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.path_input.textChanged.connect(self.checkLogValid)
        self.browse_log_path.clicked.connect(self.browseLogPath)
        self.screenshot_dir_browse.clicked.connect(self.browseScreenshotPath)
        self.export_dir_browse.clicked.connect(self.browseExportPath)
        
        self.wizardPage1.fullfilled = True
        self.wizardPage2.pageCreated.connect(self.logWork)
        self.wizardPage3.pageCreated.connect(self.AppConfigWork)
        self.wizardPage3.fullfilled = True
        self.wizardPage4.pageCreated.connect(self.PathsWork)
        self.wizardPage4.fullfilled = True
        self.wizardPage5.pageCreated.connect(self.showSummary)
        self.wizardPage5.fullfilled = True

    def accept(self):
        """
        self.settings.setValue('label_color', self.dominant)
        self.settings.setValue('input_color', self.dominant)
        self.settings.setValue('button_color', self.dominant)
        self.settings.setValue('button_border_color', self.dominant)
        self.settings.setValue('border_color', self.dominant)
        """
        #self.settings.setValue('contrast', self.contrast)
        self.settings.setValue('log_dir', self.path_input.text())
        self.settings.setValue('screenshot_dir', self.screenshot_dir.text())
        self.settings.setValue('export_dir', self.export_dir.text())
        self.settings.sync()
        self.close()
    
    def showSummary(self):
        text = "Log directory:\n"
        text += unicode(self.path_input.text())+"\n\n"
        text += "Screenshot directory:\n"
        text += unicode(self.screenshot_dir.text())+"\n\n"
        text += "Export directory:\n"
        text += unicode(self.export_dir.text())+"\n\n"
        text += "AppConfig.xml found:\n"
        text += unicode(self.appconf_found.text())+"\n\n"
        text += "Verbose logging enabled in AppConfig.xml:\n"
        text += unicode(self.verbose_enabled.text())+"\n\n"
        #text += "OCR contrast value for HUD color:\n"
        #text += unicode(self.contrast)+"\n\n"
        self.summary.setText(text)
        """
        item = unicode(self.screenshot_list.item(0).text())
        image = cv2.imread(item)
        palette = get_palette(image)
        buttons = [self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8, self.c9]
        for i in range(len(buttons)):
            color = '#%02x%02x%02x' % palette[i]
            self.settings.setValue('color'+unicode(i+1), color)
            buttons[i].setStyleSheet("background:"+unicode(color))
        """

    def PathsWork(self):
        if 'screenshot_dir' in self.settings.values:
            self.screenshot_dir.setText(self.settings['screenshot_dir'])
        if 'export_dir' in self.settings.values:
            self.export_dir.setText(self.settings['export_dir'])
    
    def AppConfigWork(self):
        path = unicode(self.path_input.text())+ os.sep +".."+ os.sep +"AppConfig.xml"
        if isfile(path):
            self.appconf_found.setText("Yes")
            
            file = codecs.open(path, 'r', "utf-8")
            file_content = file.read()
            file.close()
            start = file_content.find("<Network")
            end = file_content.find("</Network>")
            position = file_content.lower().find('verboselogging="1"', start, end)
            
            if position == -1:
                self.verbose_enabled.setText("No")
                self.verbose_button.setEnabled(True)
            else:
                self.verbose_enabled.setText("Yes")
            
    def browseLogPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", ".")
        if not dir is None and dir != "":
            self.path_input.setText(dir)
    
    def browseScreenshotPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", ".")
        if not dir is None and dir != "":
            self.screenshot_dir.setText(dir)
            
    def browseExportPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", ".")
        if not dir is None and dir != "":
            self.export_dir.setText(dir)
    
    def checkLogValid(self):
        if isdir(unicode(self.path_input.text())):
            path = unicode(self.path_input.text())+ os.sep +".."+ os.sep +"AppConfig.xml"
            if isfile(path):
                self.valid_path.setText("Yes")
                return
                
        self.valid_path.setText("No")
    
    def logWork(self):
        sys = system()
        self.operating_system.setText(sys)
        if sys == 'Windows':
            self.findLogPathWin()
            
    def findLogPathWin(self):
        #standard Path
        path = environ['USERPROFILE']+ os.sep +"AppData"+ os.sep +"Local"+ os.sep +"Frontier_Developments"+ os.sep +"Products"+ os.sep
        #path = "."
        if isdir(path):
            dirlist = listdir(path)
            for dir in dirlist:
                if dir[:9] == "FORC-FDEV":
                    if isdir(path + dir + os.sep +"Logs"):
                        self.standard_path.setText("Yes")
                        self.path_input.setText(path + dir + os.sep +"Logs")
                        self.wizardPage2.fullfilled = True
                        return
            self.standard_path.setText("No")
        
        from _winreg import EnumValue, ConnectRegistry, OpenKey, EnumValue, EnumKey, HKEY_LOCAL_MACHINE
        aReg = ConnectRegistry(None,HKEY_LOCAL_MACHINE)
        aKey = OpenKey(aReg, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        for i in range(1024):
            try:
                asubkey_name = EnumKey(aKey,i)
                asubkey = OpenKey(aKey,asubkey_name)
                for j in range(30):
                    try:
                        test = EnumValue(asubkey, j)
                        if test[0] == "Publisher" and test[1] == "Frontier Developments":
                            custpath = self.getInstallPath(asubkey, EnumValue)
                            print custpath
                            custpath += "Products"+ os.sep +""
                            if isdir(custpath):
                                dirlist = listdir(custpath)
                                for dir in dirlist:
                                    if dir[:9] == "FORC-FDEV":
                                        if isdir(custpath + dir + os.sep +"Logs"):
                                            self.custom_path.setText("Yes")
                                            self.path_input.setText(custpath + dir + os.sep + "Logs")
                                            self.wizardPage2.fullfilled = True
                                            return
                                            
                    except:
                        break
            except EnvironmentError:
                break
        self.custom_path.setText("No")
                    
    def getInstallPath(self, subkey, EnumValue):
        for j in range(30):
            try:
                test = EnumValue(subkey, j)
                if test[0] == "InstallLocation":
                    return test[1]
            except:
                break
