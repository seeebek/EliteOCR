# -*- coding: utf-8 -*-
import sys
import random
import os
from os import environ, listdir
from os.path import isfile, isdir, basename, dirname, join, normpath
from sys import platform
from PyQt4.QtCore import QSettings, QString, QT_VERSION
from PyQt4.QtGui import QMessageBox, QFileDialog, QDesktopServices

if platform == 'win32':
    import ctypes.wintypes
    CSIDL_LOCAL_APPDATA = 0x001c
    CSIDL_PROGRAM_FILESX86 = 0x002a
    SHGFP_TYPE_CURRENT = 0 	# Current, not default, values
elif platform == 'darwin':
    from Foundation import NSHomeDirectory, NSSearchPathForDirectoriesInDomains, NSDocumentDirectory, NSApplicationSupportDirectory, NSPicturesDirectory, NSUserDomainMask

appconf = (platform=="darwin" and "AppConfigLocal.xml" or "AppConfig.xml")


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
               'horizontal_exp': self.reg.value('horizontal_exp', False, type=bool),
               'gray_preview': self.reg.value('gray_preview', False, type=bool),
               'last_export_format': self.reg.value('last_export_format', "csv", type=QString),
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
               'label_color': self.reg.value('label_color', '#ff7f0f', type=QString),
               'input_color': self.reg.value('input_color', '#ffffff', type=QString),
               'button_color': self.reg.value('button_color', '#ff7f0f', type=QString),
               'button_border_color': self.reg.value('button_border_color', '#af4f0f', type=QString),
               'border_color': self.reg.value('border_color', '#af4f0f', type=QString),
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
        # Native save dialogs bugged on 4.8.6 on OSX - https://codereview.qt-project.org/#/c/94980/
        self.reg.setValue('native_dialog', platform=="darwin" and QT_VERSION>=0x40807)
        
    def setDefaultScreenshotDir(self):
        path = join(unicode(QDesktopServices.storageLocation(QDesktopServices.PicturesLocation)), "Frontier Developments", "Elite Dangerous")
        self.reg.setValue('screenshot_dir', isdir(path) and path or self.userprofile)
        
    def setDefaultLogDir(self):
        self.reg.setValue('log_dir', self.getCustomLogDir() or self.getStandardLogDir() or self.userprofile)

    def getStandardLogDir(self):
        if platform == 'win32':
            # https://support.elitedangerous.com/kb/faq.php?id=108
            programs = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetSpecialFolderPathW(0, programs, CSIDL_PROGRAM_FILESX86, 0)
            applocal = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetSpecialFolderPathW(0, applocal, CSIDL_LOCAL_APPDATA, 0)
            for base in [join(programs.value, "Steam", "steamapps", "common", "Elite Dangerous", "Products"),
                         join(programs.value, "Frontier", "Products"),
                         join(applocal.value, "Frontier_Developments", "Products")]:
                if isdir(base):
                    for d in listdir(base):
                        if d.startswith("FORC-FDEV-D-1") and isdir(join(base, d, "Logs")):
                            return join(base, d, "Logs")

        elif platform == 'darwin':
            # TODO: Steam on Mac
            suffix = join("Frontier Developments", "Elite Dangerous", "Logs")
            paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)
            if len(paths) and isdir(join(paths[0], suffix)):
                return join(paths[0], suffix)

        return None	# not found in standard places

    def getCustomLogDir(self):
        if platform == 'win32':
            from _winreg import OpenKey, EnumKey, QueryValueEx, HKEY_LOCAL_MACHINE
            aKey = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
            try:
                i = 0
                while True:
                    asubkey = OpenKey(aKey, EnumKey(aKey,i))
                    try:
                        if QueryValueEx(asubkey, "Publisher")[0] == "Frontier Developments":
                            custpath = join(QueryValueEx(asubkey, "InstallLocation")[0], "Products")
                            if isdir(custpath):
                                for d in listdir(custpath):
                                    if d.startswith("FORC-FDEV-D-1") and isdir(join(custpath, d, "Logs")):
                                        asubkey.Close()
                                        aKey.Close()
                                        return join(custpath, d, "Logs")
                    except:
                        pass
                    asubkey.Close()
                    i += 1
            except:
                aKey.Close()
        return None

    def setDefaultExportDir(self):
        path = unicode(QDesktopServices.storageLocation(QDesktopServices.DocumentsLocation))
        self.reg.setValue('export_dir', isdir(path) and path or self.userprofile)

    def getUserProfile(self):
        path = unicode(QDesktopServices.storageLocation(QDesktopServices.HomeLocation))
        return isdir(path) and path or u"."

    def getPathToSelf(self):
        """Return the path to our supporting files"""
        if getattr(sys, 'frozen', False):
            if platform=='darwin':
                application_path = normpath(join(dirname(sys.executable), os.pardir, 'Resources'))
            else:
                application_path = dirname(sys.executable).decode(sys.getfilesystemencoding())
        elif __file__:
            application_path = dirname(__file__).decode(sys.getfilesystemencoding())
        else:
            application_path = u"."
        return application_path


# AppConfig helpers

def isValidLogPath(logpath):
    return isfile(join(logpath, os.pardir, (platform=="darwin" and "AppNetCfg.xml" or "AppConfig.xml")))

def hasAppConf(logpath):
    return isfile(join(logpath, os.pardir, appconf))

def hasVerboseLogging(logpath):
    path = join(logpath, os.pardir, appconf)
    if isfile(path):
        file = open(path, 'rt')
        file_content = file.read()
        file.close()
        start = file_content.find("<Network")
        end = file_content.find("</Network>")
        return file_content.lower().find('verboselogging="1"', start, end) >= 0
    return False

def enableVerboseLogging(logpath):
    path = join(logpath, os.pardir, appconf)
    if not isValidLogPath(logpath) or hasVerboseLogging(logpath):
        return False
    elif not hasAppConf(logpath):
        if platform=="darwin":
            # Create new file
            f = open(path, 'wt')
            f.write('<AppConfig>\n\t<Network\n\t\tVerboseLogging="1"\n\t>\n\t</Network>\n</AppConfig>\n')
            f.close()
            return True
        else:
            return False	# Can't amend file that doesn't exist

    f = open(path, 'rt')
    file_content = f.read()
    f.close()

    f = open(path[:-4] + "_backup.xml", 'wt')
    f.write(file_content)
    f.close()

    f = open(path, 'wt')
    start = file_content.find("<Network")
    if start >= 0:
        f.write(file_content[:start+8] + '\n\t\tVerboseLogging="1"' + file_content[start+8:])
    else:
        start = file_content.find("</AppConfig>")
        if start >= 0:
            f.write(file_content[:start] + '\t<Network\n\t\tVerboseLogging="1"\n\t>\n\t</Network>\n' + file_content[start:])
        else:
            f.write(file_content)	# eh ?
    f.close()

    return True
