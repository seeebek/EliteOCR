# -*- coding: utf-8 -*-
from __future__ import division
import os
import cv2
import numpy as np
from math import pi
from operator import itemgetter
from imageprocessing import contBright
import random


class OCRAreasFinder:
    def __init__(self, image):
        self.station_name = None
        self.market_table = None
        self.market_width = 0
        self.valid = False
        self.areas = None
        self.findMarket(image)
        
    def findMarket(self, input):
        img = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
        imgheight, imgwidth = img.shape
        
        ret,thresh1 = cv2.threshold(img,70,255,cv2.THRESH_BINARY)
        #small = cv2.resize(thresh1, (0,0), fx=0.5, fy=0.5) 
        lines = cv2.HoughLinesP(thresh1, 1, pi/2, 2, None, imgheight/2, 1)
        
        loi = self.getLinesOfInterest(lines)
        #print loi
        longestline = max(loi,key=itemgetter(2))
        self.market_width = longestline[2]
        
        #validate:
        self.validate(longestline, loi)

        x1 = longestline[0]
        y1 = longestline[1]-int(longestline[2]*0.6653)
        x2 = int((longestline[0]+longestline[2])*0.839)
        x2_station = longestline[0]+longestline[2]
        y2 = longestline[1]
        y1_station = longestline[1]-int(longestline[2]*0.7428)
        y2_station = longestline[1]-int(longestline[2]*0.72)
        
        self.areas = self.getAreas(x1, x2)
          
        if x1 > 0 and x2 > x1 and y1_station > 0 and y2_station > y1_station and y1 > y2_station and y2 > y1:
            self.station_name = [[x1, y1_station],[x2_station, y2_station]]
            self.market_table = [[x1, int((y2-y1)*0.101+y1)],[x2,int((y2-y1)*0.998+y1)]]
        else:
            self.station_name = None
            self.market_table = None
        
    
    def validate(self, longestline, loi):
        tolerance1 = [longestline[1]-int(0.98*longestline[2]*0.665306), longestline[1]-int(1.02*longestline[2]*0.665306)]
        tolerance2 = [longestline[1]-int(0.98*longestline[2]*0.600816), longestline[1]-int(1.02*longestline[2]*0.600816)]
        confirmed = [False,False]
        for line in loi:
            if line[1] < tolerance1[0] and line[1] > tolerance1[1]:
                if line[2] > longestline[2]*0.70:
                    confirmed[0] = True
            if line[1] < tolerance2[0] and line[1] > tolerance2[1]:
                if line[2] > longestline[2]*0.70:
                    confirmed[1] = True
        if all(item for item in confirmed):
            self.valid = True
    
    def getLinesOfInterest(self, lines):
        loi = []
        if not (lines is None):
            for line in lines[0]:
                loi.append((int(line[0]), int(line[1]), int(line[2])-int(line[0])))
        else:
            return []
        if len(loi) == 0:
            return[]
        return loi
    
    def getAreas(self, x1, x2):
        areas = [[0.0, 0.357],
                 [0.361, 0.444],
                 [0.448, 0.531],
                 [0.625, 0.731],
                 [0.732, 0.802],
                 [0.805, 0.912],
                 [0.913, 0.999]]

        new_areas = []
        x = x2 - x1

        for area in areas:
            new_areas.append([(area[0]*x),
                              (area[1]*x)])
        return new_areas
        
