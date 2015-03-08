# -*- coding: utf-8 -*-
import os
import cv2
import math
import tesseract
import json
import codecs
import numpy as np
import cv2.cv as cv
from imageprocessing import *
from bs4 import BeautifulSoup
from nn_scripts.nn_training import nnTraining
from Levenshtein import ratio, distance
from collections import Counter
from operator import itemgetter

class OCRAreasFinder:
    def __init__(self, image):
        self.station_name = None
        self.market_table = None
        self.market_width = 0
        self.valid = False
        self.hud_color = 0
        self.findAreas(image)
        
    def findAreas(self, image):
        img = image
        imgheight, imgwidth, xcolor = img.shape
        b,g,r  = cv2.split(img)
        r = np.add(r, 0.0)
        new = np.absolute(np.subtract(r, b))
        del b,r
        new = np.subtract(np.add(new,g), 128.0)
        del g
        value = np.clip(new, 0, 255)
        del new
        value = value.astype(np.uint8)
        h, w = value.shape
        ret,thresh1 = cv2.threshold(255 - value,160,255,cv2.THRESH_BINARY)
        #cv2.imshow("xx", thresh1)
        #cv2.waitKey(0)
        lines = cv2.HoughLinesP((255 - thresh1), 1, math.pi/2, 2, None, h/2, 1)
        loi = []
        if not (lines is None):
            for line in lines[0]:
                loi.append((int(line[0]), int(line[1]), int(line[2])-int(line[0])))
        else:
            self.station_name = [[0,0],[0,0]]
            self.market_table = [[0,0],[0,0]]
            return
        if len(loi) == 0:
            self.station_name = [[0,0],[0,0]]
            self.market_table = [[0,0],[0,0]]
            return
        
        longestline = max(loi,key=itemgetter(2))
        self.market_width = longestline[2]
        #print "start: " + str(longestline)
        
        self.hud_color = self.getHUD(longestline, img)
        
        #validate:
        tolerance1 = [longestline[1]-int(0.98*longestline[2]*0.665306), longestline[1]-int(1.02*longestline[2]*0.665306)]
        tolerance2 = [longestline[1]-int(0.98*longestline[2]*0.600816), longestline[1]-int(1.02*longestline[2]*0.600816)]
        confirmed = [False,False]
        for line in loi:
            if line[1] < tolerance1[0] and line[1] > tolerance1[1]:
                if line[2] > longestline[2]*0.70:
                    #print "one"
                    confirmed[0] = True
            if line[1] < tolerance2[0] and line[1] > tolerance2[1]:
                if line[2] > longestline[2]*0.70:
                    #print "two"
                    confirmed[1] = True
        if all(item for item in confirmed):
            self.valid = True
                
        
        x1 = longestline[0]
        y1 = longestline[1]-int(longestline[2]*0.6653)
        x2 = longestline[0]+longestline[2]
        y2 = longestline[1]
        y1_station = longestline[1]-int(longestline[2]*0.7428)
        y2_station = longestline[1]-int(longestline[2]*0.72)
        

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
        #    cv2.rectangle(img,(int(area[0]*x + x1), int((y2-y1)*0.101+y1)), (int(area[1]*x +x1), int((y2-y1)*0.996+y1)), (0,255,255), 1)
            
        self.station_name = [[x1, y1_station],[x2, y2_station]]
        self.market_table = [[x1, int((y2-y1)*0.101+y1)],[x2,int((y2-y1)*0.996+y1)]]
        if x1 > 0 and x2 > x1 and y1_station > 0 and y2_station > y1_station and y1 > y2_station and y2 > y1:
            self.station_name = [[x1, y1_station],[x2, y2_station]]
            self.market_table = [[x1, int((y2-y1)*0.101+y1)],[x2,int((y2-y1)*0.996+y1)]]
            #self.valid = True
        else:
            self.station_name = [[0,0],[0,0]]
            self.market_table = [[0,0],[0,0]]
        #small = cv2.resize(img, (0,0), fx=0.5, fy=0.5) 
        #cv2.imshow("xx", img)
        #cv2.waitKey(0)
        
    def getHUD(self, line, img):
        colors = [[10,105,245], #standard orange
                  [245,105, 10]] # blue
        candidates = [list(img[line[1]-1, line[0]+(line[2]/2)]),
                      list(img[line[1],   line[0]+(line[2]/2)]),
                      list(img[line[1]+1, line[0]+(line[2]/2)])]
        color_found = False
        for i in range(len(colors)):
            first = False
            second = False
            third = False
            for c in candidates:
                first = colors[i][0]-10 <= c[0] <= colors[i][0]+10
                second = colors[i][1]-10 <= c[1] <= colors[i][1]+10
                third = colors[i][2]-10 <= c[2] <= colors[i][2]+10
                if first and second and third:
                    color_found = True
                    #print i
                    return i
        return 0
                
            

