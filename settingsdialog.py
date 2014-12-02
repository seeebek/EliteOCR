from PyQt4.QtGui import QDialog, QFileDialog
from PyQt4.QtCore import QSettings
from settingsUI import Ui_Settings
from settings import loadSettings

class SettingsDialog(QDialog, Ui_Settings):
    def __init__(self, parent=None):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = loadSettings(None)
        self.screenshotdir = self.settings['screenshot_dir']
        self.exportdir = self.settings['export_dir']
        self.scr_dir.setText(self.screenshotdir)
        self.exp_dir.setText(self.exportdir)
        self.auto_fill.setChecked(self.settings['auto_fill'])
        self.remove_dupli.setChecked(self.settings['remove_dupli'])
        self.browse.clicked.connect(self.browseDir)
        self.exp_browse.clicked.connect(self.browseExportDir)
    
    def browseDir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Choose", self.screenshotdir)
        if new_dir != "":
            self.screenshotdir = new_dir
            self.scr_dir.setText(self.screenshotdir)
            
    def browseExportDir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Choose", self.exportdir)
        if new_dir != "":
            self.exportdir = new_dir
            self.exp_dir.setText(self.exportdir)
    
    def accept(self):
        new_settings = QSettings('seeebek', 'eliteOCR')
        new_settings.setValue('screenshot_dir', self.screenshotdir)
        new_settings.setValue('export_dir', self.exportdir)
        new_settings.setValue('auto_fill', self.auto_fill.isChecked())
        new_settings.setValue('remove_dupli', self.remove_dupli.isChecked())
        del new_settings
        self.close()