# -*- coding: utf-8 -*-
import sys
import random
import os
from os import environ
from os.path import isdir, dirname, split, realpath
from PyQt4.QtCore import QSettings, QString
from PyQt4.QtGui import QMessageBox, QFileDialog

class Settings():
    def __init__(self, parent=None):
        self.parent = parent
        self.app_path = self.getPathToSelf()
        self.values = {}
        self.reg = QSettings('seeebek', 'eliteOCR')
        self.userprofile = self.getUserProfile()
        if self.reg.contains('settings_version'):
            if float(self.reg.value('settings_version', type=QString)) < 1.6:
                self.cleanReg()
                self.setAllDefaults()
                self.reg.sync()
                self.values = self.loadSettings()
            else:
                self.values = self.loadSettings()
                self.values['create_nn_images'] = False
        else:
            self.cleanReg()
            self.setAllDefaults()
            self.reg.sync()
            self.values = self.loadSettings()
    
    def __getitem__(self, key):
        if key in self.values:
            return self.values[key]
        else:
            raise KeyError("Key "+unicode(key)+" not found in settings.")
            
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

    def loadSettings(self):
        """Load all settings to a dict"""
        set = {'first_run': self.reg.value('first_run', True, type=bool),
               'screenshot_dir': self.reg.value('screenshot_dir', type=QString),
               'export_dir': self.reg.value('export_dir', type=QString),
               'horizontal_exp': self.reg.value('horizontal_exp', type=bool),
               'gray_preview': self.reg.value('gray_preview', False, type=bool),
               'last_export_format': self.reg.value('last_export_format', type=QString),
               'log_dir': self.reg.value('log_dir', type=QString),
               'auto_fill': self.reg.value('auto_fill', type=bool),
               'remove_dupli': self.reg.value('remove_dupli', type=bool),
               'userID': self.reg.value('userID', type=QString),
               'ui_language': self.reg.value('ui_language', type=QString),
               'ocr_language': self.reg.value('ocr_language', type=QString),
               'delete_files': self.reg.value('delete_files', type=bool),
               'translate_results': self.reg.value('translate_results', type=bool),
               'pause_at_end': self.reg.value('pause_at_end', type=bool),
               'public_mode': self.reg.value('public_mode', type=bool),
               'native_dialog': self.reg.value('native_dialog', type=bool),
               'create_nn_images': self.reg.value('create_nn_images', type=bool),
               'zoom_factor': self.reg.value('zoom_factor', 1.0, type=float),
               'info_accepted': self.reg.value('info_accepted', False, type=bool),
               'theme': self.reg.value('theme', 'default', type=QString),
               'input_size': self.reg.value('input_size', 30, type=int),
               'snippet_size': self.reg.value('snippet_size', 30, type=int),
               'label_color': self.reg.value('label_color', '#ffffff', type=QString),
               'input_color': self.reg.value('input_color', '#ffffff', type=QString),
               'button_color': self.reg.value('button_color', '#ffffff', type=QString),
               'button_border_color': self.reg.value('button_border_color', '#ffffff', type=QString),
               'border_color': self.reg.value('border_color', '#ffffff', type=QString),
               'background_color': self.reg.value('background_color', '#000000', type=QString),
               'color1': self.reg.value('color1', '#ffffff', type=QString),
               'color2': self.reg.value('color2', '#ffffff', type=QString),
               'color3': self.reg.value('color3', '#ffffff', type=QString),
               'color4': self.reg.value('color4', '#ffffff', type=QString),
               'color5': self.reg.value('color5', '#ffffff', type=QString),
               'contrast': self.reg.value('contrast', 85.0, type=float)}
        return set
        
    def setAllDefaults(self):
        """Set all settings to default values"""
        self.setDefaultAutoFill()
        self.setDefaultRemoveDupli()
        self.setDefaultCreateNNImg()
        self.setDefaultDelete()
        self.setDefaultTranslateResults()
        self.setDefaultPause()
        self.setDefaultPublicMode()
        self.setDefaultNativeDialog()
        self.setDefaultScreenshotDir()
        self.setDefaultLogDir()
        self.setDefaultExportDir()
        self.setDefaultLanguage()
        self.setUserID()
        self.setSettingsVersion()
        
    def setSettingsVersion(self):
        self.reg.setValue('settings_version', "1.6")
        
    def setUserID(self):
        self.reg.setValue('userID', "EO"+''.join(random.choice('0123456789abcdef') for i in range(8)))
        
    def setDefaultExportOptions(self):
        self.setValue('horizontal_exp', False)
        self.setValue('last_export_format', 'xlsx')
    
    def setDefaultAutoFill(self):
        self.reg.setValue('auto_fill', False)
        
    def setDefaultRemoveDupli(self):
        self.reg.setValue('remove_dupli', True)
    
    def setDefaultLanguage(self):
        self.reg.setValue('ui_language', "en")
        self.reg.setValue('ocr_language', "eng")
        
    def setDefaultCreateNNImg(self):
        self.reg.setValue('create_nn_images', False)
        
    def setDefaultDelete(self):
        self.reg.setValue('delete_files', False)
        
    def setDefaultTranslateResults(self):
        self.reg.setValue('translate_results', False)
    
    def setDefaultPause(self):
        self.reg.setValue('pause_at_end', True)
        
    def setDefaultPublicMode(self):
        self.reg.setValue('public_mode', True)
    
    def setDefaultNativeDialog(self):
        self.reg.setValue('native_dialog', False)
        
    def setDefaultScreenshotDir(self):
        if isdir(self.userprofile+ os.sep +"Pictures"+ os.sep +"Frontier Developments"+ os.sep +"Elite Dangerous"):
            dir = self.userprofile+ os.sep +"Pictures"+ os.sep +"Frontier Developments"+ os.sep +"Elite Dangerous"
        else:
            dir = self.app_path
        self.reg.setValue('screenshot_dir', dir)
        
    def setDefaultLogDir(self):
        if isdir(self.userprofile+ os.sep +"AppData"+ os.sep +"Local"+ os.sep +"Frontier_Developments"+ os.sep +"Products"+ os.sep +"FORC-FDEV-D-1002"+ os.sep +"Logs"):
            logdir = self.userprofile+ os.sep +"AppData"+ os.sep +"Local"+ os.sep +"Frontier_Developments"+ os.sep +"Products"+ os.sep +"FORC-FDEV-D-1002"+ os.sep +"Logs"
            self.reg.setValue('log_dir', logdir)
        else:
            self.reg.setValue('log_dir', self.app_path)
                
    def setDefaultExportDir(self):
        self.reg.setValue('export_dir', self.app_path)
    
    def getUserProfile(self):
        if 'USERPROFILE' in environ:
            return environ['USERPROFILE'].decode(sys.getfilesystemencoding())
        else:
            return u"."
    
    def getPathToSelf(self):
        """Return the path to EliteOCR.py or EliteOCR.exe"""
        if getattr(sys, 'frozen', False):
            application_path = dirname(sys.executable).decode(sys.getfilesystemencoding())
        elif __file__:
            application_path = dirname(__file__).decode(sys.getfilesystemencoding())
        else:
            application_path = u"."
        return application_path
        