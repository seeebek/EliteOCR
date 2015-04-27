# -*- coding: utf-8 -*-
import sys
import gzip
import cv2
import random
import numpy as np
from os import remove
from os.path import split
from functools import partial
from qimage2ndarray import array2qimage
from bitarray import bitarray

from PyQt4.QtGui import QWizard, QFileDialog, QListWidgetItem, QGraphicsScene, QPen, QPixmap, QMovie
from PyQt4.QtCore import Qt, QObject, SIGNAL, QSize

from learningUI import Ui_Wizard
from settings import Settings
from ocr import OCR
from customqlistwidgetitem import CustomQListWidgetItem
from trainer import Trainer

try:
   import cPickle as pickle
except:
   import pickle

class LearningWizard(QWizard, Ui_Wizard):
    def __init__(self, settings):
        QWizard.__init__(self)
        self.setupUi(self)
        self.settings = settings
        self.wizardPage3.pageCreated.connect(self.showSummary)
        self.wizardPage3.fullfilled = True

        self.wizardPage2.fullfilled = True
        self.errors = 0
        self.steps = 0
        self.delete_images_button.clicked.connect(self.deleteUserImages)
        self.add_files_button.clicked.connect(self.AddFiles)
        self.remove_file_button.clicked.connect(self.removeFile)
        self.save_button.clicked.connect(self.saveImgData)
        self.train_button.clicked.connect(self.trainOCR)
        self.ocr_button.clicked.connect(self.runOCR)
        self.next_button.clicked.connect(self.nextBox)
        self.prev_button.clicked.connect(self.previousBox)
        #self.add_screenshots.clicked.connect(self.AddFiles)
        #self.wizardPage2.pageCreated.connect(self.AnalyzeImg)
        #self.contrast = 0.0
        self.img_fields = [self.g1,self.g2,self.g3,self.g4,self.g5,self.g6,self.g7,self.g8,self.g9,self.g10,self.g11,self.g12,self.g13,self.g14,self.g15,self.g16,self.g17,self.g18,self.g19,self.g20]
        self.input_fields = [self.e1,self.e2,self.e3,self.e4,self.e5,self.e6,self.e7,self.e8,self.e9,self.e10,self.e11,self.e12,self.e13,self.e14,self.e15,self.e16,self.e17,self.e18,self.e19,self.e20]
        self.boxlist = []
        self.imglist = []
        self.charlist = []
        self.current = 0
        self.scene = None
        self.ratio_h = 1.0
        self.ratio_w = 1.0
        self.base = self.loadBase()
        self.user = self.loadUser()
        if not self.base is None:
            self.base_data_label.setText(self.getBaseData())
        if not self.user is None:
            self.delete_images_button.setEnabled(True)
            self.user_data_label.setText(self.getUserData())
        self.resizeElements()
        
        for index,item in zip(range(20), self.input_fields):
            item.textEdited.connect(partial(self.changeText, index))
        self.train_button.setEnabled(True)
        
    def deleteUserImages(self):
        self.user = None
        path = self.settings.app_path+"\\trainingdata\\user_training_data.pck"
        remove(path)
        self.user_data_label.setText("-")
        self.delete_images_button.setEnabled(False)
    
    def showSummary(self):
        summary = ""
        userdata = {}
        characters = ["'", ',', '-', '&', '[', ']', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        for char in self.charlist:
            if char in characters:
                if char in userdata:
                    userdata[char] += 1
                else:
                    userdata[char] = 1
        for key in characters:
            if key in userdata:
                summary += '"'+key+'"' +": " +str(userdata[key])+", "
                
        self.summary_label.setText(summary)
    
    def trainOCR(self):
        self.train_button.setEnabled(False)
        alldata = self.connectData()
        testnumbers = self.getRandomData(alldata,[',', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        testletters = self.getRandomData(alldata,["'", ',', '-', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
        teststation = self.getRandomData(alldata,["'", ',', '-', '&', '[', ']', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
        self.movie = QMovie(":/ico/loader.gif")
        self.loader.setMovie(self.movie)
        self.movie.start()
        self.numberstrainerthread = Trainer(self, "numbers", self.base, self.user, testnumbers, testletters, teststation)
        self.letterstrainerthread = Trainer(self, "letters", self.base, self.user, testnumbers, testletters, teststation)
        self.stationtrainerthread = Trainer(self, "station", self.base, self.user, testnumbers, testletters, teststation)
        QObject.connect(self.numberstrainerthread, SIGNAL('finished(QString, int)'), self.stepFinished)
        QObject.connect(self.letterstrainerthread, SIGNAL('finished(QString, int)'), self.stepFinished)
        QObject.connect(self.stationtrainerthread, SIGNAL('finished(QString, int)'), self.stepFinished)
        #QObject.connect(self.trainerthread, SIGNAL('finishedall(int)'), self.trainingFinished)
        self.numberstrainerthread.execute()
        self.letterstrainerthread.execute()
        self.stationtrainerthread.execute()
        self.training_summary.setText("Training in progress")

    def trainingFinished(self):
        if self.errors < 3:
            self.training_summary.setText("The training sucessfully finished. Your OCR accuracy should be very high.")
        elif self.errors < 6:
            self.training_summary.setText("The training sucessfully finished. Your OCR accuracy should satisfactory. You might still increase it by repeating this process with other screenshots.")
        elif self.errors < 10:
            self.training_summary.setText("The training sucessfully finished. Your OCR accuracy is sufficient but not perfect. You should repeat this process with other screenshots.")
        else:
            self.training_summary.setText("The training finished. Your OCR accuracy is not sufficient. You should repeat this process with other screenshots.")
        
    def stepFinished(self, value, error):
        self.steps += 1
        self.details.append(value+"\n")
        self.errors += error
        if self.steps == 3:
            self.trainingFinished()
            self.movie.stop()
            self.loader.clear()
    
    def connectData(self):
        connected = {}
        characters = ["'", ',', '-', '&', '[', ']', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        
        if self.user is None:
            self.user = {}
        if self.base is None:
            self.base = {}
            

        for char in characters:
            if char in self.base and char in self.user:
                connected[char] = self.base[char]+self.user[char]
            elif char in self.base:
                connected[char] = self.base[char]
            elif char in self.user:
                connected[char] = self.user[char]
        return connected
        
    def getRandomData(self, data, characters):
        self.testsamples = {}
        samples = 30
        
        for char in characters:
            amount = len(data[char])/400
            if amount > samples:
                picks = random.sample(range(amount), samples)
            else:
                picks = random.sample(range(amount), amount)
                
            temp = bitarray()
            for pick in picks:
                temp += data[char][pick*400:pick*400+400]
                
            self.testsamples[char] = temp
                
        return self.testsamples
    
    def saveImgData(self):
        characters = ["'", ',', '-', '&', '[', ']', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        
        if self.user is None:
            self.user = {}
            
        for i in range(len(self.charlist)):
            if self.charlist[i] in characters:
                data = bitarray()
                image = cv2.resize(self.imglist[i], (20, 20))
                ret,image = cv2.threshold(image,250,255,cv2.THRESH_BINARY)
                for row in image:
                    for cell in row:
                        if cell == 255:
                            data.append(True)
                        else:
                            data.append(False)
                if self.charlist[i] in self.user:
                    self.user[self.charlist[i]] += data
                else:
                    self.user[self.charlist[i]] = data
                    
        path = self.settings.app_path+"\\trainingdata\\user_training_data.pck"
        file = gzip.GzipFile(path, 'wb')
        pickle.dump(self.user, file,-1)
        file.close()
        
        self.save_button.setEnabled(False)
        self.train_button.setEnabled(True)
                                
        
    
    def changeText(self, index):
        #print index
        if len(self.charlist) > (self.current*20)+index:
            self.charlist[(self.current*20)+index] = str(self.input_fields[index].text())
    
    def getBaseData(self):
        text = ""
        keys = []
        for key in self.base:
            keys.append(key)
        keys.sort()
        for key in keys:
            text += key + ": " + str(len(self.base[key])/400)+", "
        #print keys
        return text
        
    def getUserData(self):
        text = ""
        keys = []
        for key in self.user:
            keys.append(key)
        keys.sort()
        for key in keys:
            text += key + ": " + str(len(self.user[key])/400)+", "
        return text
    
    def loadBase(self):
        try:
            path = self.settings.app_path+"\\trainingdata\\base_training_data.pck"
            file = gzip.GzipFile(path, 'rb')
            letters = pickle.load(file)
            file.close()
            return letters
        except:
            return None
        
    def loadUser(self):
        try:
            path = self.settings.app_path+"\\trainingdata\\user_training_data.pck"
            file = gzip.GzipFile(path, 'rb')
            letters = pickle.load(file)
            file.close()
            return letters
        except:
            return None
    
    def removeFile(self):
        item = self.file_list.currentItem()
        self.file_list.takeItem(self.file_list.currentRow())
        del item
    
    def AddFiles(self):
        if self.settings["native_dialog"]:
                files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'])
        else:
            files = QFileDialog.getOpenFileNames(self, "Open", self.settings['screenshot_dir'], options = QFileDialog.DontUseNativeDialog)

        if files == []:
            return
        first_item = None
        counter = 0
        for file in files:
            file1 = unicode(file).encode(sys.getfilesystemencoding())
            item = CustomQListWidgetItem(split(file1)[1], file1, self.settings)
            if first_item == None:
                first_item = item
            self.file_list.addItem(item)
            counter+=1
            
    def resizeElements(self):
        fields = self.input_fields
        for field in fields:
            field.setMinimumSize(QSize(0, self.settings['input_size']))
            field.setMaximumSize(QSize(16777215, self.settings['input_size']))
        canvases = self.img_fields
        for canvas in canvases:
            canvas.setMinimumSize(QSize(0, self.settings['snippet_size']))
            canvas.setMaximumSize(QSize(16777215, self.settings['snippet_size']))
            
    def runOCR(self):
        self.add_files_button.setEnabled(False)
        self.remove_file_button.setEnabled(False)
        self.ocr_button.setEnabled(False)
        self.file_list.setEnabled(False)
        self.repaint()
        self.current_image = 0
        self.results = []
        images = []
        self.prev = []
        files = self.file_list.count()
        for i in xrange(files):
            self.file_list.setCurrentRow(i)
            item = self.file_list.currentItem()
            color_image = item.loadColorImage()
            preview_image = item.addTestImage(color_image)
            images.append(color_image)
            self.prev.append(preview_image)
            #cv2.imshow("x", color_image)
            #cv2.waitKey(0)
            #
            #images.append(preview_image)
            #self.setPreviewImage(preview_image)
            #return
            current_result = OCR(color_image, item.ocr_areas, self.settings["ocr_language"], item, levels = False)
            
            self.results.append(current_result)
        self.allBoxes()
        #self.drawSnippet(self.imglist[0])
        #self.setPreviewImage(self.prev[0])
        self.next_button.setEnabled(True)
        self.prev_button.setEnabled(True)
        self.showSet()
        #self.drawOCRPreview()
        #self.character_input.setText(self.charlist[self.current])
    
    def showSet(self):
        pictures = len(self.img_fields)
        if pictures < len(self.imglist)-((self.current-1)*20):
            for i in range(20):
                if len(self.imglist) > (self.current*20)+i:
                    self.drawSnippet(self.img_fields[i], self.imglist[(self.current*20)+i])
                    self.input_fields[i].setText(self.charlist[(self.current*20)+i])
                else:
                    self.cleanSnippet(self.img_fields[i])
                    self.input_fields[i].setText("")
                    self.wizardPage2.fullfilled = True
                    self.wizardPage2.completeChanged.emit()
            
    
    def previousBox(self):
        if self.current > 0:
            self.current -= 1
            self.showSet()
       
    def nextBox(self):
        #print self.maxcount
        if self.current < self.maxcount:
            self.current += 1
            self.showSet()
            
    def cleanSnippet(self, graphicsview):
        scene = QGraphicsScene()
        graphicsview.setScene(scene)
        
    def drawOCRPreview(self):
        factor = 1.0
        img = self.prev[0]
        
        old_h = img.height()
        old_w = img.width()
        
        pix = img.scaled(QSize(self.preview.size().width()*factor,self.preview.size().height()*factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #pix = img.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        new_h = pix.height()
        new_w = pix.width()
        
        self.ratio_h = old_h/float(new_h)
        self.ratio_w = old_w/float(new_w)
        
        self.scene = QGraphicsScene()
        self.scene.addPixmap(pix)
        #self.scene.addPixmap(img)
        
        self.previewRects = []

        pen = QPen(Qt.yellow)
        redpen = QPen(Qt.red)
        bluepen = QPen(Qt.blue)
        greenpen = QPen(Qt.green)
        
        #for box in self.boxes():
        #    rect = self.addRect(self.scene, box, ratio_w, ratio_h, pen)
        #    self.previewRects.append(rect)
        rect = self.addRect(self.scene, self.boxlist[0], self.ratio_w, self.ratio_h, pen)
        self.previewRects.append(rect)
        self.previewSetScene(self.scene)

    
    def drawSnippet(self, graphicsview, snippet):
        """Draw single result item to graphicsview"""
        processedimage = array2qimage(snippet)
        pix = QPixmap()
        pix.convertFromImage(processedimage)
        pix = pix.scaled(graphicsview.width(), graphicsview.height()-1, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        graphicsview.setScene(scene)
        graphicsview.show()
    
    def addRect(self, scene, item, ratio_w, ratio_h, pen):
        """Adds a rectangle to scene and returns it."""
        rect = scene.addRect((item[0])/ratio_w , (item[2])/ratio_h,
                              item[1]/ratio_w, item[3]/ratio_h, pen)
        return rect
    
    def allBoxes(self):
        for i in range(self.file_list.count()):
            self.file_list.setCurrentRow(i)
            current = self.file_list.currentItem()
            res = self.results[i].station.name
            cres = self.results[i]
            self.charlist += list(res.value.replace(" ", ""))
            #boxlist += 
            for unit in self.results[i].station.name.units:
                self.boxlist.append([unit[0]+current.station_offset[0],unit[1]-unit[0],
                unit[2]+current.station_offset[1],unit[3]-unit[2]])
                
                image = cres.station_img[unit[2]:unit[3]+1,unit[0]:unit[1]]
                h = res.h
                if len(image) > 0:
                    if ((h*1.0)/len(image[0])) > 3:
                        image = cres.station_img[res.y1:unit[3], unit[0]:unit[1]]
                        border = (h - len(image[0]))/2
                        image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))

                    if len(image) < h/2.0:
                        image = cres.station_img[res.y1:res.y2, unit[0]:unit[1]]
                        border = (h - len(image[0]))/2
                        image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))
                    self.imglist.append(image)
            
            for line in self.results[i].commodities:
                for item in line.items:
                    if not item is None:
                        self.charlist += list(item.value.replace(" ", ""))
                        for unit in item.units:
                            self.boxlist.append([unit[0]+current.market_offset[0],unit[1]-unit[0],
                                            unit[2]+current.market_offset[1],unit[3]-unit[2]])
                                           
                            image = cres.commodities_img[unit[2]:unit[3]+1,unit[0]:unit[1]]
                            h = line.h
                            if len(image) > 0:
                                if ((h*1.0)/len(image[0])) > 3:
                                    image = cres.commodities_img[line.y1:unit[3], unit[0]:unit[1]]
                                    border = (h - len(image[0]))/2
                                    image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))

                                if len(image) < h/2.0:
                                    image = cres.commodities_img[line.y1:line.y2, unit[0]:unit[1]]
                                    border = (h - len(image[0]))/2
                                    image = cv2.copyMakeBorder(image,0,0,border,border,cv2.BORDER_CONSTANT,value=(255,255,255))
                                
                                self.imglist.append(image)
        self.maxcount = len(self.imglist)/20
        
    
    def setPreviewImage(self, image):
        """Show image in self.preview."""
        #factor = self.factor.value()
        factor = 1.0
        pix = image.scaled(QSize(self.preview.size().width()*factor,self.preview.size().height()*factor), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scene = QGraphicsScene()
        scene.addPixmap(pix)
        self.previewSetScene(scene)
        
    def previewSetScene(self, scene):
        """Shows scene in preview"""
        self.preview.setScene(scene)
        self.preview.show()