class TesseractStation:
    def __init__(self, image, area, path):
        self.path = path.decode('windows-1252')
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
        api.Init(self.path.encode('windows-1252'), "big", tesseract.OEM_DEFAULT)
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
                    newline.addWord(OCRbox(word['title'], word.getText(), area, factor), True)
                    not_empty = True
            if not_empty:
                linelist.append(newline)
        return linelist

class TesseractStationMLP:
    def __init__(self, image, ocr_data, path):
        self.ocr_data = ocr_data
        layers = np.array([400,32,46])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "text.xml", "OCRMLP")
        self.classdict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"Ä",27:"Ö",28:"Ü",29:"À",30:"É",31:"È",32:"Ê",33:"'",34:"-",35:".",36:"0",37:"1",38:"2",39:"3",40:"4",41:"5",42:"6",43:"7",44:"8",45:"9",}
        #try:
        self.ocrSnippets(self.ocr_data, image)
        #except:
        #    self.ocr_data.name.confidence = 0.5
        
    def ocrSnippets(self, ocr_data, image):
        if ocr_data.name != None:
            restext = ""
            for box in ocr_data.name.boxes:
                snippet = image[box[1]-5:box[3]+5, box[0]-5:box[2]+5]
                characters = self.split(snippet)
                ar = self.toArray(characters)
                
                data = np.array(ar, dtype='float32')
                resultclasses = -1 * np.ones((len(data),46), dtype='float32')
                self.nnetwork.predict(data, resultclasses)
                
                for j in range(len(resultclasses)):
                    restext += self.classdict[np.argmax(resultclasses[j])].decode('utf-8')
                restext += " "
            #print ocr_data.name.value
            #print restext.strip()
            #print
            ocr_data.name.value = restext.strip()
            ocr_data.name.confidence = 1.0
                
    
    def toArray(self, images):
        array = []
        for image in images:
            temp = []
            image = cv2.resize(image, (20, 20))
            ret,image = cv2.threshold(image,140,255,cv2.THRESH_BINARY)
            #print image
            for row in image:
                for cell in row:
                    if cell == 255:
                        temp.append(1)
                    else:
                        temp.append(0)
            array.append(temp)
        return array
    
    def split(self, image):
        characters = []
        x1 = 0
        x2 = 0
        symbol = 0
        blackflag = False
        start = False
        image = cv2.resize(image, (0,0), fx=2, fy=2)
        image = contBright(image, 70.0, 200.0)
        
        h, w = image.shape
        for i in range(len(image[0])):
            blackflag = False
            for j in range(len(image)):
                if image[j][i] < 150:
                    blackflag = True
                    break
            if blackflag and (not start):
                x1 = i
                start = True 
            if (not blackflag) and start:
                x2 = i
                start = False
                snippet, point = self.topbottom(image[0:len(image), x1:x2], h)
                ret,snippet = cv2.threshold(snippet,200,255,cv2.THRESH_BINARY)
                characters.append(snippet)
        return characters
                
    def topbottom(self, input, h):
        first = 0
        last = 0
        blackflag = False
        firstflag = False
        point = False
        for i in range(len(input)):
            blackflag = False
            for j in range(len(input[0])):
                if input[i][j] < 200:
                    if not firstflag:
                        first = i
                        firstflag = True
                    last = i
        res = input[first:last, 0:len(input[0])]
        if first > (0.55*len(input)) and last>=len(input)-14:
            point = True
        if len(res)<((h-20)/2) or ((h-20)*1.0)/len(res[0]) > 4.5:
            res = input[10:len(input)-10, 0:len(input[0])]
            border = ((h-20) - len(res[0]))/2
            res = cv2.copyMakeBorder(res,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))
        return res, point
        
