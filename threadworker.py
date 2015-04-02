import requests
import re
from bs4 import BeautifulSoup
from PyQt4.QtCore import QThread, SIGNAL

class Worker(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.ver = 0
        
    
    def check(self, version):
        self.ver = version
        self.start()
    
    def versioncmp(self, version1, version2):
        def normalize(v):
            try:
                return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
            except:
                return 0
        return cmp(normalize(version1), normalize(version2))
    
    def run(self):
        try:
            r = requests.get('http://sourceforge.net/projects/eliteocr/files/')
        except:
            return
        #print r.status_code
        result = r.text.encode('utf-8')

        versions = []

        soup = BeautifulSoup(result)
        try:
            for line in soup.findAll("table", { "id" : "files_list" }):
                for row in line.findAll("tr", { "class" : "folder" }):
                    if re.search("[0-9]$", row['title'].strip()):
                        versions.append(row['title'].strip())

            versions.sort(reverse=True)
        except:
            return
            
        try:
            r2 = requests.get('http://sourceforge.net/projects/eliteocr/files/'+versions[0]+"/")
        except:
            return
        #print "got files"
        result2 = r2.text.encode('utf-8')

        files = []

        soup = BeautifulSoup(result2)
        for line in soup.findAll("table", { "id" : "files_list" }):
            for row in line.findAll("tr", { "class" : "file" }):
                if re.search("zip$", row['title'].strip()):
                    files.append(row['title'].strip()[9:-4])

        files.sort(reverse=True)

        newerfile = ""
        for file in files:
            if self.versioncmp(self.ver, file) < 0:
                newerfile = file
                break
                
        if newerfile != "":
            self.emit(SIGNAL("output(QString,QString)"), versions[0], newerfile)
            return
            
        self.emit(SIGNAL("end()"))
        