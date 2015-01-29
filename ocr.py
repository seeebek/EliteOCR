import cv2
import cv2.cv as cv
import tesseract
import re
from collections import Counter
from bs4 import BeautifulSoup
from PyQt4.QtCore import QSettings
from imageprocessing import *
from settings import Settings

#OCR engines:
from ocrmethods import TesseractStation, TesseractStationMLP, TesseractMarket1, Levenshtein, NNMethod, MLPMethod

class OCR():
    def __init__(self, parent, color_image, ocr_areas, language = "big", item = None):
        self.item = item
        self.lang = language
        self.settings = Settings()
        self.repeats = 1
        self.image = color_image
        if not parent is None:
            parent.progress_bar.setMinimum(0)
            parent.progress_bar.setMaximum(60)
            parent.progress_bar.setValue(0)
        self.contrast_station_img = makeCleanStationImage(self.image, item)
        cv2.imwrite(".\\nn_training_images\\station.png", self.contrast_station_img)
        if not parent is None:
            parent.progress_bar.setValue(10)
            parent.repaint()
        else:
            sys.stdout.write("\r[===       ]")
            sys.stdout.flush()
        self.contrast_commodities_img = makeCleanImage(self.image, item)
        if not parent is None:
            parent.progress_bar.setValue(20)
        self.ocr_areas = ocr_areas
        if not parent is None:
            parent.progress_bar.setValue(30)
        self.station = self.readStationName(parent)
        if not parent is None:
            parent.progress_bar.setValue(40)
        else:
            sys.stdout.write("\r[====      ]")
            sys.stdout.flush()
        self.commodities = self.readMarket(parent)
        if not parent is None:
            parent.progress_bar.setValue(0)
        
    def readStationName(self, parent):
        station_name = TesseractStation(self.contrast_station_img, self.ocr_areas.station_name)
        station_name1 = TesseractStationMLP(self.contrast_station_img, station_name.result[0], self.settings.app_path)
        
        if len(station_name.result) > 0:
            return station_name.result[0]
        else:
            return None
        
    def readMarket(self, parent):
        market_table = TesseractMarket1(parent, self.contrast_commodities_img, self.ocr_areas.market_table, self.lang)
        if not self.item is None:
            if self.item.market_width > 1065:
                mlp = MLPMethod(parent, self.contrast_commodities_img, market_table.result, self.settings.app_path)
        if not parent is None:
            parent.progress_bar.setValue(50)
        else:
            sys.stdout.write("\r[=====     ]")
            sys.stdout.flush()
        clean_commodities = Levenshtein(market_table.result, self.settings.app_path, self.lang)
        clean_numbers = NNMethod(parent,self.contrast_commodities_img, market_table.result, self.settings.app_path)
        if not parent is None:
            parent.progress_bar.setValue(60)
        
        #return self.compareResults(market_table.result,[market_table2.result])
        return clean_numbers.result
        
    def compareResults(self, first, additional):
        for i in range(len(first)):
            internal = 0
            for j in range(len(first[i].items)):
                item = first[i].items[j]
                if item != None:
                    alternatives = []
                    if self.testTypeConformity(j, item.value):
                        alternatives.append(item.value)
                    for k in range(len(additional)):
                        if i < len(additional[k]):
                            if self.checkResultCompatible(first[i], additional[k][i]):
                                newi = ""
                                for l in range(len(item.value.split(' '))):
                                    newi += additional[k][i][internal+l].value + " "
                                if j != 0:
                                    newi = newi.replace('.', ',')
                                if self.testTypeConformity(j, newi):
                                    alternatives.append(newi.strip())

                    if len(additional) > 1:
                        most_common = Counter(alternatives).most_common()
                        if len(most_common) > 0:
                            item.value = most_common[0][0]
                            item.confidence = most_common[0][1]/(self.repeats+1.0)
                            item.optional_values = self.sortAlternatives(most_common)
                    else:
                        item.value = alternatives[1]
                        item.optional_values = list(set(alternatives))
                        
                    internal += len(item.value.split(' '))
        return first
        
    def testTypeConformity(self, index, item):
        numlist = [1, 2, 3,5]
        if index in numlist:
            return re.match("^[0-9,]*$", item.strip())
        else:
            return re.match("^[-A-Z. ]*$", item.strip())
            
    def checkResultCompatible(self, one, two):
        entries = 0
        for item in one.items:
            if item != None:
                entries += 1
        entries += len(one.items[0].value.split(" "))-1
        if entries == len(two):
            return True
        else:
            return False       

    def sortAlternatives(self, alt):
        sorted = []
        for tuple in alt:
            sorted.append(tuple[0])
        return sorted