class TesseractMarket1:
    def __init__(self, parent, image, area, path, language = "big"):
        self.path = path.decode('windows-1252')
        self.lang = language
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
        #print self.lang
        if self.lang == "big" or self.lang == "eng":
            api.Init(self.path.encode('windows-1252'),"big",tesseract.OEM_DEFAULT)
        else:
            api.Init(self.path.encode('windows-1252'), str(self.lang), tesseract.OEM_DEFAULT)
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
        res = self.hocrToObject(api.GetHOCRText(0).decode('utf-8'), area, factor)
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
                    newline.addWord(OCRbox(word['title'], word.getText(), area, factor))
                    not_empty = True
            if not_empty:
                linelist.append(newline)
        return linelist

class Levenshtein:
    def __init__(self, ocr_data, path, language = "big"):
        if language == "big":
            self.lang = u"eng"
        else:
            self.lang = unicode(language)
        
        self.levels = {u"eng": [u'LOW', u'MED', u'HIGH'],
                       u"deu": [u'NIEDRIG', u'MITTEL', u'HOCH'], 
                       u"fra": [u'FAIBLE', u'MOYEN', u'ÉLEVÉ']}
        file = codecs.open(path + os.sep + "commodities.json", 'r', "utf-8")
        self.comm_list = json.loads(file.read())
        file.close()
        #print self.comm_list
        #self.comm_list.sort(key = len)
        if language == "big" or language == "eng":
            self.comm_list = [k for k, v in self.comm_list.iteritems()]
        else:
            self.comm_list = [v[self.lang] for k, v in self.comm_list.iteritems()]

        self.result = self.cleanCommodities(ocr_data)
        
    def cleanCommodities(self, data):
        for i in xrange(len(data)):
            if not data[i][0] is None:
                mindist = 100
                topcomm = ""
                alternatives = []
                for comm in self.comm_list:
                    dist = distance(data[i][0].value, unicode(comm))
                    if dist < 7:
                        alternatives.append((unicode(comm), dist))
                    if dist < mindist:
                        mindist = dist
                        topcomm = comm
                    if dist == 0:
                        data[i][0].value = topcomm
                        data[i][0].confidence = 1.0
                        break
                #print unicode(data[i][0].value)
                #print topcomm
                #print
                alternatives.sort(key=lambda x: x[1])
                optional_values = [j[0] for j in alternatives]
                
                maxdist = 4
                if len(data[i][0].value) < 5:
                    maxdist = 3

                if mindist < maxdist:
                    data[i][0].value = topcomm
                    if mindist < 2:
                        data[i][0].confidence = 1.0
                    else:
                        data[i][0].confidence = 0.7
                    if mindist != 0:
                        data[i][0].optional_values = [data[i][0].value] + optional_values
                else:
                    data[i][0].confidence = 0.0
                    data[i][0].optional_values = [data[i][0].value] + optional_values
            # LOW MED HIGH
            if not data[i][4] is None:
                topratio = 0.0
                toplev = ""
                for lev in self.levels[self.lang]:
                    rat = ratio(data[i][4].value, unicode(lev))
                    if rat > topratio:
                        topratio = rat
                        toplev = lev
                data[i][4].value = toplev
            if not data[i][6] is None:
                topratio = 0.0
                toplev = ""
                for lev in self.levels[self.lang]:
                    rat = ratio(data[i][6].value, unicode(lev))
                    if rat > topratio:
                        topratio = rat
                        toplev = lev
                data[i][6].value = toplev

