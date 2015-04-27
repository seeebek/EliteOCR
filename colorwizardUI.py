# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'colorwizardUI.ui'
#
# Created: Mon Apr 27 13:40:41 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ColorCalibrationWizard(object):
    def setupUi(self, ColorCalibrationWizard):
        ColorCalibrationWizard.setObjectName(_fromUtf8("ColorCalibrationWizard"))
        ColorCalibrationWizard.resize(539, 520)
        ColorCalibrationWizard.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.wizardPage1 = CustomQWizardPage()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.wizardPage1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_20 = QtGui.QLabel(self.wizardPage1)
        self.label_20.setWordWrap(True)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.verticalLayout.addWidget(self.label_20)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.add_screenshots = QtGui.QPushButton(self.wizardPage1)
        self.add_screenshots.setObjectName(_fromUtf8("add_screenshots"))
        self.horizontalLayout_7.addWidget(self.add_screenshots)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.label_8 = QtGui.QLabel(self.wizardPage1)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_9.addWidget(self.label_8)
        self.ocr_language = QtGui.QComboBox(self.wizardPage1)
        self.ocr_language.setObjectName(_fromUtf8("ocr_language"))
        self.ocr_language.addItem(_fromUtf8(""))
        self.ocr_language.addItem(_fromUtf8(""))
        self.ocr_language.addItem(_fromUtf8(""))
        self.horizontalLayout_9.addWidget(self.ocr_language)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.screenshot_list = QtGui.QListWidget(self.wizardPage1)
        self.screenshot_list.setObjectName(_fromUtf8("screenshot_list"))
        self.verticalLayout.addWidget(self.screenshot_list)
        ColorCalibrationWizard.addPage(self.wizardPage1)
        self.wizardPage2 = CustomQWizardPage()
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.wizardPage2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_21 = QtGui.QLabel(self.wizardPage2)
        self.label_21.setWordWrap(True)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.verticalLayout_2.addWidget(self.label_21)
        self.analyzing_progress = QtGui.QProgressBar(self.wizardPage2)
        self.analyzing_progress.setMaximum(0)
        self.analyzing_progress.setProperty("value", 0)
        self.analyzing_progress.setTextVisible(False)
        self.analyzing_progress.setObjectName(_fromUtf8("analyzing_progress"))
        self.verticalLayout_2.addWidget(self.analyzing_progress)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.label_13 = QtGui.QLabel(self.wizardPage2)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_11.addWidget(self.label_13)
        self.time_left = QtGui.QLabel(self.wizardPage2)
        self.time_left.setObjectName(_fromUtf8("time_left"))
        self.horizontalLayout_11.addWidget(self.time_left)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.scr_result = QtGui.QPlainTextEdit(self.wizardPage2)
        self.scr_result.setReadOnly(True)
        self.scr_result.setObjectName(_fromUtf8("scr_result"))
        self.verticalLayout_2.addWidget(self.scr_result)
        ColorCalibrationWizard.addPage(self.wizardPage2)

        self.retranslateUi(ColorCalibrationWizard)
        QtCore.QMetaObject.connectSlotsByName(ColorCalibrationWizard)

    def retranslateUi(self, ColorCalibrationWizard):
        ColorCalibrationWizard.setWindowTitle(_translate("ColorCalibrationWizard", "Color Calibration Wizard", None))
        self.wizardPage1.setTitle(_translate("ColorCalibrationWizard", "Color Calibration Wizard", None))
        self.wizardPage1.setSubTitle(_translate("ColorCalibrationWizard", "Screenshot selection", None))
        self.label_20.setText(_translate("ColorCalibrationWizard", "EliteOCR will evaluate your screenshots for their compatibility with OCR. It will measure if the text size is sufficient for the process and tell you what you can do in case it isn\'t.\n"
"\n"
"Always run this wizard after changing resolution, hud color or other game settings which change the appearance of the screenshots. Even the smallest change can reduce OCR accuracy.\n"
"\n"
"First select between 3 and 5 screenshots.", None))
        self.add_screenshots.setText(_translate("ColorCalibrationWizard", "Add Screenshots", None))
        self.label_8.setText(_translate("ColorCalibrationWizard", "Screenshot language:", None))
        self.ocr_language.setItemText(0, _translate("ColorCalibrationWizard", "English", None))
        self.ocr_language.setItemText(1, _translate("ColorCalibrationWizard", "German", None))
        self.ocr_language.setItemText(2, _translate("ColorCalibrationWizard", "French", None))
        self.wizardPage2.setTitle(_translate("ColorCalibrationWizard", "Color Calibration Wizard", None))
        self.wizardPage2.setSubTitle(_translate("ColorCalibrationWizard", "Screenshot evaluation", None))
        self.label_21.setText(_translate("ColorCalibrationWizard", "Now EliteOCR will calibrate itself to your HUD color. It is necessary in order to maximize the OCR accuracy. When finished it will inform you about quality of your screenshots and the accuracy you can expect. \n"
"Please wait. This process can take some time.", None))
        self.label_13.setText(_translate("ColorCalibrationWizard", "Time left:", None))
        self.time_left.setText(_translate("ColorCalibrationWizard", "calculating", None))

from customqwizardpage import CustomQWizardPage
