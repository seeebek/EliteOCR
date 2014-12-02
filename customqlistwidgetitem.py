import cv2
import numpy as np
from os.path import getctime
from time import gmtime, strftime
from PyQt4.QtGui import QListWidgetItem, QPixmap
from settings import loadSettings
from qimage2ndarray import array2qimage
from imageprocessing import *

class CustomQListWidgetItem(QListWidgetItem):
    def __init__(self, text, hiddentext):
        QListWidgetItem.__init__(self, text)
        self.settings = loadSettings()
        self.hiddentext = hiddentext
        self.color_image = self.addImage(hiddentext)
        self.image = cv2.cvtColor(self.color_image, cv2.COLOR_BGR2GRAY)
        self.preview_image = self.addPreviewImage()
        
        self.timestamp = self.getTimeStamp()
        
    def addImage(self,imagepath):
        image = cv2.imread(str(imagepath))
        return image
    
    def addPreviewImage(self):
        #image = self.color_image
        #h, w, c = image.shape
        image = self.image
        h, w = image.shape
        cut = image[0:self.settings["cal_points"][7]*h + 20,
                    0:self.settings["cal_points"][6]*w + 20]
        processedimage = array2qimage(cut)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        return pix
        
    def getTimeStamp(self):
        """Return timestamp for selected file."""
        tmstmp = gmtime(getctime(str(self.hiddentext)))
        file_tmstmp = str(strftime("%Y-%m-%dT%H:%M", tmstmp))
        return file_tmstmp
