import requests
import json
import time
from PyQt4.QtCore import QThread, SIGNAL

class EDDNExport(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.parent = parent
    
    def execute(self, data, userID):
        self.data = data
        self.userID = userID
        self.start()
    
    def run(self):
        parent = self.parent
        data = self.data
        userID = self.userID
        #print data
        outcomeok = []
        outcomefail = []
        toprocess = len(data)
        counter = 0
        for line in data:
            try:
                postdata = json.dumps(self.createRequest(line, userID))

                r = requests.post("http://eddn-gateway.elite-markets.net:8080/upload/", data=postdata)
                #print postdata
                #time.sleep(1)
                if r.text.strip() == "OK":
                    outcomeok.append("OK")
                else:
                    print(line[2] + " failed")
                    outcomefail.append("Fail")
            except:
                outcomefail.append("Fail")
                print(line[2] + " failed")
                #pass
            counter += 1
            self.emit(SIGNAL("update(int,int)"), counter, toprocess)
            
        self.result = "Success: "+str(len(outcomeok))+" Fail: "+str(len(outcomefail))
        self.emit(SIGNAL("finished(QString)"), self.result)
        
        
    def createRequest(self, line, userID):
        request = {
                    "$schemaRef": "http://schemas.elite-markets.net/eddn/commodity/1",
                    "header": {
                        "uploaderID": userID,
                        "softwareName": "EliteOCR",
                        "softwareVersion": self.parent.appversion
                    },
                    "message": self.makeDict(line)
                   }
        return request
        
    def makeDict(self, line):
        new_dict = { "systemName": line[0],
                     "stationName": line[1],
                     "itemName": line[2],
                     "buyPrice": (int(line[4]) if line[4] else 0),
                     "stationStock": (int(line[7]) if line[7] else 0),
                     "sellPrice": (int(line[3]) if line[3] else 0),
                     "demand": (int(line[5]) if line[5] else 0),
                     "timestamp": line[9],
                    }
        if line[6] != "":
            new_dict["supplyLevel"] = line[6]
        if line[8] != "":
            new_dict["demandLevel"] = line[8]
        #print new_dict
        return new_dict