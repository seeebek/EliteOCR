import cv2
import re
from PyQt4.QtCore import QSettings
from settings import Settings
from imageprocessing import contBright

#OCR engines:
from engine import MLP

class OCR():
    def __init__(self, color_image, ocr_areas, language = "big", item = None):
        self.item = item
        self.lang = language
        self.settings = Settings()
        self.image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        
        self.contrast_station_img = self.makeStationImgClean(ocr_areas.station_name)
        self.contrast_commodities_img = self.makeMarketImgClean(ocr_areas.market_table)
        
        self.station_img = self.makeStationImg(ocr_areas.station_name)
        self.commodities_img = self.makeMarketImg(ocr_areas.market_table)

        self.ocr_areas = ocr_areas

        self.station = self.readStationName()

        self.commodities = self.readMarket()

        
    def readStationName(self):
        station = MLP(self.station_img, self.settings.app_path, self.ocr_areas.areas, isstation=True)
        return station.result[0]
        
    def readMarket(self):
        market = MLP(self.commodities_img, self.settings.app_path, self.ocr_areas.areas, isstation=False)
        return market.result
    
    def makeStationImgClean(self, station):
        img = self.image[station[0][1]-2:station[1][1]+2, station[0][0]-2:station[1][0]+2]
        img = 255 - contBright(img, 100.0, 200.0)
        return img
        
    def makeMarketImgClean(self, market):
        img = self.image[market[0][1]:market[1][1], market[0][0]:market[1][0]]
        img = 255 - contBright(img, 65.0, 110.0)
        return img
    
    def makeStationImg(self, station):
        img = self.image[station[0][1]:station[1][1], station[0][0]:station[1][0]]
        img = 255 - contBright(img, 120.0, 160.0)
        return img
        
    def makeMarketImg(self, market):
        img = self.image[market[0][1]:market[1][1], market[0][0]:market[1][0]]
        img = 255 - contBright(img, 85.0, 90.0)
        return img
    
