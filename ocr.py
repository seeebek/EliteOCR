# -*- coding: utf-8 -*-
import cv2
from PyQt4.QtCore import QSettings
from settings import Settings
from imageprocessing import contBright, whiteBalance

#OCR engines:
from engine import MLP, Levenshtein

class OCR():
    def __init__(self, color_image, ocr_areas, language = "big", item = None, levels = True, levenshtein = True):
        #self.contrast = 85.0 # standard
        self.item = item
        self.lang = language
        self.settings = Settings()
        self.contrast = self.settings["contrast"]
        self.image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        self.contrast_station_img = self.makeStationImgClean(ocr_areas.station_name)

        self.contrast_commodities_img = self.makeMarketImgClean(ocr_areas.market_table)
        
        self.station_img = self.makeStationImg(ocr_areas.station_name)
        self.commodities_img = self.makeMarketImg(ocr_areas.market_table)

        self.ocr_areas = ocr_areas

        self.station = self.readStationName()

        self.commodities = self.readMarket(levels, levenshtein)

    def readStationName(self):
        station = MLP(self.station_img, self.settings, self.ocr_areas.areas, isstation=True)
        #print station.result[0].name
        return station.result[0]
        
    def readMarket(self, levels, levenshtein = True):
        market = MLP(self.commodities_img, self.settings, self.ocr_areas.areas, isstation=False)
        #for line in market.result:
        #    print line.name
        if levenshtein:
            Levenshtein(market.result, self.settings.app_path, self.lang, levels)
        return market.result
    
    def makeStationImgClean(self, station):
        img = self.image[station[0][1]-2:station[1][1]+2, station[0][0]-2:station[1][0]+2]
        img = 255 - contBright(img, 100.0, 200.0)
        return img
        
    def makeMarketImgClean(self, market):
        img = self.image[market[0][1]:market[1][1], market[0][0]:market[1][0]]
        img = 255 - contBright(img, self.contrast - 20.0, self.contrast + 20.0)
        return img
    
    def makeStationImg(self, station):
        img = self.image[station[0][1]:station[1][1], station[0][0]:station[1][0]]
        h, w = img.shape  
        img = whiteBalance(img)
        #cv2.imshow("x", img)
        #cv2.waitKey(0)
        img = 255 - contBright(img, 250.0, 255.0)
        try:
            h, w = img.shape
            if w == 0 or h == 0:
                img = np.ones((1,1), dtype='float32')
        except:
            img = np.ones((1,1), dtype='float32')
        return img
        
    def makeMarketImg(self, market):
        img = self.image[market[0][1]:market[1][1], market[0][0]:market[1][0]]
        img = contBright(img, self.contrast, self.contrast+5.0)
        #cv2.imshow("x", img)
        #cv2.waitKey(0)
        img = 255 - img
        try:
            h, w = img.shape
            if w == 0 or h == 0:
                img = np.ones((1,1), dtype='float32')
        except:
            img = np.ones((1,1), dtype='float32')
        return img
    
