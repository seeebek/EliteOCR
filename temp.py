import cv2
import cv2.cv as cv
import numpy as np
import tesseract
from bs4 import BeautifulSoup
from PyQt4.QtCore import QSettings

def getXAreas(w):
    settings = QSettings('seeebek', 'eliteOCR')
    cal_points = settings.value('cal_points', type=float)
    areas = [[0.0, 0.297],
             [0.300, 0.370],
             [0.373, 0.442],
             [0.520, 0.607],
             [0.609, 0.665],
             [0.670, 0.758],
             [0.760, 0.832]]
    new_areas = []
    x = cal_points[6] - cal_points[4]
    for area in areas:
        new_areas.append([(area[0]*x + cal_points[4])*w,
                          (area[1]*x + cal_points[4])*w])
    return new_areas

def intR(input):
    return int(round(input))
    
def secondRun(image, lines, offset):
    current = 0
    snippets = []
    current_snippet = 0
    for line in lines:
        newline = []
        for item in line.items:
            if item != None:
                snippet = image[item.y1-1:item.y2+1,
                                      item.x1-1:item.x2+1]
                cv2.imwrite('snippets/'+str(current)+'.png',snippet)
                newline.append(snippet)
                current += 1
        snippets.append(newline)
        
    
    vis = np.zeros((5000, 5000), np.uint8)
    vis = (255 - vis)

    currenty = 10
    currentx = 10
    for line in snippets:
        for item in line:
            height, width = item.shape
            vis[currenty:currenty+height, currentx:currentx+width] = item
            currentx = currentx+width+offset
        currentx = 10
        currenty += 40
        
    cv2.imwrite('snippets/ready.png',vis)
    
    api = tesseract.TessBaseAPI()
    api.Init(".","big",tesseract.OEM_DEFAULT)
    api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
    h,w = vis.shape
    w_step = w*vis.dtype.itemsize
     
    iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, vis.tostring(),vis.dtype.itemsize * (w))
    tesseract.SetCvImage(iplimage,api)
    #settings = QSettings('seeebek', 'eliteOCR')
    #cal_points = settings.value('cal_points', type=float)
    res = api.GetUTF8Text()
    print res.strip()

def multirun(image, lines):
    for i in range(1):
        secondRun(image, lines, 5*i+10)
    
def hocrToObject(input, width, scale_factor):
    """ Converts HOCR HTML data from Tesseract OCR into easily usable objects.
    """
    soup = BeautifulSoup(input)
    linelist = []
    for line in soup.findAll("span", { "class" : "ocr_line" }):
        wordlist = []
        not_empty = False
        newline = OCRline(line['title'], width, scale_factor)
        for word in line.findAll("span", { "class" : "ocrx_word" }):
            if word.getText().strip() != '':
                newline.addWord(OCRbox(word['title'], word.getText(), scale_factor))
                not_empty = True
        if not_empty:
            linelist.append(newline)
    return linelist

def ocr(image):
    pass
    
def ocrx(image, return_type):
    """ Sets up OCR settings and runs OCR on provided image """
    scale_factor = 1
    h,w = image.shape
    if h < 2160:
        image = cv2.resize(image, (0,0), 2, 2, cv2.INTER_CUBIC)
        h, w = image.shape
        scale_factor = 2
    api = tesseract.TessBaseAPI()
    api.Init(".","big",tesseract.OEM_DEFAULT)
    api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)

    w_step = w*image.dtype.itemsize
     
    iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
    tesseract.SetCvImage(iplimage,api)
    settings = QSettings('seeebek', 'eliteOCR')
    cal_points = settings.value('cal_points', type=float)
    if return_type == "UTF8":
        api.SetRectangle(int(cal_points[0]*w), int(cal_points[1]*h), int((cal_points[6]-cal_points[0])*w), int((cal_points[3]-cal_points[1])*h))
        res = hocrToObject(api.GetHOCRText(0), w, scale_factor)
        return res
    else:
        api.SetRectangle(int(cal_points[4]*w), int(cal_points[5]*h), int((cal_points[6]-cal_points[4])*w), int((cal_points[7]-cal_points[5])*h))
        first_result = hocrToObject(api.GetHOCRText(0), w, scale_factor)
        second_run = multirun(image, first_result)
        
        return first_result
        
class OCRline():
    """ Class providing a recognised line of text as an object, 
    additionally embedding all recognised words as OCRBox objects.
    """
    def __init__(self, bbox, width, scale_factor):
        self.scale_factor = scale_factor
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
        
    def addWord(self, word):
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
            self.name = OCRbox(bbox, self.name.value+" "+word.value, self.scale_factor)
    
    def __str__(self):
        return "OCRline: "+ str(self.name.value)
    
    def __repr__(self):
        return "OCRbox: "+ str(self.name.value)
            
    
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, bbox, text, scale_factor):
        self.scale_factor = scale_factor
        coords = bbox.split()
        self.x1 = int(coords[1])
        self.y1 = int(coords[2])
        self.x2 = int(coords[3])
        self.y2 = int(coords[4].replace(';', ''))
        self.w = int(coords[3]) - int(coords[1])
        self.h = int(coords[4].replace(';', '')) - int(coords[2])
        self.value = text.strip()
        
    def __str__(self):
        return "OCRbox: "+ str(self.value)
    
    def __repr__(self):
        return "OCRbox: "+ str(self.value)