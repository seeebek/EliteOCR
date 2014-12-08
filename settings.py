import sys
from os import environ
from os.path import isdir, dirname, split, realpath
from PyQt4.QtCore import QSettings, QString
from PyQt4.QtGui import QMessageBox, QFileDialog
from calibrate import CalibrateDialog

class Settings():
    def __init__(self, parent=None):
        self.parent = parent
        self.app_path = self.getPathToSelf()
        self.values = {}
        self.reg = QSettings('seeebek', 'eliteOCR')
        if self.reg.contains('settings_version'):
            if float(self.reg.value('settings_version', type=QString)) < 1.1:
                self.setDefaultExportOptions()
                self.setSettingsVersion()
                self.reg.sync()
                self.values = self.loadSettings()
            else:
                self.values = self.loadSettings()
        else:
            self.cleanReg()
            self.setAllDefaults()
            self.reg.sync()
            self.values = self.loadSettings()
            self.runCalibration()
            self.values = self.loadSettings()
    
    def __getitem__(self, key):
        if key in self.values:
            return self.values[key]
        else:
            raise KeyError("Key "+str(key)+" not found in settings.")
            
    def setValue(self, key, value):
        self.reg.setValue(key, value)
        
    def sync(self):
        """Save changes and reload settings"""
        self.reg.sync()
        self.values = self.loadSettings()
        
    def cleanReg(self):
        """Clean all registry entries (for old version or version not set)"""
        keys = self.reg.allKeys()
        for key in keys:
            self.reg.remove(key)
    
    def runCalibration(self):
        """Run Calibration process"""
        QMessageBox.information(self.parent, "Calibration neccessary", "The OCR areas need to be set."+\
            " Callibration dialog will open now. Please choose a screenshot file."+\
            " You can recalibrate at any time by clicking on Calibrate in Settings menu.")
        image = QFileDialog.getOpenFileName(None, "Open", self.values['screenshot_dir'])
        if image != "":
            calibrateDialog = CalibrateDialog(self, image)
            calibrateDialog.exec_()
            self.sync()

    def loadSettings(self):
        """Load all settings to a dict"""
        set = {'screenshot_dir': self.reg.value('screenshot_dir', type=QString),
               'export_dir': self.reg.value('export_dir', type=QString),
               'horizontal_exp': self.reg.value('horizontal_exp', type=bool),
               'last_export_format': self.reg.value('last_export_format', type=QString),
               'log_dir': self.reg.value('log_dir', type=QString),
               'auto_fill': self.reg.value('auto_fill', type=bool),
               'remove_dupli': self.reg.value('remove_dupli', type=bool),
               'cal_points': self.reg.value('cal_points', type=float),
               'img_res': self.reg.value('img_res', type=int),
               'create_nn_images': self.reg.value('create_nn_images', type=bool)}
        return set
        
    def setAllDefaults(self):
        """Set all settings to default values"""
        self.setDefaultAutoFill()
        self.setDefaultRemoveDupli()
        self.setDefaultCreateNNImg()
        self.setDefaultScreenshotDir()
        self.setDefaultLogDir()
        self.setDefaultExportDir()
        self.setSettingsVersion()
        
    def setSettingsVersion(self):
        self.reg.setValue('settings_version', "1.1")
        
    def setDefaultExportOptions(self):
        self.setValue('horizontal_exp', False)
        self.setValue('last_export_format', 'xlsx')
    
    def setDefaultAutoFill(self):
        self.reg.setValue('auto_fill', False)
        
    def setDefaultRemoveDupli(self):
        self.reg.setValue('remove_dupli', True)
        
    def setDefaultCreateNNImg(self):
        self.reg.setValue('create_nn_images', False) # opt-in
        
    def setDefaultScreenshotDir(self):
        if isdir(environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'):
            dir = environ['USERPROFILE']+'\\Pictures\\Frontier Developments\\Elite Dangerous'
        else:
            dir = self.app_path
        self.reg.setValue('screenshot_dir', dir)
        
    def setDefaultLogDir(self):
        if isdir(environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'):
            logdir = environ['USERPROFILE']+'\\AppData\\Local\\Frontier_Developments\\Products\\FORC-FDEV-D-1002\\Logs'
            self.reg.setValue('log_dir', logdir)
        else:
            QMessageBox.warning(None, "Warning", "The Game was not installed in the default "+\
                "location. Log directory could not be found. Please choose the directory in which "+\
                "you installed the game. Otherwise system names will not be added to the results.")
            logdir = QFileDialog.getExistingDirectory(None, "Choose", self.app_path)
            if logdir != "":
                if isdir(logdir + "\\Products\\FORC-FDEV-D-1002\\Logs"):
                    self.reg.setValue('log_dir', logdir+"\\Products\\FORC-FDEV-D-1002\\Logs")
                elif split(str(logdir))[1] == "Logs":
                    self.reg.setValue('log_dir', logdir)
                else:
                    QMessageBox.warning(None, "Warning", "Log directory not found.\n"+\
                        "You can add this directory later in settings menu. Until then your "+\
                        "results will not contain system names.")
                    self.reg.setValue('log_dir', self.app_path)
            else:
                self.reg.setValue('log_dir', self.app_path)
                
    def setDefaultExportDir(self):
        self.reg.setValue('export_dir', self.app_path)
        
    def getPathToSelf(self):
        """Return the path to EliteOCR.py or EliteOCR.exe"""
        if getattr(sys, 'frozen', False):
            application_path = dirname(sys.executable)
        elif __file__:
            application_path = dirname(__file__)
        return application_path
        