class MLPMethod:
    def __init__(self, parent, image, ocr_data, path):
        self.ocr_data = ocr_data
        layers = np.array([400,32,46])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "text.xml", "OCRMLP")
        self.classdict = {0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"Ä",27:"Ö",28:"Ü",29:"À",30:"É",31:"È",32:"Ê",33:"'",34:"-",35:".",36:"0",37:"1",38:"2",39:"3",40:"4",41:"5",42:"6",43:"7",44:"8",45:"9",}
        self.ocrSnippets(parent, self.ocr_data, image)
        
    def ocrSnippets(self, parent, ocr_data, image):
        for i in xrange(len(ocr_data)):
            if ocr_data[i].name != None:
                restext = ""
                try:
                    for box in ocr_data[i].name.boxes:
                        snippet = image[box[1]-5:box[3]+5, box[0]-5:box[2]+5]
                        characters = self.split(snippet)
                        ar = self.toArray(characters)
                        
                        data = np.array(ar, dtype='float32')
                        resultclasses = -1 * np.ones((len(data),46), dtype='float32')
                        self.nnetwork.predict(data, resultclasses)
                        
                        for j in range(len(resultclasses)):
                            restext += self.classdict[np.argmax(resultclasses[j])].decode('utf-8')
                        restext += " "
                    #print ocr_data[i].name.value
                    #print restext
                    #print
                    ocr_data[i].name.value = restext.strip()
                except:
                    ocr_data[i].name.confidence = 0.5
    
    def toArray(self, images):
        array = []
        for image in images:
            temp = []
            image = cv2.resize(image, (20, 20))
            ret,image = cv2.threshold(image,140,255,cv2.THRESH_BINARY)
            #print image
            for row in image:
                for cell in row:
                    if cell == 255:
                        temp.append(1)
                    else:
                        temp.append(0)
            array.append(temp)
        return array
    
    def split(self, image):
        characters = []
        x1 = 0
        x2 = 0
        symbol = 0
        blackflag = False
        start = False
        image = cv2.resize(image, (0,0), fx=2, fy=2)
        image = contBright(image, 70.0, 200.0)
        
        h, w = image.shape
        for i in range(len(image[0])):
            blackflag = False
            for j in range(len(image)):
                if image[j][i] < 150:
                    blackflag = True
                    break
            if blackflag and (not start):
                x1 = i
                start = True 
            if (not blackflag) and start:
                x2 = i
                start = False
                snippet, point = self.topbottom(image[0:len(image), x1:x2], h)
                ret,snippet = cv2.threshold(snippet,200,255,cv2.THRESH_BINARY)
                characters.append(snippet)
        return characters
                
    def topbottom(self, input, h):
        first = 0
        last = 0
        blackflag = False
        firstflag = False
        point = False
        for i in range(len(input)):
            blackflag = False
            for j in range(len(input[0])):
                if input[i][j] < 200:
                    if not firstflag:
                        first = i
                        firstflag = True
                    last = i
        res = input[first:last, 0:len(input[0])]
        if first > (0.55*len(input)) and last>=len(input)-14:
            point = True
        if len(res)<((h-20)/2) or ((h-20)*1.0)/len(res[0]) > 4.5:
            res = input[10:len(input)-10, 0:len(input[0])]
            border = ((h-20) - len(res[0]))/2
            res = cv2.copyMakeBorder(res,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))
        return res, point
                