class MLP:
    def __init__(self, image, path, areas, isstation):
        #full old
        """
        layers = np.array([400,32,46])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "text.xml", "OCRMLP")
        self.classdict={0:"A",1:"B",2:"C",3:"D",4:"E",5:"F",6:"G",7:"H",8:"I",9:"J",10:"K",11:"L",12:"M",13:"N",14:"O",15:"P",16:"Q",17:"R",18:"S",19:"T",20:"U",21:"V",22:"W",23:"X",24:"Y",25:"Z",26:"Ä",27:"Ö",28:"Ü",29:"À",30:"É",31:"È",32:"Ê",33:"'",34:"-",35:".",36:"0",37:"1",38:"2",39:"3",40:"4",41:"5",42:"6",43:"7",44:"8",45:"9",}
        """
        #numbers
        self.numbers = TrainedDataNumbers(path)
        self.letters = TrainedDataLetters(path)
        """
        layers = np.array([400,36,12])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "numbers.xml", "OCRMLP")
        self.revclassdict = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,",":10,"-":11,}
        self.classdict = dict((v,k.decode("utf-8")) for k,v in self.revclassdict.iteritems())
        """
        self.result = []
        self.areas = areas
        self.ocrImage(image, isstation)

    def findLines(self, input):
        """ finds boundaries of text lines in the market table """
        rows, cols = input.shape
        lines = []
        first = 0
        last = 0
        blackflag = False
        firstflag = False
        
        start = cols
        end = 0
        
        whitecount = 0
        
        for i in xrange(rows):
            blackflag = False
            for j in xrange(cols):
                if input.item(i,j) < 250:
                    whitecount = 0
                    blackflag = True
                    if j < start :
                        start = j
                    if j > end:
                        end = j+1
                    if not firstflag:
                        first = i
                        firstflag = True
            
            if not blackflag:
                whitecount += 1
            
            if firstflag and not blackflag and whitecount > (rows/183):
                last = i+1 -whitecount
                firstflag = False
                lines.append([start, end, first, last])
                start = cols
                end = 0

        if firstflag and not blackflag and whitecount > (rows/183):
            last = rows - whitecount
            firstflag = False
            lines.append([start, end, first, last])
            start = cols
            end = 0
        
        #for line in lines:
        #    cv2.rectangle(input,(line[0],line[2]),(line[1],line[3]),(0,0,0),1)   
        #cv2.imshow("x", input)
        #cv2.waitKey(0)
        return lines
        
        
    def findBoxes(self, input, lines):
        """ searches single characters in the lines. creates bounding boxes for full 
            words and single charachters 
        """
        h, w = input.shape
        
        #cv2.imshow("x", input)
        #cv2.waitKey(0)
        
        boxes = []
        for line in lines:
            boxline = []
            charboxes = []
            first = 0
            last = 0
            blackflag = False
            firstflag = False
            firstcharflag = False
            
            whitecount = 0
            lastblack = 1000
            lastfirst = 0
            
            start = line[3]+2
            end = 0
            
            startchar = line[3]+2
            endchar = 0
            
            firstchar = 0
            
            j_to = line[3]+1
            #if line[3]+2 >= h:
            #    j_to = h-1
            i_to = line[1]+2
            #if line[1]+2 >= w:
            #    i_to = w-1
            
            for i in xrange(line[0]-2,i_to):
                blackflag = False
                for j in xrange(line[2]-2,j_to):
                    #print(j,i)
                    if input.item(j,i) < 250:
                        whitecount = 0
                        blackflag = True
                        if j < start :
                            start = j-1
                        if j < startchar :
                            startchar = j-1
                        if j > end:
                            end = j+1
                        if j > endchar:
                            endchar = j+1
                        if not firstflag:
                            first = i-1
                            firstflag = True
                        if not firstcharflag:
                            firstchar = i-1
                            firstcharflag = True

                
                if not blackflag:
                    whitecount += 1
                
                if firstcharflag and not blackflag:
                    last = i+1
                    charboxes.append([firstchar,last, startchar, endchar])
                    firstcharflag = False
                    startchar = line[3]+2
                    endchar = 0
                
                if firstflag and not blackflag and whitecount > (line[3] - line[2])/2.2:
                    h = line[3] - line[2]
                    last = i - whitecount + 1
                    whitecount = 0
                    firstflag = False
                    boxline.append({"line":line,"box":[first,last, start, end], "units":charboxes})
                    charboxes = []
                    start = line[3]+2
                    end = 0
                    
            if firstflag:
                last = i_to - whitecount
                whitecount = 0
                firstflag = False
                boxline.append({"line":line,"box":[first,last, start, end], "units":charboxes})
                charboxes = []

            boxes.append(boxline)
        
            #for box in boxline:
            #    cv2.rectangle(input,(box["box"][0],box["box"][2]),(box["box"][1],box["box"][3]),(0,0,0),1)   
            #    cv2.imshow("x", input)
            #    cv2.waitKey(0)
            #return boxes
        return boxes
    
    def mlpocr(self, input, box, type):
        """ performs OCR on a part of the image specified by box (full word) """
        restext = ""
        temp = []
        for letter in box["units"]:
            temp2 = []
            image = input[letter[2]:letter[3]+1,letter[0]:letter[1]]
            h = box["line"][3]-box["line"][2]
            if len(image) > 0:
                if (h/len(image[0])) > 3:
                    image = input[box["line"][2]:letter[3], letter[0]:letter[1]]
                    border = int((h - len(image[0]))/2)
                    image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))

                if len(image) < h/1.5:
                    image = input[box["line"][2]:box["line"][3], letter[0]:letter[1]]
                    border = int((h - len(image[0]))/2)
                    image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))
                #cv2.imwrite("test\\"+str(random.randint(1, 100000))+".png",image)
                
                image = cv2.resize(image, (20, 20))
                ret,image = cv2.threshold(image,250,255,cv2.THRESH_BINARY)
                
                
                rows, cols = image.shape
                for i in xrange(rows):
                    for j in xrange(cols):
                        if image.item(i,j) == 255:
                            temp2.append(1)
                        else:
                            temp2.append(0)
                temp.append(temp2)
        #print len(temp[0])
        #print len(temp)
        #for item in temp:
            #print len(item)
        if len(temp)>0:
            classdict = None
            data = np.array(temp, dtype='float32')
            if type == "numbers":
                resultclasses = -1 * np.ones((len(data),self.numbers.keys), dtype='float32')
                self.numbers.nnetwork.predict(data, resultclasses)
                classdict = self.numbers.classdict
            elif type == "letters":
                resultclasses = -1 * np.ones((len(data),self.letters.keys), dtype='float32')
                self.letters.nnetwork.predict(data, resultclasses)
                classdict = self.letters.classdict
            
            
            for k in range(len(resultclasses)):
                #print resultclasses[j]
                restext += classdict[np.argmax(resultclasses[k])].decode('utf-8')    
        return restext    

    def ocrImage(self, input, isstation):
        """ require grayscale market table only """
        
        tableheight, tablewidth = input.shape
        
        minh = int(round(tableheight/57.38))
        maxh = int(round(tableheight/46.96))

        lines = self.findLines(input)

        boxes = self.findBoxes(input, lines)
        
        result = ""
        for line in boxes:

            if len(line) > 0:
                if line[0]["line"][0] > tableheight/18:
                    newline = OCRLine(line[0]["line"], self.areas)
                    conf_mod = 1.0
                    lineheight = line[0]["line"][3]-line[0]["line"][2]
                    if lineheight > minh and lineheight < maxh:
                        conf_mod = 0.5
                    
                    for word in line:
                        self.areas
                        if word["box"][1] < self.areas[0][1]:
                            result = self.mlpocr(input, word, "letters")
                        elif word["box"][0] > self.areas[4][0] and word["box"][1] < self.areas[4][1]:
                            result = self.mlpocr(input, word, "letters")
                        elif word["box"][0] > self.areas[6][0] and word["box"][1] < self.areas[6][1]:
                            result = self.mlpocr(input, word, "letters")    
                        else:
                            result = self.mlpocr(input, word, "numbers")
                        
                        newline.addWord(OCRbox(word["box"], result, word["units"]), isstation)
                        
                    #print newline
                    self.result.append(newline)
        #print self.result
        
