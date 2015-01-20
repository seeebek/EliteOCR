from PyQt4.QtGui import QDialog, QFileDialog
from PyQt4.QtCore import QSettings
from settingsUI import Ui_Settings
from settings import Settings
from os.path import isdir
from os import listdir

class SettingsDialog(QDialog, Ui_Settings):
    def __init__(self, settings):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.screenshotdir = self.settings['screenshot_dir']
        
        self.exportdir = self.settings['export_dir']
        self.exp_dir.setText(self.exportdir)
        self.horizontal_exp.setChecked(self.settings['horizontal_exp'])
        self.native_dialog.setChecked(self.settings['native_dialog'])
        self.updates_check.setChecked(self.settings['updates_check'])
        self.exp_browse.clicked.connect(self.browseExportDir)
        
        self.logdir = self.settings['log_dir']
        self.scr_dir.setText(self.screenshotdir)
        
        self.lg_dir.setText(self.logdir)
        self.translate_results.setChecked(self.settings['translate_results'])
        self.auto_fill.setChecked(self.settings['auto_fill'])
        self.remove_dupli.setChecked(self.settings['remove_dupli'])
        self.delete_files.setChecked(self.settings['delete_files'])
        self.pause_at_end.setChecked(self.settings['pause_at_end'])
        self.create_nn_images.setChecked(self.settings['create_nn_images'])
        self.browse.clicked.connect(self.browseDir)
        
        self.lg_browse.clicked.connect(self.browseLogDir)
        
        self.fillUILang()
        self.fillOCRLang()
    
    def fillUILang(self):
        self.ui_language.addItem("en")
        path = unicode(self.settings.app_path.decode('windows-1252')+"/translations/")#.encode('windows-1252')
        if isdir(path):
            dir = listdir(path)
            options = []
            for file in dir:
                options.append(file[-5:-3])
            self.ui_language.addItems(options)
        index = self.ui_language.findText(self.settings['ui_language'])
        if index == -1:
            index = 0
        self.ui_language.setCurrentIndex(index)
        
    def fillOCRLang(self):
        self.ocr_language.addItem("eng")
        path = ""
        if isdir(unicode(self.settings.app_path.decode('windows-1252')+"\\..\\tessdata\\")):
            path = unicode(self.settings.app_path.decode('windows-1252')+"\\..\\tessdata\\")
        if isdir(unicode(self.settings.app_path.decode('windows-1252')+"\\tessdata\\")):
            path = unicode(self.settings.app_path.decode('windows-1252')+"\\tessdata\\")
        if isdir(path):
            dir = listdir(path)
            dir.remove("big.traineddata")
            dir = [d[:3] for d in dir]
            self.ocr_language.addItems(dir)
        index = self.ocr_language.findText(self.settings['ocr_language'])
        if index == -1:
            index = 0
        self.ocr_language.setCurrentIndex(index)
            
    def browseDir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Choose", self.screenshotdir)
        if new_dir != "":
            self.screenshotdir = new_dir
            self.scr_dir.setText(self.screenshotdir)

    def browseLogDir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Choose", self.logdir)
        if new_dir != "":
            self.logdir = new_dir
            self.lg_dir.setText(self.logdir)
    
    def browseExportDir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Choose", self.exportdir)
        if new_dir != "":
            self.exportdir = new_dir
            self.exp_dir.setText(self.exportdir)
    
    def accept(self):
        self.screenshotdir = self.scr_dir.text()
        self.exportdir = self.exp_dir.text()
        self.logdir = self.lg_dir.text()
        self.settings.setValue('screenshot_dir', self.screenshotdir)
        self.settings.setValue('export_dir', self.exportdir)
        self.settings.setValue('horizontal_exp', self.horizontal_exp.isChecked())
        self.settings.setValue('native_dialog', self.native_dialog.isChecked())
        self.settings.setValue('log_dir', self.logdir)
        self.settings.setValue('translate_results', self.translate_results.isChecked())
        self.settings.setValue('auto_fill', self.auto_fill.isChecked())
        self.settings.setValue('remove_dupli', self.remove_dupli.isChecked())
        self.settings.setValue('delete_files', self.delete_files.isChecked())
        self.settings.setValue('pause_at_end', self.pause_at_end.isChecked())
        self.settings.setValue('updates_check', self.updates_check.isChecked())
        self.settings.setValue('ui_language', self.ui_language.currentText())
        self.settings.setValue('ocr_language', self.ocr_language.currentText())
        self.settings.setValue('create_nn_images', self.create_nn_images.isChecked())
        self.settings.sync()
        self.close()