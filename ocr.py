import cv2
import cv2.cv as cv
import tesseract
import re
from collections import Counter
from bs4 import BeautifulSoup
from PyQt4.QtCore import QSettings
from imageprocessing import *
from settings import loadSettings

def generateNewImage(image, lines, variable):
    """Generate image for an additional OCR run"""
    h, w = image.shape
    vis = np.zeros((h/2, w/2), np.uint8)
    vis = (255 - vis)
    currenty = 20
    currentx = 20
    for line in lines:
        for item in line.items:
            if item != None:
                snippet = image[item.y1-1:item.y2+1, item.x1-1:item.x2+1]
                height, width = snippet.shape
                vis[currenty:currenty+height, currentx:currentx+width] = snippet
                currentx = currentx+width+20+(variable)*3
        currentx = 20
        currenty += 40
    return vis

def ocr(image):
    """Return OCR result."""
    api = tesseract.TessBaseAPI()
    api.Init(".","big",tesseract.OEM_DEFAULT)
    api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
    h,w = image.shape
    w_step = w*image.dtype.itemsize
    iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
    tesseract.SetCvImage(iplimage,api)
    hocr = api.GetHOCRText(0)
    return hocr

def hocrToList(input, scale_factor=1):
    """Converts HOCR HTML data from Tesseract OCR into easily usable objects."""
    soup = BeautifulSoup(input)
    linelist = []
    for line in soup.findAll("span", { "class" : "ocr_line" }):
        wordlist = []
        not_empty = False
        for word in line.findAll("span", { "class" : "ocrx_word" }):
            if word.getText().strip() != '':
                new_word = OCRbox(word['title'], word.getText(), scale_factor)
                wordlist.append(new_word)
                not_empty = True
        if not_empty:
            linelist.append(wordlist)
    return linelist
    

    
def getXAreas(w):
    settings = loadSettings()
    areas = [[0.0, 0.297],
             [0.300, 0.370],
             [0.373, 0.442],
             [0.520, 0.607],
             [0.609, 0.665],
             [0.670, 0.758],
             [0.760, 0.832]]
    new_areas = []
    x = settings["cal_points"][6] - settings["cal_points"][4]
    for area in areas:
        new_areas.append([(area[0]*x + settings["cal_points"][4])*w,
                          (area[1]*x + settings["cal_points"][4])*w])
    return new_areas

def hocrToObject(input, width, scale_factor, station):
    """Converts HOCR HTML data from Tesseract OCR into easily usable objects."""
    #f = open("output.html", "w")
    #f.write(input)
    #f.close()
    soup = BeautifulSoup(input)
    linelist = []
    for line in soup.findAll("span", { "class" : "ocr_line" }):
        wordlist = []
        not_empty = False
        newline = OCRline(line['title'], width, scale_factor)
        for word in line.findAll("span", { "class" : "ocrx_word" }):
            if word.getText().strip() != '':
                newline.addWord(OCRbox(word['title'], word.getText(), scale_factor), station)
                not_empty = True
        if not_empty:
            linelist.append(newline)
    return linelist