class OCRLine():
    """Class providing a recognised line of text as an object, 
       additionally embedding all recognised words in line as OCRBox 
       objects.
    """
    def __init__(self, coords, areas):
        self.x1 = coords[0]
        self.y1 = coords[2]
        self.x2 = coords[1]
        self.y2 = coords[3]
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.area = None
        self.areas_x = areas
        
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
        
    def addWord(self, word, station = False):
        if station:
            self.addName(word)
            self.items[0] = self.name
            return
            
        x1 = word.x1
        x2 = word.x2
        #for x in xrange(0, len(self.areas_x)):
        if x2 < self.areas_x[0][1]:
            self.addName(word)
            self.items[0] = self.name
            return
        if x1 > self.areas_x[1][0] and x2 < self.areas_x[1][1]:
            if self.sell is None:
                self.sell = word
            else:
                self.sell = self.addPart(self.sell, word)
            self.sell.value = self.sell.value.replace('.', ',')
            self.items[1] = self.sell
            return
        if x1 > self.areas_x[2][0] and x2 < self.areas_x[2][1]:
            if self.buy is None:
                self.buy = word
            else:
                self.buy = self.addPart(self.buy, word)
            self.buy.value = self.buy.value.replace('.', ',')
            self.items[2] = self.buy
            return
        if x1 > self.areas_x[3][0] and x2 < self.areas_x[3][1]:
            if self.demand_num is None:
                self.demand_num = word
            else:
                self.demand_num = self.addPart(self.demand_num, word)
            self.demand_num.value = self.demand_num.value.replace('.', ',')
            self.items[3] = self.demand_num
            return
        if x1 > self.areas_x[4][0] and x2 < self.areas_x[4][1]:
            self.demand = word
            self.items[4] = self.demand
            return
        if x1 > self.areas_x[5][0] and x2 < self.areas_x[5][1]:
            if self.supply_num is None:
                self.supply_num = word
            else:
                self.supply_num = self.addPart(self.supply_num, word)
            self.supply_num.value = self.supply_num.value.replace('.', ',')
            self.items[5] = self.supply_num
            return
        if x1 > self.areas_x[6][0] and x2 < self.areas_x[6][1]:
            self.supply = word
            self.items[6] = self.supply
            return
        
    def addPart(self, word, to_add):
        coords = [word.x1, to_add.x2, word.y1, to_add.y2]
        units = word.units + to_add.units
        new_word = OCRbox(coords, word.value + "" + to_add.value, units)
        
        return new_word
        
    def addName(self, word):
        if self.name == None:
            self.name = word
            self.name.addBox()
        else:
            temp = self.name
            coords = [self.name.x1, word.x2, self.name.y1, word.y2]
            units = self.name.units + word.units
            self.name = OCRbox(coords, self.name.value+" "+word.value, units)
            self.name.addBox(temp.boxes + [word.box])
    
    def __str__(self):
        return "OCRline: "+ unicode(self.items)
    
    def __repr__(self):
        return "OCRline: "+ unicode(self.items)
        
        
        
