# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL, QUrl, QThread, QString
from updateUI import Ui_Update
from threadworker import Worker
import os
from os import makedirs, rename, remove
from os.path import isdir, isfile
import os
import requests
import time
import sys
import subprocess

class UpdateDialog(QDialog, Ui_Update):
    def __init__(self, path, appversion, newupd):
        QDialog.__init__(self)
        self.app_path = path
        self.setupUi(self)
        self.exiting = False
        self.appversion = appversion
        self.newupd = newupd
        self.filepath = ""
        if not newupd is None:
            self.label.setText("New version found: "+newupd[1])
            self.download.setEnabled(True)
            
        #self.download.setEnabled(True)
        self.download.clicked.connect(self.downloadFile)
        self.check.clicked.connect(self.checkUpdate)
        
        self.thread = Worker()
        self.connect(self.thread, SIGNAL("output(QString, QString)"), self.showUpdateAvailable)
        self.connect(self.thread, SIGNAL("end()"), self.showNoUpdate)
        
        self.downloader = Downloader(self)
        self.connect(self.downloader, SIGNAL("loaded(int, int)"), self.updateProgress)
        self.connect(self.downloader, SIGNAL("finished()"), self.downloadFinished)
        self.connect(self.downloader, SIGNAL("finishederror()"), self.downloadFinishedError)
    
    def closeEvent(self, event):
        self.emit(SIGNAL("exiting()"))
        event.accept()
    
    def downloadFile(self):
        self.check.setEnabled(False)
        self.download.setEnabled(False)
        
        if not self.newupd is None:
            self.label.setText("Starting download.")
            url = "http://sourceforge.net/projects/eliteocr/files/"+self.newupd[0]+"/EliteOCR."+self.newupd[1]+".zip"
            #url = "http://blog.fancyrhino.com/wp-content/uploads/2014/03/3.jpg"
<<<<<<< HEAD
            if not isdir(unicode(self.app_path)+u""+ os.sep +".."+ os.sep +"update"+ os.sep +""):
                makedirs(unicode(self.app_path)+u""+ os.sep +".."+ os.sep +"update"+ os.sep +"")
            self.filepath = unicode(self.app_path)+u""+ os.sep +".."+ os.sep +"update"+ os.sep +"EliteOCR."+unicode(self.newupd[1])+u".zip.part"
=======
            if not isdir(unicode(self.app_path)+os.sep+u".."+os.sep+u"update"+os.sep):
		    makedirs(unicode(self.app_path)+os.sep+u".."+os.sep+u"update"+os.sep)
            self.filepath = unicode(self.app_path)+os.sep+u".."+os.sep+u"update"+os.sep+u"EliteOCR."+unicode(self.newupd[1])+u".zip.part"
>>>>>>> master
            #print self.filepath
            self.downloader.get(url, self.filepath)
    
    def downloadFinished(self):
        if isfile(self.filepath[:-5]):
            remove(self.filepath[:-5])
        rename(self.filepath, self.filepath[:-5])
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.label.setText("Download finished. You can find it in the update directory.")
        
<<<<<<< HEAD
        subprocess.Popen(r'explorer /select,"'+unicode(self.app_path).encode(sys.getfilesystemencoding())+ os.sep +".."+ os.sep +"update"+ os.sep +"EliteOCR."+unicode(self.newupd[1]).encode(sys.getfilesystemencoding())+".zip")
=======
        subprocess.Popen(r'explorer /select,"'+unicode(self.app_path).encode('windows-1252')+os.sep+'..'+os.sep+'update'+os.sep+'EliteOCR.'+unicode(self.newupd[1]).encode('windows-1252')+'.zip"')
>>>>>>> master
    
    def downloadFinishedError(self):
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.label.setText("Error while downloading.")

    def updateProgress(self, done, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(done)
        self.label.setText("Downloading: "+unicode("%.2f" % (done/1048576.0))+"MB / "+unicode("%.2f" % (total/1048576.0))+"MB")

    def showNoUpdate(self):
        self.label.setText("No updates found.")
        self.check.setEnabled(True)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
    
    def showUpdateAvailable(self, dir, appversion):
        self.newupd = (dir, appversion)
        self.label.setText("New version found: "+appversion)
        self.check.setEnabled(True)
        self.download.setEnabled(True)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        
    def checkUpdate(self):
        self.label.setText("Looking for new updates")
        self.check.setEnabled(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(0)
        self.thread.check(self.appversion)
        
class Downloader(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.url = ""
        self.path = "./"
        self.exiting = False
        self.connect(parent, SIGNAL("exiting()"), self.abort)
    
    def abort(self):
        self.exiting = True
    
    def get(self, url, path):
        self.url = url
        self.path = path
        self.start()
    
    def run(self):
        url = self.url
        localFilename = self.path
        
        with open( localFilename, 'wb') as f:
            start = time.clock()
            r = requests.get(url, stream=True)
            total_length = r.headers.get('content-length')
            dl = 0
            if total_length is None: # no content length header
                f.write(r.content)
            else:
                for chunk in r.iter_content(1024):
                    if self.exiting:
                        return
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / int(total_length))
                    speed = (dl//(time.clock() - start)) #in bps
                    self.emit(SIGNAL("loaded(int,int)"), int(dl), int(total_length))
        
        
        if (dl == total_length) and (not self.exiting):
            self.emit(SIGNAL("finished()"))
        else:
            self.emit(SIGNAL("finishederror()"))