class OCR():
    def __init__(self, color_image, gray_image):
        self.repeats = 5
        self.contrast_station_img = None
        self.contrast_commodities_img = None
        self.settings = loadSettings()
        self.image = color_image
        self.gray_image = gray_image
        self.gray_image_alt = gray_image
        self.image_big = color_image
        #self.station = self.ocrStationName()[0]
        self.station = self.readStationName()
        if self.station != None:
            self.commodities = self.readMarket()
        else:
            self.commodities = None
        
    def readStationName(self):
        image = self.image
        self.contrast_station_img = makeCleanStationImage(image)
        h, w, c = image.shape
        scale_factor = 1.0
        if int(w*100.0/h) == 160:
            #16:10 screen ratio
            factor = 2400.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
            scale_factor = factor
        else:
        #if int(w*100.0/h) == 177:
            #16:9 screen ratio and others
            factor = 2160.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
            scale_factor = factor
        h, w, c = image.shape   
        image = makeCleanStationImage(image)
        relevant_points = [int(self.settings["cal_points"][0]*w),
                           int(self.settings["cal_points"][1]*h),
                           int((self.settings["cal_points"][6]-self.settings["cal_points"][0])*w),
                           int((self.settings["cal_points"][3]-self.settings["cal_points"][1])*h)]
        result = self.ocr(image, relevant_points, scale_factor, station = True)
        if len(result) == 0:
            result = None
        else:
            result = result[0]
        return result
        
    def readMarket(self):
        image = self.image
        h, w, c = image.shape
        scale_factor = 1.0

        if int(w*100.0/h) == 160:
            #16:10 screen ratio
            factor = 2400.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
            scale_factor = factor
        else:
        #if int(w*100.0/h) == 177:
            #16:9 screen ratio and others
            factor = 2160.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
            scale_factor = factor

        self.gray_image_alt = adjustTableImg(image, scale_factor)
        image = makeCleanImage(image)
        #cv2.imshow('image', image)
        #cv2.waitKey(0)
        self.image_big = image
        first = self.ocrCommodities(image, scale_factor)
        results = []
        for i in range(self.repeats):
            newimg = self.genImageVariation(i, first)
            results.append(hocrToList(ocr(newimg)))
            
        return self.compareResults(first, results)
    
    def genImageVariation(self, value, lines):
        
        if value == 0:
            image = self.image_big
        else:
            image = contBright(255.0 - self.gray_image_alt, 120.0+((value)*5), 190.0)
            #cv2.imwrite('image.png', self.gray_image_alt)
            #temp = cv2.resize(image, (0,0), fx=0.4, fy=0.4)
            #cv2.imshow('image', temp)
            #cv2.waitKey(0)
            
        image = generateNewImage(image, lines, value)
        #cv2.imwrite('snippets/'+str(value)+'.png',image)
        return image
    
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
                        #print i
                        #print k
                        #print
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
        #alt = Counter(alternatives).most_common()
        sorted = []
        for tuple in alt:
            sorted.append(tuple[0])
        return sorted
    
    def ocrStationName(self):
        self.contrast_station_img = contBright(255.0 - self.gray_image, 0.0, 71.0)
        image = self.contrast_station_img
        h,w = image.shape
        scale_factor = 1
        if h < 2160:
            image = cv2.resize(image, (0,0), 2, 2, cv2.INTER_CUBIC)
            h, w = image.shape
            scale_factor = 2
        
        relevant_points = [int(self.settings["cal_points"][0]*w),
                           int(self.settings["cal_points"][1]*h),
                           int((self.settings["cal_points"][6]-self.settings["cal_points"][0])*w),
                           int((self.settings["cal_points"][3]-self.settings["cal_points"][1])*h)]
        return self.ocr(image, relevant_points, scale_factor)
        
    def ocrCommodities(self, image, scale_factor):
        self.contrast_commodities_img = makeCleanImage(self.image)
        """
        self.contrast_commodities_img = contBright(255.0 - image, 142.0, 190.0)
        h,w = image.shape
        scale_factor = 1
        if h < 2160:
            image = cv2.resize(image, (0,0), 2, 2, cv2.INTER_CUBIC)
            scale_factor = 2

        image = adjustTableImg(image, scale_factor)
        self.image_big = image
        image = contBright(255.0 - image, 142.0, 190.0)
        """
        self.contrast_commodities_img_big = image
        h,w = image.shape
        
        relevant_points = [int(self.settings["cal_points"][4]*w),
                           int(self.settings["cal_points"][5]*h),
                           int((self.settings["cal_points"][6]-self.settings["cal_points"][4])*w),
                           int((self.settings["cal_points"][7]-self.settings["cal_points"][5])*h)]
        return self.ocr(image, relevant_points, scale_factor)
    
    def ocr(self, image, points, factor, station = False):
        """Return OCR result."""
        api = tesseract.TessBaseAPI()
        api.Init(".","big",tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
        h,w = image.shape
        w_step = w*image.dtype.itemsize
        iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
        cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
        tesseract.SetCvImage(iplimage,api)
        api.SetRectangle(*points)
        res = hocrToObject(api.GetHOCRText(0), w, factor, station)
        return res
        
class OCRline():
    """Class providing a recognised line of text as an object, 
       additionally embedding all recognised words in line as OCRBox 
       objects.
    """
    def __init__(self, bbox, width, scale_factor):
        self.scale = scale_factor
        coords = bbox.split()
        self.x1 = int(coords[1])
        self.y1 = int(coords[2])
        self.x2 = int(coords[3])
        self.y2 = int(coords[4].replace(';', ''))
        self.w = int(coords[3]) - int(coords[1])
        self.h = int(coords[4].replace(';', '')) - int(coords[2])
        self.areas_x = getXAreas(width)
        self.name = None
        self.sell = None
        self.buy = None
        self.demand_num = None
        self.demand = None
        self.supply_num = None
        self.supply = None
        # just for understanding:
        self.items = [self.name, self.sell, self.buy, self.demand_num,
                      self.demand, self.supply_num, self.supply]
        
    def addWord(self, word, station = False):
        if station:
            self.addName(word)
            self.items[0] = self.name
            return
            
        x1 = word.x1
        x2 = word.x2
        for x in xrange(0, len(self.areas_x)):
            if x2 < self.areas_x[0][1]:
                self.addName(word)
                self.items[0] = self.name
                break
            if x1 > self.areas_x[1][0] and x2 < self.areas_x[1][1]:
                self.sell = word
                self.sell.value = self.sell.value.replace('.', ',')
                self.items[1] = self.sell
                break
            if x1 > self.areas_x[2][0] and x2 < self.areas_x[2][1]:
                if word.value == "-":
                    self.buy = None
                else:
                    self.buy = word
                    self.buy.value = self.buy.value.replace('.', ',')
                    self.items[2] = self.buy
                break
            if x1 > self.areas_x[3][0] and x2 < self.areas_x[3][1]:
                self.demand_num = word
                self.demand_num.value = self.demand_num.value.replace('.', ',')
                self.items[3] = self.demand_num
                break
            if x1 > self.areas_x[4][0] and x2 < self.areas_x[4][1]:
                self.demand = word
                self.items[4] = self.demand
                break
            if x1 > self.areas_x[5][0] and x2 < self.areas_x[5][1]:
                self.supply_num = word
                self.supply_num.value = self.supply_num.value.replace('.', ',')
                self.items[5] = self.supply_num
                break
            if x1 > self.areas_x[6][0] and x2 < self.areas_x[6][1]:
                self.supply = word
                self.items[6] = self.supply
                break
        
                
    def addName(self, word):
        if self.name == None:
            self.name = word
        else:
            bbox = "bbox " + str(self.name.x1) + " " +\
                   str(self.name.y1) + " " + str(word.x2) +\
                   " " + str(word.y2)
            self.name = OCRbox(bbox, self.name.value+" "+word.value, self.scale)
    
    def __str__(self):
        return "OCRline: "+ str(self.items)
    
    def __repr__(self):
        return "OCRline: "+ str(self.items)
            
    
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, bbox, text, scale_factor):
        self.scale = scale_factor
        coords = bbox.split()
        self.x1 = int(coords[1])
        self.y1 = int(coords[2])
        self.x2 = int(coords[3])
        self.y2 = int(coords[4].replace(';', ''))
        self.w = int(coords[3]) - int(coords[1])
        self.h = int(coords[4].replace(';', '')) - int(coords[2])
        self.value = text.strip()
        self.confidence = 0

        self.optional_values = []
        
    def __str__(self):
        return "OCRbox: "+ str(self.value)
    
    def __repr__(self):
        return "OCRbox: "+ str(self.value)