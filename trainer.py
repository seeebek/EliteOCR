# -*- coding: utf-8 -*-
import sys
import os
import cv2
import numpy as np
from time import time
from PyQt4.QtCore import QSettings, QThread, SIGNAL
from settings import Settings

class Trainer(QThread):
    def __init__(self, parent, type, base, user, tnumbers, tletters, tstation):
        QThread.__init__(self, parent)
        self.type = type
        self.base = base
        self.user = user
        self.testnumbers = tnumbers
        self.testletters = tletters
        self.teststation = tstation
        self.errors = 0
        self.message = type.title()+" training:\n"
    
    def execute(self):
        self.start()
    
    def run(self):
        self.settings = Settings()
        self.time1 = time()
        
        if self.type == "numbers":
            self.trainNumbers()
            
        if self.type == "letters":
            self.trainLetters()
            
        if self.type == "station":
            self.trainStation()
            
        self.message += self.type.title() + " training took " + str(int(time()-self.time1))+"s to perform."
        self.emit(SIGNAL("finished(QString, int)"), self.message, self.errors)
        
    def trainNumbers(self):
        classdict = {"0":0,"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,",":10,"-":11}
        nnetwork = self.trainProcess(classdict)
        if not nnetwork is None:
            nnetwork.save((self.settings.storage_path + os.sep +"user_numbers.xml").encode(sys.getfilesystemencoding()), "OCRMLP")
            
            resultcheck = self.testProcess(classdict, self.testnumbers)
            if not resultcheck is None:
                predictions = np.empty_like(resultcheck[1])
                nnetwork.predict(resultcheck[0], predictions)
                self.processResults(classdict, resultcheck[1], predictions)
    
    def trainLetters(self):
        classdict = {"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25,"-":26,",":27,"'":28}
        nnetwork = self.trainProcess(classdict)
        if not nnetwork is None:
            nnetwork.save((self.settings.storage_path + os.sep + "user_letters.xml").encode(sys.getfilesystemencoding()), "OCRMLP")
            
            resultcheck = self.testProcess(classdict, self.testletters)
            if not resultcheck is None:
                predictions = np.empty_like(resultcheck[1])
                nnetwork.predict(resultcheck[0], predictions)
                self.processResults(classdict, resultcheck[1], predictions)
    
    def trainStation(self):
        classdict = {"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,"J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15,"Q":16,"R":17,"S":18,"T":19,"U":20,"V":21,"W":22,"X":23,"Y":24,"Z":25,"1":26,"2":27,"3":28,"4":29,"5":30,"6":31,"7":32,"8":33,"9":34,"-":35,",":36,"'":37,"&":38,"[":39,"]":40}
        nnetwork = self.trainProcess(classdict)
        if not nnetwork is None:
            nnetwork.save((self.settings.storage_path + os.sep + "user_station.xml").encode(sys.getfilesystemencoding()), "OCRMLP")
            
            resultcheck = self.testProcess(classdict, self.teststation)
            if not resultcheck is None:
                predictions = np.empty_like(resultcheck[1])
                nnetwork.predict(resultcheck[0], predictions)
                self.processResults(classdict, resultcheck[1], predictions)
    
    def processResults(self, classdict, testclasses, predictions):
        KEYS = len(classdict)
        revclassdict = dict((v,k.decode("utf-8")) for k,v in classdict.iteritems())
        results = {}
        for i in range(KEYS):
            results[i] = {}
            for j in range(KEYS):
                results[i][j] = 0
        for i in range(len(testclasses)):
            results[np.argmax(testclasses[i])][np.argmax(predictions[i])] += 1

        output = ""
        for i in range(KEYS):
            for j in range(KEYS):
                if results[i][j] == 0:
                    continue
                if revclassdict[i] == revclassdict[j]:
                    continue
                output += revclassdict[i] + " "
                self.errors += results[i][j]
                output +=  revclassdict[j]+": "+ str(results[i][j]) + " "
                output += "\n"
        if len(output) > 2:
            self.message += "Errors while testing:\n"
            self.message += output
        else:
            self.message += "No errors while testing.\n"
            
    def testProcess(self, classdict, testdata):
        KEYS = len(classdict)
        revclassdict = dict((v,k.decode("utf-8")) for k,v in classdict.iteritems())
        dictlength = 0
        for key in classdict:
            if key in testdata:
                dictlength += len(testdata[key])/400
        if dictlength == 0:
            return None
        
        test = np.empty((dictlength,400), dtype='float32')
        testclasses = -1 * np.ones((dictlength,KEYS), dtype='float32')
        
        counter = 0
        for key in classdict:
            if key in testdata:
                for i in range(len(testdata[key])/400):
                    for j in range(400):
                        if testdata[key][i*400+j]:
                            test[counter][j] = 1.0
                        else:
                            test[counter][j] = 0.0
                    testclasses[counter][classdict[key]] = 1.0
                    counter += 1
        
        return (test, testclasses)
        
        
    def trainProcess(self, classdict):
        KEYS = len(classdict)
        revclassdict = dict((v,k.decode("utf-8")) for k,v in classdict.iteritems())
        dictlength = 0
        for key in classdict:
            if not self.base is None:
                if key in self.base:
                    dictlength += len(self.base[key])/400
            if not self.user is None:
                if key in self.user:
                    dictlength += len(self.user[key])/400
        if dictlength == 0:
            return None
        data = np.empty((dictlength,400), dtype='float32')
        classes = -1 * np.ones((dictlength,KEYS), dtype='float32')
        
        counter = 0
        #np.set_printoptions(threshold=np.nan)
        for key in classdict:
            #base data
            if not self.base is None:
                if key in self.base:
                    for i in range(len(self.base[key])/400):
                        for j in range(400):
                            if self.base[key][i*400+j]:
                                data[counter][j] = 1.0
                            else:
                                data[counter][j] = 0.0
                        classes[counter][classdict[key]] = 1.0
                        counter += 1
                        #print data
                        #return None
            #user data
            if not self.user is None:
                if key in self.user:
                    for i in range(len(self.user[key])/400):
                        for j in range(400):
                            if self.user[key][i*400+j]:
                                data[counter][j] = 1.0
                            else:
                                data[counter][j] = 0.0
                            
                        classes[counter][classdict[key]] = 1.0
                        counter += 1
        # parameter setup 
        layers = np.array([400,71,KEYS])
        nnetwork = cv2.ANN_MLP(layers, 1,0.65,1)
        params = dict(term_crit = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 1000, 0.00001),
                      train_method = cv2.ANN_MLP_TRAIN_PARAMS_BACKPROP,
                      bp_dw_scale = 0.01,
                      bp_moment_scale = 0.01)
        # training
        iterations = nnetwork.train(data, classes, None, params = params)
        self.message += "Iterations: " + str(iterations)+"\n"
        return nnetwork
