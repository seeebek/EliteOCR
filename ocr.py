import cv2
import cv2.cv as cv
import tesseract
from bs4 import BeautifulSoup

def intR(input):
    return int(round(input))

def hocrToObject(input, width):
    """ Converts HOCR HTML data from Tesseract OCR into easily usable objects.
    """
    soup = BeautifulSoup(input)
    linelist = []
    for line in soup.findAll("span", { "class" : "ocr_line" }):
        wordlist = []
        not_empty = False
        newline = OCRline(line['title'], width)
        for word in line.findAll("span", { "class" : "ocrx_word" }):
            if word.getText().strip() != '':
                newline.addWord(OCRbox(word['title'], word.getText()))
                not_empty = True
        if not_empty:
            linelist.append(newline)
    return linelist
    
def ocr(image, return_type):
    """ Sets up OCR settings and runs OCR on provided image """
    h,w = image.shape

    api = tesseract.TessBaseAPI()
    if w < 1600:
        api.Init(".","small",tesseract.OEM_DEFAULT)
    else:
        api.Init(".","big",tesseract.OEM_DEFAULT)
    api.SetPageSegMode(tesseract.PSM_AUTO)

    w_step = w*image.dtype.itemsize
     
    iplimage = cv.CreateImageHeader((w,h), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, image.tostring(),image.dtype.itemsize * (w))
    tesseract.SetCvImage(iplimage,api)
    if return_type == "UTF8":
        return api.GetUTF8Text()
    else:
        return hocrToObject(api.GetHOCRText(0), w)
        
class OCRline():
    """ Class providing a recognised line of text as an object, 
    additionally embedding all recognised words as OCRBox objects.
    """
    def __init__(self, bbox, width):
        coords = bbox.split()
        self.x1 = int(coords[1])
        self.y1 = int(coords[2])
        self.x2 = int(coords[3])
        self.y2 = int(coords[4].replace(';', ''))
        self.w = int(coords[3]) - int(coords[1])
        self.h = int(coords[4].replace(';', '')) - int(coords[2])
        self.areas_x = [[0, intR(0.3204*width)],
                        [intR(0.3357*width), intR(0.4289*width)],
                        [intR(0.4341*width), intR(0.5064*width)],
                        [intR(0.6072*width), intR(0.7080*width)],
                        [intR(0.7231*width), intR(0.7829*width)],
                        [intR(0.7901*width), intR(0.9147*width)],
                        [intR(0.9298*width), width]]
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
                self.items[1] = self.sell
                break
            if x1 > self.areas_x[2][0] and x2 < self.areas_x[2][1]:
                if word.value == "-":
                    self.buy = None
                else:
                    self.buy = word
                    self.items[2] = self.buy
                break
            if x1 > self.areas_x[3][0] and x2 < self.areas_x[3][1]:
                self.demand_num = word
                self.items[3] = self.demand_num
                break
            if x1 > self.areas_x[4][0] and x2 < self.areas_x[4][1]:
                self.demand = word
                self.items[4] = self.demand
                break
            if x1 > self.areas_x[5][0] and x2 < self.areas_x[5][1]:
                self.supply_num = word
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
            self.name = OCRbox(bbox, self.name.value+" "+word.value)
    
    def __str__(self):
        return "OCRline: "+ self.name.value
    
    def __repr__(self):
        return "OCRbox: "+ self.name.value
            
    
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, bbox, text):
        coords = bbox.split()
        self.x1 = int(coords[1])
        self.y1 = int(coords[2])
        self.x2 = int(coords[3])
        self.y2 = int(coords[4].replace(';', ''))
        self.w = int(coords[3]) - int(coords[1])
        self.h = int(coords[4].replace(';', '')) - int(coords[2])
        self.value = text.strip()
        
    def __str__(self):
        return "OCRbox: "+ self.value
    
    def __repr__(self):
        return "OCRbox: "+ self.value