class OCRbox():
    """ Class providing recognised words as objects """
    def __init__(self, coords, text, units):
        self.x1 = coords[0]
        self.y1 = coords[2]
        self.x2 = coords[1]
        self.y2 = coords[3]
        self.units = units
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.box = [self.x1, self.y1, self.x2, self.y2]
        self.boxes = []
        self.value = text.strip()
        
    def __str__(self):
        return "OCRbox: "+ unicode(self.value)
    
    def __repr__(self):
        return "OCRbox: "+ unicode(self.value)
    
    def addBox(self, box = None):
        if not box is None:
            self.boxes = box
        else:
            self.boxes.append(self.box)
        
class TrainedDataNumbers():
    def __init__(self, path):
        self.revclassdict = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,",":10,"-":11,}
        self.keys = len(self.revclassdict)
        layers = np.array([400,36,self.keys])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "numbers.xml", "OCRMLP")
        self.classdict = dict((v,k.decode("utf-8")) for k,v in self.revclassdict.iteritems())
        
        
class TrainedDataLetters():
    def __init__(self, path):
        self.revclassdict = {"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25,"-":26,".":27}
        self.keys = len(self.revclassdict)
        layers = np.array([400,36,self.keys])
        self.nnetwork = cv2.ANN_MLP(layers, 1,0.6,1)
        self.nnetwork.load(path + os.sep + "letters.xml", "OCRMLP")
        self.classdict = dict((v,k.decode("utf-8")) for k,v in self.revclassdict.iteritems())
        
        
        
        
        
        
        
        
        
        
        
        