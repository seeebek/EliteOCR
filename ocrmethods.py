import cv2
import math
import tesseract
import json
import numpy as np
import cv2.cv as cv
from imageprocessing import *
from bs4 import BeautifulSoup
from nn_scripts.nn_training import nnTraining
from Levenshtein import ratio, distance
from collections import Counter

class OCRAreasFinder:
    def __init__(self, image):
        self.station_name = None
        self.market_table = None
        self.valid = False
        self.findAreas(image)
        
    def findAreas(self, image):
        img = image
        imgheight, imgwidth, xcolor = img.shape
        b,g,r  = cv2.split(img)
        b = np.add(b, 0.0) 
        new = np.divide(np.multiply(b, g), 255.0)
        value = np.clip(new, 0.0, 255.0)
        value = value.astype(np.uint8)
        ret,thresh1 = cv2.threshold(value,128,255,cv2.THRESH_BINARY)
        workimg = cv2.GaussianBlur(thresh1,(51,11),0)
        ret,cont = cv2.threshold(workimg,1,255,cv2.THRESH_BINARY)
        #cv2.imshow("xx", cont)
        #cv2.waitKey(0)
        contours,hierarchy = cv2.findContours(cont, 1, 2)
        cnt = contours
        y_pos = []
        for c in cnt:
            if cv2.contourArea(c) > 200:
                x,y,w,h = cv2.boundingRect(c)
                y_pos.append([y,h,x])
        
        r = np.add(r, 0.0) 
        new = np.absolute(np.subtract(r, b))
        new = np.subtract(np.add(new,g), 128.0)
        value = np.clip(new, 0, 255)
        value = value.astype(np.uint8)
        h, w = value.shape
        ret,thresh1 = cv2.threshold(255 - value,128,255,cv2.THRESH_BINARY)
        lines = cv2.HoughLinesP((255 - thresh1), 1, math.pi/2, 2, None, h/2, 1);
        counter = 0
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        if not (lines is None):
            for line in lines[0]:
                x1.append(line[0])
                y1.append(line[1])
                x2.append(line[2])
                y2.append(line[3])
                pt1 = (line[0],line[1])
                pt2 = (line[2],line[3])
                counter += 1
        else:
            self.station_name = [[0,0],[0,0]]
            self.market_table = [[0,0],[0,0]]
            return
        x1 = min(x1)
        y1 = min(y1)
        x2 = max(x2)
        y2 = max(y2)
        
        for pos in y_pos:
            if pos[0] < y1 and (pos[2]>(x1-0.02*imgwidth) and pos[2]<(x1+0.02*imgwidth)):
                y1_station = pos[0]
                y2_station = (pos[0]+pos[1])
                break

        #cv2.rectangle(img,(x1,y1_station),(x2,y2_station),(0,255,255),2)
        #cv2.rectangle(img,(x1, y1),(x2-int((x2-x1)*0.17), y2),(255,0,0),2)

        areas = [[0.0, 0.295],
                 [0.299, 0.368],
                 [0.370, 0.440],
                 [0.517, 0.605],
                 [0.607, 0.665],
                 [0.668, 0.756],
                 [0.758, 0.830]]

        new_areas = []
        x = x2 - x1

        for area in areas:
            new_areas.append([(area[0]*x + x1),
                              (area[1]*x + x1)])
          
        #for area in areas:
        #    cv2.rectangle(img,(int(area[0]*x + x1), int((y2-y1)*0.101+y1)), (int(area[1]*x +x1), int((y2-y1)*0.996+y1)), (0,255,255), 2)
            
        self.station_name = [[x1, y1_station],[x2, y2_station]]
        self.market_table = [[x1, int((y2-y1)*0.101+y1)],[x2,int((y2-y1)*0.996+y1)]]
        if x1 > 0 and x2 > x1 and y1_station > 0 and y2_station > y1_station and y1 > y2_station and y2 > y1:
            self.station_name = [[x1, y1_station],[x2, y2_station]]
            self.market_table = [[x1, int((y2-y1)*0.101+y1)],[x2,int((y2-y1)*0.996+y1)]]
            self.valid = True
        else:
            self.station_name = [[0,0],[0,0]]
            self.market_table = [[0,0],[0,0]]
        #small = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
        #cv2.imshow("xx", img)
        #cv2.waitKey(0)

