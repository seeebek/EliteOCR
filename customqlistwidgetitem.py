import cv2
import re
import numpy as np
from os import listdir
from os.path import getctime
from time import gmtime, localtime, strftime
from PyQt4.QtGui import QListWidgetItem, QPixmap
from qimage2ndarray import array2qimage
from imageprocessing import *
from ocrmethods import OCRAreasFinder

class CustomQListWidgetItem(QListWidgetItem):
    def __init__(self, text, hiddentext, settings):
        QListWidgetItem.__init__(self, text)
        self.settings = settings
        self.hiddentext = hiddentext
        #self.color_image = self.addImage(hiddentext)
        #self.preview_image = self.addPreviewImage()
        
        self.timestamp = self.getTimeStamp()
        self.filetime = self.getFileTime()
        self.system = self.getSystemName()
        self.valid_market = False
        
    def loadColorImage(self):
        return self.addImage(self.hiddentext)
        
    def loadPreviewImage(self, color_image):
        return self.addPreviewImage(color_image)
    
    def addImage(self,imagepath):
        image = cv2.imread(unicode(imagepath))
        h, w, c = image.shape
        #cut image if too long to prevent memory errors
        aspect_ratio = float(w) / (h)
        if aspect_ratio > 1.78:
            new_w = int(1.77778*h)
            cut = image[0:h, (w - new_w)/2:(w - new_w)/2 + new_w]
            return cut
        return image
    
    def addPreviewImage(self, color_image):
        image = color_image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = image.shape
        ocr_areas = OCRAreasFinder(color_image)
        points = ocr_areas.market_table
        self.valid_market = ocr_areas.valid
        if self.valid_market:
            cut = image[0:points[1][1] + 20,
                        0:points[1][0] + 20]
        else:
            cut = image[:]
        processedimage = array2qimage(cut)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        return pix
        
    def getTimeStamp(self):
        """Return timestamp for selected file."""
        tmstmp = gmtime(getctime(unicode(self.hiddentext)))
        file_tmstmp = unicode(strftime("%Y-%m-%dT%H:%M", tmstmp))
        return file_tmstmp
    
    def getFileTime(self):
        """Return creation time as an array, for searching in logs"""
        tmstmp = localtime(getctime(unicode(self.hiddentext)))
        year = strftime("%y", tmstmp)
        month = strftime("%m", tmstmp)
        day = strftime("%d", tmstmp)
        hour = strftime("%H", tmstmp)
        minute = strftime("%M", tmstmp)
        second = strftime("%S", tmstmp)
        return [year, month, day, hour, minute, second]
        
    def getSystemName(self):
        """Get system name from log files""" # TODO make more robust and cleaner
        path = self.settings['log_dir']
        dir = listdir(path)
        matchfile = "^netLog."+self.filetime[0]+self.filetime[1]+self.filetime[2]
        matchfile2 = "^netLog."+self.filetime[0]+self.filetime[1]+unicode(int(self.filetime[2])-1)
        matchscreen = "^{"+self.filetime[3]+":"+self.filetime[4]+":..} SCREENSHOT:"
        matchsystem = "^{[\S]*}\sSystem:"
        findname = "[(].+?[)]"
        candidates = []
        for file in dir:
            if re.match(matchfile, file):
                candidates.append(file)
        
        screenshotfound = False
        for file in candidates:
            for line in reversed(open(path+"\\"+file).readlines()):
                if screenshotfound:
                    if re.match(matchsystem, line):
                        match = re.search(findname, line)
                        if match:
                            return match.group(0).strip("(").strip(")")
                else:
                    if re.match(matchscreen, line):
                        screenshotfound = True
        
        #second try one day before (if game started before midnight but screenshot made after)
        candidates = []
        for file in dir:
            if re.match(matchfile2, file):
                candidates.append(file)
        
        screenshotfound = False
        for file in candidates:
            for line in reversed(open(path+"\\"+file).readlines()):
                if screenshotfound:
                    if re.match(matchsystem, line):
                        match = re.search(findname, line)
                        if match:
                            return match.group(0).strip("(").strip(")")
                else:
                    if re.match(matchscreen, line):
                        screenshotfound = True
        return ""
