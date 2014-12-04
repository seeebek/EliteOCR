import cv2
import re
import numpy as np
from os import listdir
from os.path import getctime
from time import gmtime, localtime, strftime
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
        self.filetime = self.getFileTime()
        self.system = self.getSystemName()
        
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
    
    def getFileTime(self):
        """Return creation time as an array, for searching in logs"""
        tmstmp = localtime(getctime(str(self.hiddentext)))
        year = strftime("%y", tmstmp)
        month = strftime("%m", tmstmp)
        day = strftime("%d", tmstmp)
        hour = strftime("%H", tmstmp)
        minute = strftime("%M", tmstmp)
        second = strftime("%S", tmstmp)
        return [year, month, day, hour, minute, second]
        
    def getSystemName(self):
        path = self.settings['log_dir']
        dir = listdir(path)
        matchfile = "^netLog."+self.filetime[0]+self.filetime[1]+self.filetime[2]
        matchfile2 = "^netLog."+self.filetime[0]+self.filetime[1]+str(int(self.filetime[2])-1)
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
