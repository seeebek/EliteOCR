from PyQt4.QtGui import QDialog, QFileDialog
from PyQt4.QtCore import QSettings
from settingsUI import Ui_Settings
from settings import Settings

class SettingsDialog(QDialog, Ui_Settings):
    def __init__(self, settings):
        QDialog.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.screenshotdir = self.settings['screenshot_dir']
        self.exportdir = self.settings['export_dir']
        self.logdir = self.settings['log_dir']
        self.scr_dir.setText(self.screenshotdir)
        self.exp_dir.setText(self.exportdir)
        self.lg_dir.setText(self.logdir)
        self.auto_fill.setChecked(self.settings['auto_fill'])
        self.remove_dupli.setChecked(self.settings['remove_dupli'])
        self.create_nn_images.setChecked(self.settings['create_nn_images'])
        self.browse.clicked.connect(self.browseDir)
        self.exp_browse.clicked.connect(self.browseExportDir)
        self.lg_browse.clicked.connect(self.browseLogDir)
    
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
        self.settings.setValue('screenshot_dir', self.screenshotdir)
        self.settings.setValue('export_dir', self.exportdir)
        self.settings.setValue('log_dir', self.logdir)
        self.settings.setValue('auto_fill', self.auto_fill.isChecked())
        self.settings.setValue('remove_dupli', self.remove_dupli.isChecked())
        self.settings.setValue('create_nn_images', self.create_nn_images.isChecked())
        self.settings.sync()
        self.close()