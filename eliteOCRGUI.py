# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eliteOCRGUI.ui'
#
# Created: Sun Dec 07 12:39:16 2014
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1131, 788)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/icon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 200))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_9.setMargin(0)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_7 = QtGui.QLabel(self.widget)
        self.label_7.setMinimumSize(QtCore.QSize(150, 0))
        self.label_7.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_4.addWidget(self.label_7)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.add_button = QtGui.QToolButton(self.widget)
        self.add_button.setMaximumSize(QtCore.QSize(16777215, 20))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_button.setIcon(icon1)
        self.add_button.setObjectName(_fromUtf8("add_button"))
        self.horizontalLayout_7.addWidget(self.add_button)
        self.remove_button = QtGui.QToolButton(self.widget)
        self.remove_button.setEnabled(False)
        self.remove_button.setMaximumSize(QtCore.QSize(16777215, 20))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/ico/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.remove_button.setIcon(icon2)
        self.remove_button.setObjectName(_fromUtf8("remove_button"))
        self.horizontalLayout_7.addWidget(self.remove_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.file_list = QtGui.QListWidget(self.widget)
        self.file_list.setMinimumSize(QtCore.QSize(150, 0))
        self.file_list.setMaximumSize(QtCore.QSize(16777215, 200))
        self.file_list.setObjectName(_fromUtf8("file_list"))
        self.verticalLayout_4.addWidget(self.file_list)
        self.horizontalLayout_9.addLayout(self.verticalLayout_4)
        self.line_3 = QtGui.QFrame(self.widget)
        self.line_3.setFrameShape(QtGui.QFrame.VLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.horizontalLayout_9.addWidget(self.line_3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_8 = QtGui.QLabel(self.widget)
        self.label_8.setMaximumSize(QtCore.QSize(30, 25))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout.addWidget(self.label_8)
        self.file_label = QtGui.QLabel(self.widget)
        self.file_label.setMaximumSize(QtCore.QSize(16777215, 25))
        self.file_label.setObjectName(_fromUtf8("file_label"))
        self.horizontalLayout.addWidget(self.file_label)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.ocr_button = QtGui.QPushButton(self.widget)
        self.ocr_button.setEnabled(False)
        self.ocr_button.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ocr_button.setObjectName(_fromUtf8("ocr_button"))
        self.horizontalLayout_8.addWidget(self.ocr_button)
        self.ocr_all = QtGui.QPushButton(self.widget)
        self.ocr_all.setEnabled(False)
        self.ocr_all.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ocr_all.setObjectName(_fromUtf8("ocr_all"))
        self.horizontalLayout_8.addWidget(self.ocr_all)
        spacerItem1 = QtGui.QSpacerItem(40, 5, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_2.addWidget(self.line)
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setMinimumSize(QtCore.QSize(0, 0))
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_2.addWidget(self.label_5)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.station_name_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(6)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.station_name_img.sizePolicy().hasHeightForWidth())
        self.station_name_img.setSizePolicy(sizePolicy)
        self.station_name_img.setMinimumSize(QtCore.QSize(0, 20))
        self.station_name_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.station_name_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.station_name_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.station_name_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.station_name_img.setObjectName(_fromUtf8("station_name_img"))
        self.horizontalLayout_5.addWidget(self.station_name_img)
        self.station_name = QtGui.QComboBox(self.widget)
        self.station_name.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.station_name.sizePolicy().hasHeightForWidth())
        self.station_name.setSizePolicy(sizePolicy)
        self.station_name.setMinimumSize(QtCore.QSize(0, 20))
        self.station_name.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.station_name.setAcceptDrops(False)
        self.station_name.setStyleSheet(_fromUtf8(""))
        self.station_name.setEditable(True)
        self.station_name.setIconSize(QtCore.QSize(16, 16))
        self.station_name.setFrame(True)
        self.station_name.setObjectName(_fromUtf8("station_name"))
        self.horizontalLayout_5.addWidget(self.station_name)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.demand_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.demand_img.sizePolicy().hasHeightForWidth())
        self.demand_img.setSizePolicy(sizePolicy)
        self.demand_img.setMinimumSize(QtCore.QSize(0, 20))
        self.demand_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.demand_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.demand_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.demand_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.demand_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.demand_img.setObjectName(_fromUtf8("demand_img"))
        self.gridLayout.addWidget(self.demand_img, 1, 3, 1, 1)
        self.supply_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.supply_img.sizePolicy().hasHeightForWidth())
        self.supply_img.setSizePolicy(sizePolicy)
        self.supply_img.setMinimumSize(QtCore.QSize(0, 20))
        self.supply_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.supply_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.supply_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.supply_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.supply_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.supply_img.setObjectName(_fromUtf8("supply_img"))
        self.gridLayout.addWidget(self.supply_img, 1, 5, 1, 1)
        self.supply_text_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.supply_text_img.sizePolicy().hasHeightForWidth())
        self.supply_text_img.setSizePolicy(sizePolicy)
        self.supply_text_img.setMinimumSize(QtCore.QSize(0, 20))
        self.supply_text_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.supply_text_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.supply_text_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.supply_text_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.supply_text_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.supply_text_img.setObjectName(_fromUtf8("supply_text_img"))
        self.gridLayout.addWidget(self.supply_text_img, 1, 6, 1, 1)
        self.demand_text_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.demand_text_img.sizePolicy().hasHeightForWidth())
        self.demand_text_img.setSizePolicy(sizePolicy)
        self.demand_text_img.setMinimumSize(QtCore.QSize(0, 20))
        self.demand_text_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.demand_text_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.demand_text_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.demand_text_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.demand_text_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.demand_text_img.setObjectName(_fromUtf8("demand_text_img"))
        self.gridLayout.addWidget(self.demand_text_img, 1, 4, 1, 1)
        self.buy_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buy_img.sizePolicy().hasHeightForWidth())
        self.buy_img.setSizePolicy(sizePolicy)
        self.buy_img.setMinimumSize(QtCore.QSize(0, 20))
        self.buy_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.buy_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.buy_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.buy_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.buy_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.buy_img.setObjectName(_fromUtf8("buy_img"))
        self.gridLayout.addWidget(self.buy_img, 1, 2, 1, 1)
        self.name_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_img.sizePolicy().hasHeightForWidth())
        self.name_img.setSizePolicy(sizePolicy)
        self.name_img.setMinimumSize(QtCore.QSize(0, 20))
        self.name_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.name_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.name_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.name_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.name_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.name_img.setObjectName(_fromUtf8("name_img"))
        self.gridLayout.addWidget(self.name_img, 1, 0, 1, 1)
        self.sell_img = QtGui.QGraphicsView(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sell_img.sizePolicy().hasHeightForWidth())
        self.sell_img.setSizePolicy(sizePolicy)
        self.sell_img.setMinimumSize(QtCore.QSize(0, 20))
        self.sell_img.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.sell_img.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sell_img.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sell_img.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.sell_img.setRenderHints(QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.sell_img.setObjectName(_fromUtf8("sell_img"))
        self.gridLayout.addWidget(self.sell_img, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.label_4 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 3, 1, 1)
        self.label_6 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 0, 5, 1, 1)
        self.name = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(43)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy)
        self.name.setMinimumSize(QtCore.QSize(0, 20))
        self.name.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.name.setStyleSheet(_fromUtf8(""))
        self.name.setEditable(True)
        self.name.setObjectName(_fromUtf8("name"))
        self.gridLayout.addWidget(self.name, 3, 0, 1, 1)
        self.sell = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(12)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sell.sizePolicy().hasHeightForWidth())
        self.sell.setSizePolicy(sizePolicy)
        self.sell.setMinimumSize(QtCore.QSize(0, 20))
        self.sell.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.sell.setStyleSheet(_fromUtf8(""))
        self.sell.setEditable(True)
        self.sell.setObjectName(_fromUtf8("sell"))
        self.gridLayout.addWidget(self.sell, 3, 1, 1, 1)
        self.buy = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(12)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buy.sizePolicy().hasHeightForWidth())
        self.buy.setSizePolicy(sizePolicy)
        self.buy.setMinimumSize(QtCore.QSize(0, 20))
        self.buy.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.buy.setStyleSheet(_fromUtf8(""))
        self.buy.setEditable(True)
        self.buy.setObjectName(_fromUtf8("buy"))
        self.gridLayout.addWidget(self.buy, 3, 2, 1, 1)
        self.demand_num = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(14)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.demand_num.sizePolicy().hasHeightForWidth())
        self.demand_num.setSizePolicy(sizePolicy)
        self.demand_num.setMinimumSize(QtCore.QSize(0, 20))
        self.demand_num.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.demand_num.setStyleSheet(_fromUtf8(""))
        self.demand_num.setEditable(True)
        self.demand_num.setObjectName(_fromUtf8("demand_num"))
        self.gridLayout.addWidget(self.demand_num, 3, 3, 1, 1)
        self.demand = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.demand.sizePolicy().hasHeightForWidth())
        self.demand.setSizePolicy(sizePolicy)
        self.demand.setMinimumSize(QtCore.QSize(0, 20))
        self.demand.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.demand.setStyleSheet(_fromUtf8(""))
        self.demand.setEditable(True)
        self.demand.setObjectName(_fromUtf8("demand"))
        self.gridLayout.addWidget(self.demand, 3, 4, 1, 1)
        self.supply_num = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(14)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.supply_num.sizePolicy().hasHeightForWidth())
        self.supply_num.setSizePolicy(sizePolicy)
        self.supply_num.setMinimumSize(QtCore.QSize(0, 20))
        self.supply_num.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.supply_num.setStyleSheet(_fromUtf8(""))
        self.supply_num.setEditable(True)
        self.supply_num.setObjectName(_fromUtf8("supply_num"))
        self.gridLayout.addWidget(self.supply_num, 3, 5, 1, 1)
        self.supply = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.supply.sizePolicy().hasHeightForWidth())
        self.supply.setSizePolicy(sizePolicy)
        self.supply.setMinimumSize(QtCore.QSize(0, 20))
        self.supply.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.supply.setStyleSheet(_fromUtf8(""))
        self.supply.setEditable(True)
        self.supply.setObjectName(_fromUtf8("supply"))
        self.gridLayout.addWidget(self.supply, 3, 6, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.skip_button = QtGui.QPushButton(self.widget)
        self.skip_button.setEnabled(False)
        self.skip_button.setObjectName(_fromUtf8("skip_button"))
        self.verticalLayout_3.addWidget(self.skip_button)
        self.save_button = QtGui.QPushButton(self.widget)
        self.save_button.setEnabled(False)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.verticalLayout_3.addWidget(self.save_button)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_9.addLayout(self.verticalLayout_2)
        self.verticalLayout_5.addWidget(self.widget)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setEnabled(True)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout_5.addWidget(self.line_2)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setFrameShape(QtGui.QFrame.NoFrame)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.preview = QtGui.QGraphicsView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(88)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview.sizePolicy().hasHeightForWidth())
        self.preview.setSizePolicy(sizePolicy)
        self.preview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview.setObjectName(_fromUtf8("preview"))
        self.result_table = CustomQTableWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(80)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.result_table.sizePolicy().hasHeightForWidth())
        self.result_table.setSizePolicy(sizePolicy)
        self.result_table.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.result_table.setObjectName(_fromUtf8("result_table"))
        self.result_table.setColumnCount(0)
        self.result_table.setRowCount(0)
        self.horizontalLayout_4.addWidget(self.splitter)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.clear_table = QtGui.QPushButton(self.centralwidget)
        self.clear_table.setEnabled(False)
        self.clear_table.setObjectName(_fromUtf8("clear_table"))
        self.horizontalLayout_2.addWidget(self.clear_table)
        self.export_button = QtGui.QPushButton(self.centralwidget)
        self.export_button.setEnabled(False)
        self.export_button.setMaximumSize(QtCore.QSize(16777215, 25))
        self.export_button.setObjectName(_fromUtf8("export_button"))
        self.horizontalLayout_2.addWidget(self.export_button)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1131, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        MainWindow.setMenuBar(self.menubar)
        self.actionHow_to_use = QtGui.QAction(MainWindow)
        self.actionHow_to_use.setObjectName(_fromUtf8("actionHow_to_use"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionCalibrate = QtGui.QAction(MainWindow)
        self.actionCalibrate.setObjectName(_fromUtf8("actionCalibrate"))
        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setObjectName(_fromUtf8("actionPreferences"))
        self.actionTest = QtGui.QAction(MainWindow)
        self.actionTest.setObjectName(_fromUtf8("actionTest"))
        self.menuHelp.addAction(self.actionHow_to_use)
        self.menuHelp.addAction(self.actionAbout)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionExit)
        self.menuSettings.addAction(self.actionCalibrate)
        self.menuSettings.addAction(self.actionPreferences)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "EliteOCR", None))
        self.label_7.setText(_translate("MainWindow", "Files", None))
        self.add_button.setText(_translate("MainWindow", "...", None))
        self.remove_button.setText(_translate("MainWindow", "...", None))
        self.label_8.setText(_translate("MainWindow", "File: ", None))
        self.file_label.setText(_translate("MainWindow", "-", None))
        self.ocr_button.setText(_translate("MainWindow", "OCR", None))
        self.ocr_all.setText(_translate("MainWindow", "OCR All", None))
        self.label_5.setText(_translate("MainWindow", "Station", None))
        self.label.setText(_translate("MainWindow", "commodity", None))
        self.label_2.setText(_translate("MainWindow", "sell", None))
        self.label_3.setText(_translate("MainWindow", "buy", None))
        self.label_4.setText(_translate("MainWindow", "demand", None))
        self.label_6.setText(_translate("MainWindow", "supply", None))
        self.skip_button.setText(_translate("MainWindow", "Skip", None))
        self.save_button.setText(_translate("MainWindow", "Add and Next", None))
        self.clear_table.setText(_translate("MainWindow", "Clear Table", None))
        self.export_button.setText(_translate("MainWindow", "Export", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings", None))
        self.actionHow_to_use.setText(_translate("MainWindow", "How to use", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionCalibrate.setText(_translate("MainWindow", "Calibrate", None))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences", None))
        self.actionTest.setText(_translate("MainWindow", "Test", None))

from customqtablewidget import CustomQTableWidget
import res_rc
