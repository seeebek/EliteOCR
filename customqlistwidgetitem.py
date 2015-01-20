# -*- coding: utf-8 -*-
import cv2
import re
import numpy as np
import pytz
from os import listdir
from os.path import getmtime, getctime, isdir
from time import gmtime, localtime, strftime
from tzlocal import get_localzone
from datetime import datetime, timedelta
from PyQt4.QtGui import QListWidgetItem, QPixmap
from qimage2ndarray import array2qimage
from imageprocessing import *
from ocrmethods import OCRAreasFinder

class CustomQListWidgetItem(QListWidgetItem):
    def __init__(self, text, hiddentext, settings):
        QListWidgetItem.__init__(self, text)
        self.settings = settings
        self.hiddentext = hiddentext
        
        self.timestamp = self.getTimeStamp()
        self.filetime = self.getFileTime()
        #self.filetime = ["14", "12", "23", "18", "58", "30"]
        self.system = self.getSystemName()
        self.valid_market = False
        self.img_height = 0
<<<<<<< HEAD
        self.market_width = 0
=======
>>>>>>> origin/dev
        self.ocr_areas = None
        
    def loadColorImage(self):
        return self.addImage(self.hiddentext)
        
    def loadPreviewImage(self, color_image, parent = None):
        return self.addPreviewImage(color_image, parent)
    
    def addImage(self,imagepath):
        image = cv2.imread(imagepath)
        h, w, c = image.shape
        self.img_height = h
        #cut image if too long to prevent memory errors
        aspect_ratio = float(w) / (h)
        if aspect_ratio > 1.78:
            new_w = int(1.77778*h)
            cut = image[0:h, (w - new_w)/2:(w - new_w)/2 + new_w]
            return cut
        return image
    
    def addPreviewImage(self, color_image, parent = None):
        image = color_image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if not parent is None:
            parent.progress_bar.setValue(12)
        h, w = image.shape
        self.img_height = h
        self.ocr_areas = OCRAreasFinder(color_image)
<<<<<<< HEAD
        self.market_width = self.ocr_areas.market_width 
=======
>>>>>>> origin/dev
        if not parent is None:
            parent.progress_bar.setValue(14)
        points = self.ocr_areas.market_table
        self.valid_market = self.ocr_areas.valid
        if self.valid_market:
            cut = image[0:points[1][1] + 20,
                        0:points[1][0] + 20]
        else:
            cut = image[:]
        processedimage = array2qimage(cut)
        if not parent is None:
            parent.progress_bar.setValue(16)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        if not parent is None:
            parent.progress_bar.setValue(18)
        return pix
        
    def getTimeStamp(self):
        """Return timestamp for selected file."""
        creationtime = getmtime(self.hiddentext)
        tmstmp = datetime.fromtimestamp(creationtime)
        timezone = get_localzone()
        localtime = timezone.localize(tmstmp)
        utc_time = localtime.astimezone (pytz.utc)
        file_tmstmp = unicode(datetime.strftime(utc_time, "%Y-%m-%dT%H:%M:%S+00:00"))
        return file_tmstmp
    
    def getFileTime(self):
        """Return creation time as an array, for searching in logs"""
        creationtime = getmtime(self.hiddentext)
        tmstmp = localtime(creationtime)
        year = strftime("%y", tmstmp)
        month = strftime("%m", tmstmp)
        day = strftime("%d", tmstmp)
        hour = strftime("%H", tmstmp)
        minute = strftime("%M", tmstmp)
        second = strftime("%S", tmstmp)
        return [year, month, day, hour, minute, second]
        
    def getSystemName(self):
        """Get system name from log files"""
        path = unicode(self.settings['log_dir']).encode('windows-1252')
        if not isdir(path):
            return ""
        dir = listdir(path)
        system_name = self.parseLogFile(path, dir, self.filetime[0], self.filetime[1], self.filetime[2],
                                 self.filetime[3], self.filetime[4])
        if system_name == "" and int(self.filetime[3]) < 8:
<<<<<<< HEAD
            newdate = datetime(int(self.filetime[0]), int(self.filetime[1]), int(self.filetime[2]),
                                 int(self.filetime[3]), int(self.filetime[4])) - timedelta(days=1)
            system_name = self.parseLogFile(path, dir, str(newdate.year), str(newdate.month), str(newdate.day),
=======
            newdate = datetime(self.filetime[0], self.filetime[1], self.filetime[2],
                                 self.filetime[3], self.filetime[4]) - timedelta(days=1)
            system_name = self.parseLogFile(path, dir, newdate.year, newdate.month, newdate.day,
>>>>>>> origin/dev
                                 self.filetime[3], self.filetime[4])
        return system_name
        
    def parseLogFile(self, path, loglist, y, m, d, hour, minute):
        matchfile = "^netLog."+y+m+d
        matchscreen = "^{"+hour+":"+minute+":..}"
        matchsystem = "^{[\S]*}\sSystem:"
        findname = "[(].+?[)]"
        candidates = []
        for file in loglist:
            if re.match(matchfile, file):
                candidates.append(file)
        candidates.sort(reverse=True)
        if len(candidates) == 0:
            return ""
            
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