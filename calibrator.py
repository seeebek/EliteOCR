# -*- coding: utf-8 -*-
import cv2
import numpy as np
import codecs
import json
from time import time
from PyQt4.QtCore import QSettings, QThread, SIGNAL
from PyQt4.QtGui import QColor
from settings import Settings
from imageprocessing import contBright
from settings import Settings
from Levenshtein import ratio, distance
import sys
import os
from os.path import isdir
from os import listdir
from collections import Counter
from colorthief import ColorThief

#OCR engines:
from engine import MLP, Levenshtein, OCRAreasFinder

class Calibrator(QThread):
    def __init__(self, parent, imglist, language):
        QThread.__init__(self, parent)
        self.language = language
        self.parent = parent
        self.imglist = imglist
        self.steps = None
        self.left = None
        self.contrast = None
        self.time1 = None
    
    def execute(self):
        self.start()
    
    def run(self):
        self.ocr_areas = None
        self.min_contrast = 0.0
        self.max_contrast = 255.0
        self.settings = Settings()
        
        self.bestlist = []

        self.image_data = []
        
        for file in self.imglist:
            #print file
            image = cv2.imread(unicode(file).encode(sys.getfilesystemencoding()))
            h, w, c = image.shape
            #if h > 1080:
            #    width = int(w*(900.0/h))
            #    image = cv2.resize(image, (width, 900)) 
            self.calculate(image)
  
        clean = {}
        
        total = len(self.bestlist)    
        for i in xrange(int(self.min_contrast), int(self.max_contrast)):
            count = 0
            temp = 0
            for item in self.bestlist:
                if float(i) in item:
                    count+=1
                    temp+=item[float(i)]
            if count == total:
                clean[i] = temp
                
        #print clean

        cleanlist = sorted(clean.items(), key=lambda x: x[1])
        tolerance = cleanlist[0][1] + 2
        tolerated = []

        for j in range(len(cleanlist)):
            if cleanlist[j][1] < tolerance:
                tolerated.append(cleanlist[j][0])

        #print tolerated
        self.bestcontrast = reduce(lambda x, y: x + y, tolerated) / len(tolerated)
        self.error = cleanlist[0][1]
        #print self.bestcontrast
        """
        hist = []
        for i in xrange(256):
            if i in clean:
                hist.append(clean[i])
            else:
                hist.append(0)
        hist = np.asarray(hist)
        cv2.normalize(hist,hist,0,1000,cv2.NORM_MINMAX)

        h = np.zeros((1000,256,3))

        for x in xrange(len(hist)):
            cv2.line(h,(x,hist[x]),(x,hist[x]),(255,255,255))
        y=np.flipud(h)
        cv2.imshow('histogram',y)
        cv2.waitKey(0)
        """
        #self.emit(SIGNAL("update(int,int)"), counter, toprocess)
        #self.result = "Success: "+unicode(len(outcomeok))+" Fail: "+unicode(len(outcomefail))
        
        #ct = ColorThief(image)
        #palette = ct.get_palette()
        #for i in xrange(1,6):
        #    self.settings.reg.setValue('color'+str(i), QColor(*(palette[i-1])).name())
        
        self.emit(SIGNAL("finished(float, int, PyQt_PyObject)"), self.bestcontrast, self.error, self.image_data)
    
    def runTest(self, image, market, contrast):
        img = image[market[0][1]:market[1][1], market[0][0]:market[1][0]]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h,w = img.shape
        img = contBright(img, contrast, contrast+5.0)
        img = 255 - img
        #cv2.imshow("x", img)
        #cv2.waitKey(0)
        mlp = MLP(img, self.settings.app_path, self.ocr_areas.areas, isstation=False, calibration=True)
        #print market.result
        #for result in market.result:
        #    print result.name.value
        
        if self.language == "English":
            language = u"eng"
        elif self.language == "German":
            language = u"deu"
        else:
            language = u"fra"

        levels = {u"eng": [u'LOW', u'MED', u'HIGH'],
                  u"deu": [u'NIEDRIG', u'MITTEL', u'HOCH'], 
                  u"fra": [u'FAIBLE', u'MOYEN', u'ÉLEVÉ']}
        file = codecs.open(self.settings.app_path + os.sep +"commodities.json", 'r', "utf-8")
        comm_list = json.loads(file.read())
        file.close()
        #print self.comm_list
        #self.comm_list.sort(key = len)
        if language == "big" or language == "eng":
            comm_list = [k for k, v in comm_list.iteritems()]
        else:
            comm_list = [v[language] for k, v in comm_list.iteritems()]

        total_error = 0
        lines = 0
        for result in mlp.result:
            #print result.name.value
            
            if (not result.name is None) and result.name.value != '':
                if result.name.x1 > h/18:
                    lines +=1
                    mindist = 100
                    topcomm = ""
                    alternatives = []
                    for comm in comm_list:
                        #print (result.name.value, unicode(comm))
                        dist = distance(result.name.value, unicode(comm))
                        #if dist < 7:
                        #    alternatives.append((unicode(comm), dist))
                        if dist < mindist:
                            mindist = dist
                            topcomm = comm
                        if dist == 0:
                            mindist = 0
                #print result.name.value
                #print topcomm
                #print
                    #if mindist > 0:
                    #    print (topcomm, result.name.value)
                    for letter in topcomm:
                        if letter in [u"Ä",u"Ö",u"Ü"]:
                            mindist -= 1
                    total_error += mindist
        #print "contrast " + unicode(contrast)
        #print "lines " + unicode(lines)    
        #print "error " +unicode(total_error)
        #print
        return [lines, total_error, contrast]

    def calculate(self, image):
        h, w, c = image.shape
        img_height = h
        self.ocr_areas = OCRAreasFinder(image, self.contrast)
        if self.contrast is None:
            self.contrast = self.ocr_areas.contrast
        valid_market = self.ocr_areas.valid
        self.image_data.append([valid_market, w, h, self.ocr_areas.market_width])
        #print self.ocr_areas.market_table

        if valid_market:
            market = self.ocr_areas.market_table
            market_offset = (market[0][0], market[0][1])
            station = self.ocr_areas.station_name
            station_offset = (station[0][0], station[0][1])
            max_lines = 0
            start_lines = 0.0
            if self.min_contrast == 0.0 and self.max_contrast == 255.0:
                for i in xrange(5, 250, 5):
                    res = self.runTest(image, market, float(i))
                    
                    """
                    if res[1] > 30 and self.min_contrast != 0.0 and self.max_contrast == 255.0:
                        self.max_contrast = res[2]
                    if res[0] < 5 and self.min_contrast != 0.0 and max_contrast == 255.0:
                        self.max_contrast = res[2]
                    """
                    if res[0] < 10 and self.min_contrast != 0.0 and self.max_contrast == 255.0:
                        self.max_contrast = res[2]
                        break
                    if res[0] > 11 and self.min_contrast == 0.0:
                        self.min_contrast = res[2]
            
            if self.steps is None:
                self.steps = int(self.max_contrast - self.min_contrast)*len(self.imglist)
                self.left = self.steps
                self.emit(SIGNAL("steps(int)"), self.steps)
            #self.parent.analyzing_progress.setMaximum(steps)
            #self.parent.repaint()
            
            #print (self.min_contrast, self.max_contrast)
            results = []
            lines = []
            if self.time1 is None:
                self.time1 = time()
            for i in xrange(int(self.min_contrast), int(self.max_contrast), 1):
                
                res = self.runTest(image, market, float(i))
                results.append(res)
                lines.append(res[0])
                self.time2 = time()
                self.left -= 1
                #time_left = self.left
                time_left = int(((self.time2 - self.time1)/(self.steps-self.left))*self.left)
                self.emit(SIGNAL("progress(int)"), time_left)
            
            data = Counter(lines)
            valid_lines = data.most_common(1)[0][0]
            
            #list1 = sorted(results, key = lambda x : (-x[0], x[1], x[2]))
            best = {}
            for entry in results:
                if entry[0] == valid_lines:
                    if not entry[2] in best:
                        best[entry[2]] = entry[1]
                    else:
                        best[entry[2]] += entry[1]
            self.bestlist.append(best)

    """
    #img = contBright(img, 85.0, 90.0)
    img = contBright(img, 65.0, 70.0)
    cv2.imshow("x", img)
    cv2.waitKey(0)
    img = 255 - img
    cv2.imshow("x", img)
    cv2.waitKey(0)
    return img
    """