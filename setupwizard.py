# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWizard, QFileDialog, QListWidgetItem
from PyQt4.QtCore import QObject, SIGNAL
from setupwizardUI import Ui_SetupWizard
from platform import system
import os
from os import environ, listdir
from os.path import isdir, isfile, join
from sys import platform
from settings import appconf, isValidLogPath, hasAppConf, hasVerboseLogging, enableVerboseLogging
import codecs
from engine import OCRAreasFinder

#from mmcq import get_palette

class SetupWizard(QWizard, Ui_SetupWizard):
    def __init__(self, settings):
        QWizard.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.path_input.textChanged.connect(self.checkLogValid)
        self.verbose_button.clicked.connect(self.enableVerbose)
        self.browse_log_path.clicked.connect(self.browseLogPath)
        self.screenshot_dir_browse.clicked.connect(self.browseScreenshotPath)
        self.export_dir_browse.clicked.connect(self.browseExportPath)
        
        self.wizardPage1.fullfilled = True
        self.wizardPage2.pageCreated.connect(self.logWork)
        self.wizardPage2.fullfilled = True
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
        text += "%s found:\n" % appconf
        text += unicode(self.appconf_found.text())+"\n\n"
        text += "Verbose logging enabled in %s:\n" % appconf
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
        self.appconf_found.setText(hasAppConf(unicode(self.path_input.text())) and "Yes" or "No")
        if isValidLogPath(unicode(self.path_input.text())):
            if hasVerboseLogging(unicode(self.path_input.text())):
                self.verbose_enabled.setText("Yes")
                self.verbose_button.setEnabled(False)
            else:
                self.verbose_enabled.setText("No")
                self.verbose_button.setEnabled(True)
        else:
            self.verbose_enabled.setText("No")
            self.verbose_button.setEnabled(False)

        # Give advice on Mac users' Keyboard preferences
        if platform=='darwin':
            self.appconf.setText(appconf)
            self.advice.setStyleSheet("font-size: 12pt;")

            # Adjust advice depending on whether users have to press F10 or fn-F10
            try:
                from Foundation import NSUserDefaults, NSGlobalDomain
                screenshotkey = NSUserDefaults.standardUserDefaults().persistentDomainForName_(NSGlobalDomain)["com.apple.keyboard.fnState"] and 'F10' or 'fn-F10'
            except:
                screenshotkey = 'fn-F10'	# Default setting, assuming an Apple keyboard

            # Advise if F10 is bound to a keyboard shortcut
            shortcutissue = ''
            try:
                # http://krypted.com/mac-os-x/defaults-symbolichotkeys/
                for k, v in NSUserDefaults.standardUserDefaults().persistentDomainForName_("com.apple.symbolichotkeys")["AppleSymbolicHotKeys"].iteritems():
                    if v['enabled'] and v['value']['parameters'][1] == 109 and v['value']['parameters'][2] == 0:
                        if k == '33':	# F10 was the default binding for "App Exposé" under OSX 10.6
                            shortcutissue = '<p>The F10 key is currently assigned to the shortcut &ldquo;Application&nbsp;windows&rdquo;. You will need to remove this assignment in &#xF8FF; &rarr; System&nbsp;Preferences &rarr; <a href="file:/System/Library/PreferencePanes/Expose.prefPane/">Mission&nbsp;Control</a>.</p>'
                        else:
                            shortcutissue = '<p>The F10 key is currently assigned to a keyboard shortcut. You will need to disable or remove this assignment in &#xF8FF; &rarr; System&nbsp;Preferences &rarr; <a href="file:/System/Library/PreferencePanes/Keyboard.prefPane/">Keyboard</a> &rarr; Shortcuts.</p>'
                        break
            except:
                pass
        else:
            screenshotkey = 'F10'
            shortcutissue = ''
        self.advice.setText(self.advice.text().replace('%1', screenshotkey).replace('%2', shortcutissue))

    def browseLogPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", self.path_input.text())
        if dir:
            self.path_input.setText(dir)
    
    def browseScreenshotPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", self.screenshot_dir.text())
        if dir:
            self.screenshot_dir.setText(dir)
            
    def browseExportPath(self):
        dir = QFileDialog.getExistingDirectory(self, "Choose directory", self.export_dir.text())
        if dir:
            self.export_dir.setText(dir)
    
    def checkLogValid(self):
        logpath = unicode(self.path_input.text())
        self.standard_path.setText(logpath==self.settings.getStandardLogDir() and "Yes" or "No")
        self.custom_path.setText(logpath==self.settings.getCustomLogDir() and "Yes" or "No")
        self.valid_path.setText(isValidLogPath(logpath) and "Yes" or "No")

    def logWork(self):
        self.operating_system.setText(platform=="darwin" and "Mac OS" or system())
        # re-initialize to default settings
        self.path_input.setText(self.settings.getCustomLogDir() or self.settings.getStandardLogDir() or self.settings.userprofile)

    def enableVerbose(self):
        enableVerboseLogging(unicode(self.path_input.text()))
        self.AppConfigWork()	# update displayed values

