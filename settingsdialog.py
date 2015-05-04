# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog, QFileDialog, QColorDialog, QColor, QApplication
from PyQt4.QtCore import QSettings
from settingsUI import Ui_Settings
from settings import Settings
import os
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
        self.gray_preview.setChecked(self.settings['gray_preview'])
        self.exp_browse.clicked.connect(self.browseExportDir)
        
        self.logdir = self.settings['log_dir']
        self.scr_dir.setText(self.screenshotdir)
        
        self.lg_dir.setText(self.logdir)
        self.translate_results.setChecked(self.settings['translate_results'])
        self.auto_fill.setChecked(self.settings['auto_fill'])
        self.remove_dupli.setChecked(self.settings['remove_dupli'])
        self.delete_files.setChecked(self.settings['delete_files'])
        self.pause_at_end.setChecked(self.settings['pause_at_end'])
        self.input_size.setValue(self.settings['input_size'])
        self.snippet_size.setValue(self.settings['snippet_size'])
        self.label_color.setText(self.settings['label_color'])
        self.input_color.setText(self.settings['input_color'])
        self.button_color.setText(self.settings['button_color'])
        self.button_border_color.setText(self.settings['button_border_color'])
        self.border_color.setText(self.settings['border_color'])
        self.background_color.setText(self.settings['background_color'])
        """
        buttons = [self.c1, self.c2, self.c3, self.c4, self.c5]
        for i in range(len(buttons)):
            buttons[i].setStyleSheet("background:"+unicode(self.settings['color'+unicode(i+1)]))
            #'color1': self.reg.value('color1', '#ffffff', type=QString),
            #color = '#%02x%02x%02x' % palette[i]
            #self.settings.setValue('color'+unicode(i+1), color)
            #buttons[i].setStyleSheet("background:"+unicode(color))
        """
        self.browse.clicked.connect(self.browseDir)
        self.lg_browse.clicked.connect(self.browseLogDir)
        
        self.label_color_button.clicked.connect(self.getLabelColor)
        self.label_color.textChanged.connect(self.getLabelColor)
        self.label_color_button.setStyleSheet("background:"+unicode(self.label_color.text()))
        
        self.input_color_button.clicked.connect(self.getInputColor)
        self.input_color.textChanged.connect(self.getInputColor)
        self.input_color_button.setStyleSheet("background:"+unicode(self.input_color.text()))
        
        self.border_color_button.clicked.connect(self.getBorderColor)
        self.border_color.textChanged.connect(self.getBorderColor)
        self.border_color_button.setStyleSheet("background:"+unicode(self.border_color.text()))
        
        self.button_color_button.clicked.connect(self.getButtonColor)
        self.button_color.textChanged.connect(self.getButtonColor)
        self.button_color_button.setStyleSheet("background:"+unicode(self.button_color.text()))
        
        self.button_border_color_button.clicked.connect(self.getButtonBorderColor)
        self.button_border_color.textChanged.connect(self.getButtonBorderColor)
        self.button_border_color_button.setStyleSheet("background:"+unicode(self.button_border_color.text()))
        
        self.background_color_button.clicked.connect(self.getBackgroundColor)
        self.background_color.textChanged.connect(self.getBackgroundColor)
        self.background_color_button.setStyleSheet("background:"+unicode(self.background_color.text()))
        
        self.b1.setStyleSheet("background:"+unicode(self.settings["color1"]))
        self.b2.setStyleSheet("background:"+unicode(self.settings["color2"]))
        self.b3.setStyleSheet("background:"+unicode(self.settings["color3"]))
        self.b4.setStyleSheet("background:"+unicode(self.settings["color4"]))
        self.b5.setStyleSheet("background:"+unicode(self.settings["color5"]))
        self.b1.clicked.connect(lambda: self.changeColor("color1"))
        self.b2.clicked.connect(lambda: self.changeColor("color2"))
        self.b3.clicked.connect(lambda: self.changeColor("color3"))
        self.b4.clicked.connect(lambda: self.changeColor("color4"))
        self.b5.clicked.connect(lambda: self.changeColor("color5"))
        
        self.fillUILang()
        self.fillOCRLang()
        
        if self.settings['theme'] == "dark":
            self.theme.setCurrentIndex(1)
    
    def changeColor(self, color):
        self.clicked_color.setText(self.settings[color])
    
    def getLabelColor(self):
        color = QColorDialog.getColor(QColor(self.label_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.label_color.setText(color.name())
            self.label_color_button.setStyleSheet("background:"+unicode(color.name()))
            
    def getInputColor(self):
        color = QColorDialog.getColor(QColor(self.input_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.input_color.setText(color.name())
            self.input_color_button.setStyleSheet("background:"+unicode(color.name()))
    
    def getBorderColor(self):
        color = QColorDialog.getColor(QColor(self.border_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.border_color.setText(color.name())
            self.border_color_button.setStyleSheet("background:"+unicode(color.name()))
            
    def getButtonColor(self):
        color = QColorDialog.getColor(QColor(self.button_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.button_color.setText(color.name())
            self.button_color_button.setStyleSheet("background:"+unicode(color.name()))
            
    def getButtonBorderColor(self):
        color = QColorDialog.getColor(QColor(self.button_border_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.button_border_color.setText(color.name())
            self.button_border_color_button.setStyleSheet("background:"+unicode(color.name()))
            
    def getBackgroundColor(self):
        color = QColorDialog.getColor(QColor(self.background_color.text()))
        if not color.isValid():
            return
        if not color is None:
            self.background_color.setText(color.name())
            self.background_color_button.setStyleSheet("background:"+unicode(color.name()))
    
    def fillUILang(self):
        #self.ui_language.addItem("en")
        #path = unicode(self.settings.app_path+"/translations/")#.encode('windows-1252')
        #if isdir(path):
        #    dir = listdir(path)
        #    options = []
        #    for file in dir:
        #        options.append(file[-5:-3])
        #    self.ui_language.addItems(options)
        index = self.ui_language.findText(self.settings['ui_language'])
        if index == -1:
            index = 0
        self.ui_language.setCurrentIndex(index)
        
    def fillOCRLang(self):
        #self.ocr_language.addItem("eng")
        #path = ""
        #if isdir(unicode(self.settings.app_path+ os.sep +".."+ os.sep +"tessdata"+ os.sep +"")):
        #    path = unicode(self.settings.app_path+ os.sep +".."+ os.sep +"tessdata"+ os.sep +"")
        #if isdir(unicode(self.settings.app_path+ os.sep +"tessdata"+ os.sep +"")):
        #    path = unicode(self.settings.app_path+ os.sep +"tessdata"+ os.sep +"")
        #if isdir(path):
        #    dir = listdir(path)
        #    dir.remove("big.traineddata")
        #    dir = [d[:3] for d in dir]
        #    self.ocr_language.addItems(dir)
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
        self.settings.setValue('gray_preview', self.gray_preview.isChecked())
        self.settings.setValue('native_dialog', self.native_dialog.isChecked())
        self.settings.setValue('log_dir', self.logdir)
        self.settings.setValue('translate_results', self.translate_results.isChecked())
        self.settings.setValue('auto_fill', self.auto_fill.isChecked())
        self.settings.setValue('remove_dupli', self.remove_dupli.isChecked())
        self.settings.setValue('delete_files', self.delete_files.isChecked())
        self.settings.setValue('pause_at_end', self.pause_at_end.isChecked())
        self.settings.setValue('ui_language', self.ui_language.currentText())
        self.settings.setValue('ocr_language', self.ocr_language.currentText())
        self.settings.setValue('theme', self.theme.currentText())
        self.settings.setValue('input_size', self.input_size.value())
        self.settings.setValue('snippet_size', self.snippet_size.value())
        self.settings.setValue('label_color', self.label_color.text())
        self.settings.setValue('input_color', self.input_color.text())
        self.settings.setValue('button_color', self.button_color.text())
        self.settings.setValue('button_border_color', self.button_border_color.text())
        self.settings.setValue('border_color', self.border_color.text())
        self.settings.setValue('background_color', self.background_color.text())
        self.settings.sync()
        self.close()