class TesseractStation:
    def __init__(self, image, area):
        self.image = image
        self.result = self.readStationName(area)
        
    def readStationName(self, area):
        image = self.image
        h, w = image.shape
        factor = 1.0
        if int(w*100.0/h) == 160:
            #16:10 screen ratio
            factor = 2400.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
        else:
        #if int(w*100.0/h) == 177:
            #16:9 screen ratio and others
            factor = 2160.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
        result = self.ocr(image, area, factor)
        return result
        
    def ocr(self, image, area, factor):
        api = tesseract.TessBaseAPI()
        api.Init(".","big",tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
        h,w = image.shape
        w_step = w*image.dtype.itemsize
        iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
        cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
        tesseract.SetCvImage(iplimage,api)
        api.SetRectangle(int(area[0][0]*factor), int(area[0][1]*factor),
                         int(area[1][0]*factor)-int(area[0][0]*factor),
                         int(area[1][1]*factor)-int(area[0][1]*factor))
        res = self.hocrToObject(api.GetHOCRText(0), area, factor)
        return res
        
    def hocrToObject(self, input, area, factor):
        soup = BeautifulSoup(input)
        linelist = []
        for line in soup.findAll("span", { "class" : "ocr_line" }):
            wordlist = []
            not_empty = False
            newline = OCRline(line['title'], area, factor)
            for word in line.findAll("span", { "class" : "ocrx_word" }):
                if word.getText().strip() != '':
                    newline.addWord(OCRbox(word['title'], word.getText(), factor), True)
                    not_empty = True
            if not_empty:
                linelist.append(newline)
        return linelist

class TesseractStationMulti:
    def __init__(self, image, data):
        self.image = image
        self.result = self.cleanStationName(data)
        
    def cleanStationName(self, data):
        item = data.name
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        h, w = image.shape
        factor = 2400.0/h
        
        snippet = image[item.y1-1:item.y2+1, item.x1-1:item.x2+1]
        h, w = snippet.shape
        new_size = (int(w*factor), int(h*factor))
        snippet = cv2.resize(snippet, new_size, 0, 0, cv2.INTER_CUBIC)
        
        repeats = 5
        img = []
        for i in xrange(0,repeats):
            img.append(255 - contBright(snippet, 70.0+5*i, 255.0-10*i))
        
        fullimg = self.genNewImage(img)
        #cv2.imshow("xx", fullimg)
        #cv2.waitKey(0)
        results = self.hocrToList(self.ocr(fullimg))
        results.append(data.name.value)
        most_common = Counter(results).most_common()
        if len(most_common) > 0:
            if len(most_common) == 1:
                item.confidence = 1.0
            else:
                item.confidence = 0.5
            item.value = most_common[0][0]
            item.optional_values = self.sortAlternatives(most_common)

    def sortAlternatives(self, alt):
        sorted = []
        for tuple in alt:
            sorted.append(tuple[0])
        return sorted
    
    def genNewImage(self, img):
        h, w = img[0].shape
        vis = np.zeros((int(1.5*h*len(img))+20, int(1.5*w)+20), np.uint8)
        vis = 255 - vis
        currenty = 20
        currentx = 20
        for i in img:
            height, width = i.shape
            vis[currenty:currenty+height, currentx:currentx+width] = i
            currenty += height + 15
        return vis
    
    def ocr(self, image):
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
    
    def hocrToList(self, input, scale_factor=1):
        """Converts HOCR HTML data from Tesseract OCR into easily usable objects."""
        soup = BeautifulSoup(input)
        linelist = []
        for line in soup.findAll("span", { "class" : "ocr_line" }):
            wordlist = ""
            not_empty = False
            for word in line.findAll("span", { "class" : "ocrx_word" }):
                if word.getText().strip() != '':
                    new_word = word.getText()
                    wordlist += new_word +" "
                    not_empty = True
            if not_empty:
                linelist.append(wordlist.strip())
        return linelist
        
class TesseractMarket1:
    def __init__(self, image, area):
        self.image = image
        self.result = self.readMarketTable(area)
        
    def readMarketTable(self, area):
        image = self.image
        h, w = image.shape
        factor = 1.0
        if int(w*100.0/h) == 160:
            #16:10 screen ratio
            factor = 2400.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)
        else:
        #if int(w*100.0/h) == 177:
            #16:9 screen ratio and others
            factor = 2160.0/h
            new_size = (int(w*factor), int(h*factor))
            image = cv2.resize(image, new_size, 0, 0, cv2.INTER_CUBIC)

        result = self.ocr(image, area, factor)
        return result
        
    def ocr(self, image, area, factor):
        api = tesseract.TessBaseAPI()
        api.Init(".","big",tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
        h,w = image.shape
        w_step = w*image.dtype.itemsize
        iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
        cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
        tesseract.SetCvImage(iplimage,api)
        ocr_x2 = int((area[1][0]-int((area[1][0]-area[0][0])*0.17))*factor)
        api.SetRectangle(int(area[0][0]*factor), int(area[0][1]*factor),
                         ocr_x2-int(area[0][0]*factor),
                         int(area[1][1]*factor)-int(area[0][1]*factor)) 
        res = self.hocrToObject(api.GetHOCRText(0), area, factor)
        return res
        
    def hocrToObject(self, input, area, factor):
        soup = BeautifulSoup(input)
        linelist = []
        for line in soup.findAll("span", { "class" : "ocr_line" }):
            wordlist = []
            not_empty = False
            newline = OCRline(line['title'], area, factor)
            for word in line.findAll("span", { "class" : "ocrx_word" }):
                if word.getText().strip() != '':
                    newline.addWord(OCRbox(word['title'], word.getText(), factor))
                    not_empty = True
            if not_empty:
                linelist.append(newline)
        return linelist

class Levenshtein:
    def __init__(self, ocr_data, path):
        self.levels = ['LOW', 'MED', 'HIGH']
        try:
            file = open(path + "\\commodities.json", 'r')
            self.comm_list = json.loads(file.read())
            self.comm_list.sort(key = len)
        except:
            self.comm_list = ['BEER']
            
        self.result = self.cleanCommodities(ocr_data)
        
    def cleanCommodities(self, data):
        for i in xrange(len(data)):
            if not data[i][0] is None:
                mindist = 100
                topcomm = ""
                alternatives = []
                for comm in self.comm_list:
                    dist = distance(data[i][0].value, unicode(comm))
                    if dist < 5:
                        alternatives.append((unicode(comm), dist))
                    if dist < mindist:
                        mindist = dist
                        topcomm = comm
                    if dist == 0:
                        data[i][0].value = topcomm
                        data[i][0].confidence = 1.0
                        break
                        
                alternatives.sort(key=lambda x: x[1])
                optional_values = [j[0] for j in alternatives]
                
                maxdist = 4
                if len(data[i][0].value) < 5:
                    maxdist = 3

                if mindist < maxdist:
                    data[i][0].value = topcomm
                    data[i][0].confidence = 1.0
                    if mindist != 0:
                        data[i][0].optional_values = [data[i][0].value] + optional_values
                else:
                    data[i][0].confidence = 0.0
                    data[i][0].optional_values = [data[i][0].value] + optional_values
            # LOW MED HIGH
            if not data[i][4] is None:
                topratio = 0.0
                toplev = ""
                for lev in self.levels:
                    rat = ratio(data[i][4].value, unicode(lev))
                    if rat > topratio:
                        topratio = rat
                        toplev = lev
                data[i][4].value = toplev
            if not data[i][6] is None:
                topratio = 0.0
                toplev = ""
                for lev in self.levels:
                    rat = ratio(data[i][6].value, unicode(lev))
                    if rat > topratio:
                        topratio = rat
                        toplev = lev
                data[i][6].value = toplev

class NNMethod:
    def __init__(self, image, ocr_data, path):
        self.result = ocr_data
        param = {'app_path': path}
        train = nnTraining.Instance(param)
        assert isinstance(train, type(nnTraining))
        train.setClassifier('logistic')
        
        self.cleanNumbers(self.result, train, image)
        
    def cleanNumbers(self, data, train, image):
        for i in xrange(len(data)):
            for j in xrange(len(data[i].items)):
                if data[i][j] != None:
                    if j in [1, 2, 3,5]:
                        snippet = image[data[i][j].y1-2:data[i][j].y2+2,
                                        data[i][j].x1-2:data[i][j].x2+2]
                        snippet = cv2.cvtColor(snippet,cv2.COLOR_GRAY2RGB)
                        snippet = cv2.copyMakeBorder(snippet, 5, 5, 5, 5,cv2.BORDER_CONSTANT,value=(255,255,255)) 
                        res = train.doDigitPrediction(snippet)
                        try:
                            data[i][j].value = "{:,}".format(int(res))
                        except:
                            pass

class OCRline():
    """Class providing a recognised line of text as an object, 
       additionally embedding all recognised words in line as OCRBox 
       objects.
    """
    def __init__(self, bbox, area, factor):
        self.factor = factor
        coords = bbox.split()
        self.x1 = int(int(coords[1])/factor)
        self.y1 = int(int(coords[2])/factor)
        self.x2 = int(int(coords[3])/factor)
        self.y2 = int(int(coords[4].replace(';', ''))/factor)
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.areas_x = self.getXAreas(area)
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
    
    def __getitem__(self, key):
        return self.items[key]
    
    def getXAreas(self, points):
        areas = [[0.0, 0.295],
                 [0.299, 0.368],
                 [0.370, 0.440],
                 [0.517, 0.605],
                 [0.607, 0.665],
                 [0.668, 0.756],
                 [0.758, 0.830]]
        new_areas = []
        x = points[1][0] - points[0][0]
        for area in areas:
            new_areas.append([(area[0]*x + points[0][0]),
                              (area[1]*x + points[0][0])])
        return new_areas
        
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
            bbox = "bbox " + unicode(self.name.x1) + " " +\
                   unicode(self.name.y1) + " " + unicode(word.x2) +\
                   " " + unicode(word.y2)
            self.name = OCRbox(bbox, self.name.value+" "+word.value, 1.0)
    
    def __str__(self):
        return "OCRline: "+ unicode(self.items)
    
    def __repr__(self):
        return "OCRline: "+ unicode(self.items)
            
    
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, bbox, text, factor):
        coords = bbox.split()
        self.x1 = int(int(coords[1])/factor)
        self.y1 = int(int(coords[2])/factor)
        self.x2 = int(int(coords[3])/factor)
        self.y2 = int(int(coords[4].replace(';', ''))/factor)
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.value = text.strip()
        self.confidence = 1.0

        self.optional_values = []
        
    def __str__(self):
        return "OCRbox: "+ unicode(self.value)
    
    def __repr__(self):
        return "OCRbox: "+ unicode(self.value)