class NNMethod:
    def __init__(self, parent, image, ocr_data, path):
        self.result = ocr_data
        param = {'app_path': path}
        train = nnTraining.Instance(param)
        assert isinstance(train, type(nnTraining))
        train.setClassifier('logistic')
        
        self.cleanNumbers(parent, self.result, train, image)
        
    def cleanNumbers(self, parent, data, train, image):
        try:
            step = 10.0/len(data)
        except:
            step = 10.0
        for i in xrange(len(data)):
            if not parent is None:
                parent.progress_bar.setValue(50+int(i*step))
            else:
                sys.stdout.write("\r[=====")
                for s in range(5):
                    if i > (len(data)/5)*s:
                        sys.stdout.write("=")
                    else:
                        sys.stdout.write(" ")
                sys.stdout.write("]")
                sys.stdout.flush()
            for j in xrange(len(data[i].items)):
                if data[i][j] != None:
                    if j in [1, 2, 3, 5]:
                        snippet = image[data[i][j].y1-2:data[i][j].y2+2,
                                        data[i][j].x1-2:data[i][j].x2+2]
                        snippet = cv2.cvtColor(snippet,cv2.COLOR_GRAY2RGB)
                        h, w, c = snippet.shape
                        factor = data[i].factor
                        pad = int(4*factor)
                        new_size = (int(w*factor), int(h*factor))
                        snippet = cv2.resize(snippet, new_size, 0, 0, cv2.INTER_CUBIC)
                        snippet = cv2.copyMakeBorder(snippet, pad, pad, pad, pad,cv2.BORDER_CONSTANT,value=(255,255,255)) 
                        res, errorflag = train.doDigitPrediction(snippet)

                        if len(data[i][j].value.replace(".","").replace(",","")) != len(str(res)):
                            data[i][j].confidence = 0.7
                        if errorflag:
                            data[i][j].confidence = 0.0
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
        self.area = area
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
                if self.sell is None:
                    self.sell = word
                else:
                    self.sell = self.addPart(self.sell, word)
                self.sell.value = self.sell.value.replace('.', ',')
                self.items[1] = self.sell
                break
            if x1 > self.areas_x[2][0] and x2 < self.areas_x[2][1]:
                if word.value == "-":
                    self.buy = None
                else:
                    if self.buy is None:
                        self.buy = word
                    else:
                        self.buy = self.addPart(self.buy, word)
                    self.buy.value = self.buy.value.replace('.', ',')
                    self.items[2] = self.buy
                break
            if x1 > self.areas_x[3][0] and x2 < self.areas_x[3][1]:
                if self.demand_num is None:
                    self.demand_num = word
                else:
                    self.demand_num = self.addPart(self.demand_num, word)
                self.demand_num.value = self.demand_num.value.replace('.', ',')
                self.items[3] = self.demand_num
                break
            if x1 > self.areas_x[4][0] and x2 < self.areas_x[4][1]:
                self.demand = word
                self.items[4] = self.demand
                break
            if x1 > self.areas_x[5][0] and x2 < self.areas_x[5][1]:
                if self.supply_num is None:
                    self.supply_num = word
                else:
                    self.supply_num = self.addPart(self.supply_num, word)
                self.supply_num.value = self.supply_num.value.replace('.', ',')
                self.items[5] = self.supply_num
                break
            if x1 > self.areas_x[6][0] and x2 < self.areas_x[6][1]:
                self.supply = word
                self.items[6] = self.supply
                break
        
    def addPart(self, word, to_add):
        bbox = "bbox " + unicode(word.x1) + " " + unicode(word.y1) + " " + unicode(to_add.x2) +\
               " " + unicode(to_add.y2)
        new_word = OCRbox(bbox, word.value + "" + to_add.value, self.area, 1.0)
        
        return new_word
        
    def addName(self, word):
        if self.name == None:
            self.name = word
            self.name.addBox()
        else:
            temp = self.name
            bbox = "bbox " + unicode(self.name.x1) + " " +\
                   unicode(self.name.y1) + " " + unicode(word.x2) +\
                   " " + unicode(word.y2)
            self.name = OCRbox(bbox, self.name.value+" "+word.value, self.area, 1.0)
            #print temp.boxes
            self.name.addBox(temp.boxes + [word.box])
    
    def __str__(self):
        return "OCRline: "+ unicode(self.items)
    
    def __repr__(self):
        return "OCRline: "+ unicode(self.items)
            
    
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, bbox, text, area, factor):
        coords = bbox.split()
        self.x1 = int(int(coords[1])/factor)
        self.y1 = int(int(coords[2])/factor)
        self.x2 = int(int(coords[3])/factor)
        self.y2 = int(int(coords[4].replace(';', ''))/factor)
        self.box = [self.x1, self.y1, self.x2, self.y2]
        self.boxes = []
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.value = text.strip()
        
        self.confidence = self.calculateConfidence(area, self.h)

        self.optional_values = []
        
    def __str__(self):
        return "OCRbox: "+ unicode(self.value)
    
    def __repr__(self):
        return "OCRbox: "+ unicode(self.value)
    
    def addBox(self, box = None):
        if not box is None:
            self.boxes = box
        else:
            self.boxes.append(self.box)
        
    def calculateConfidence(self, area, height):
        area_h = area[1][1]-area[0][1]
        allowed_h = (int(0.7*(area_h/48)), int(1.3*(area_h/48)))
        if height>=allowed_h[0] and height<=allowed_h[1]:
            return 1.0
        else:
            return 0.5
