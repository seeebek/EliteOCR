# -*- coding: utf-8 -*-
import cv2
import re
# -*- coding: utf-8 -*-
import numpy as np
import pytz
import os
from os import listdir
from os.path import getmtime, getctime, isdir
from time import gmtime, localtime, strftime
from tzlocal import get_localzone
from datetime import datetime, timedelta
from PyQt4.QtGui import QListWidgetItem, QPixmap
from PyQt4.QtCore import QRect
from qimage2ndarray import array2qimage
from imageprocessing import *
#from ocrmethods import OCRAreasFinder
from engine import OCRAreasFinder


class CustomQListWidgetItem(QListWidgetItem):
    def __init__(self, text, hiddentext, settings):
        QListWidgetItem.__init__(self, text)
        self.settings = settings
        self.hiddentext = hiddentext
        
        self.timestamp = self.getTimeStamp()
        self.filetime = self.getFileTime()

        self.log_file = None
        self.search_time = None
        self.system = self.getSystemName()
        
        if len(self.system) > 0:
            self.station = self.getStationName(self.search_time)
        else:
            self.station = None
        self.valid_market = False
        self.img_height = 0
        self.market_width = 0
        self.offset = None
        self.ocr_areas = None
        
    def loadColorImage(self):
        return self.addImage(self.hiddentext)
        
    def loadPreviewImage(self, color_image, parent = None):
        return self.addPreviewImage(color_image, parent)
    
    def loadTestImage(self):
        return self.addTestImage(self.hiddentext)
    
    def addImage(self, imagepath):
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
    
    def addTestImage(self, color_image):
        self.ocr_areas = OCRAreasFinder(color_image, self.settings["contrast"])
        self.market_width = self.ocr_areas.market_width
        self.valid_market = self.ocr_areas.valid
        img = QPixmap(self.hiddentext)
        width = img.width()
        height = img.height()
        aspect_ratio = float(width)/height
        if aspect_ratio > 1.78:
            new_w = int(1.77778*height)
            rect = QRect((width-new_w)/2, 0, new_w, height)
            img = img.copy(rect)
            
        if self.valid_market:
            points = self.ocr_areas.market_table
            self.market_offset = (points[0][0], points[0][1])
            station = self.ocr_areas.station_name
            self.station_offset = (station[0][0], station[0][1])
            rect = QRect(0, 0, points[1][0] + 20, points[1][1] + 20)
            cut = img.copy(rect)
            return cut
        else:
            self.market_offset = (0, 0)
            self.station_offset = (0, 0)

            
        
        return img
        
    def addPreviewImage(self, color_image, parent = None):
        image = color_image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if not parent is None:
            parent.progress_bar.setValue(12)
        h, w = image.shape
        self.img_height = h
        self.ocr_areas = OCRAreasFinder(color_image, self.settings["contrast"])
        self.market_width = self.ocr_areas.market_width
        if not parent is None:
            parent.progress_bar.setValue(14)
        
        self.valid_market = self.ocr_areas.valid
        if self.valid_market:
            points = self.ocr_areas.market_table
            self.market_offset = (points[0][0], points[0][1])
            station = self.ocr_areas.station_name
            self.station_offset = (station[0][0], station[0][1])
            cut = image[0:points[1][1] + 20,
                        0:points[1][0] + 20]
        else:
            cut = image[:]
            self.market_offset = (0, 0)
            self.station_offset = (0, 0)
            
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

    def getStationName(self, search_time):
        path = unicode(self.settings['log_dir']).encode(sys.getfilesystemencoding())
        matchscreen = "^{"+search_time[0]+":"+search_time[1]+":..}"
        matchline = "^{[\S]*}\sFindBestIsland:"
        
        stationfound = False
<<<<<<< HEAD
        for line in reversed(open(path + os.sep +self.log_file).readlines()):
=======
        for line in reversed(open(path+os.sep+self.log_file).readlines()):
>>>>>>> master
            if stationfound:
                if re.match(matchline, line):
                    elements = line.split(":")
                    return elements[-2]

            else:
                if re.match(matchscreen, line):
                    stationfound = True
        return None
    
    def getSystemName(self):
        """Get system name from log files"""
        path = unicode(self.settings['log_dir']).encode(sys.getfilesystemencoding())
        if not isdir(path):
            return ""
        dir = listdir(path)
        system_name = self.parseLogFile(path, dir, self.filetime[0], self.filetime[1], self.filetime[2],
                                 self.filetime[3], self.filetime[4])
        if system_name == "" and int(self.filetime[3]) < 8:
            newdate = datetime(int('20'+self.filetime[0]), int(self.filetime[1]), int(self.filetime[2]),
                                 int(self.filetime[3]), int(self.filetime[4])) - timedelta(days=1)
            system_name = self.parseLogFile(path, dir, newdate.strftime("%y"), newdate.strftime("%m"), newdate.strftime("%d"),
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
<<<<<<< HEAD
            for line in reversed(open(path + os.sep +file).readlines()):
=======
            for line in reversed(open(path+os.sep+file).readlines()):
>>>>>>> master
                if screenshotfound:
                    if re.match(matchsystem, line):
                        match = re.search(findname, line)
                        if match:
                            self.log_file = file
                            self.search_time = (hour, minute)
                            return match.group(0).strip("(").strip(")")
                else:
                    if re.match(matchscreen, line):
                        screenshotfound = True
        return ""
