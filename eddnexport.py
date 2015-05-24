# -*- coding: utf-8 -*-
import grequests
import json
import time
from PyQt4.QtCore import QThread, SIGNAL

class EDDNExport(QThread):
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.parent = parent
        self.counter = 0
        self.outcomeok = []
        self.outcomefail = []
    
    def execute(self, data, userID):
        self.data = data
        self.userID = userID
        self.start()
    
    def hook_factory(self, name, *factory_args, **factory_kwargs):
        def getEDDNResponse(response, **kwargs):
            if response.text.strip() == "OK": 
                self.outcomeok.append(name)
            else:
                self.outcomefail.append(name)
            self.counter += 1
            self.emit(SIGNAL("update(int,int)"), self.counter, self.toprocess)
            if self.counter == self.toprocess:
                self.exportFinished()
        return getEDDNResponse
            
    def exportFinished(self):
        self.result = "Success: "+unicode(len(self.outcomeok))+" Fail: "+unicode(len(self.outcomefail))
        self.emit(SIGNAL("finished(QString, PyQt_PyObject)"), self.result, self.outcomefail)
    
    def run(self):
        self.counter = 0
        parent = self.parent
        data = self.data
        userID = self.userID
        #print data
        self.outcomeok = []
        self.outcomefail = []
        self.toprocess = len(data)
        counter = 0
        
        req_list = []
        for line in data:
            #print line
            #print self.createRequest(line, userID)["message"]
            json_data = json.dumps(self.createRequest(line, userID))
            req_list.append((json_data, line[2]))
          
        async_list = []

        for d in req_list:
            action_item = grequests.post("http://eddn-gateway.elite-markets.net:8080/upload/", data=d[0], hooks = {'response' : [self.hook_factory(name=d[1])]})
            async_list.append(action_item)

        # Do our list of things to do via async
        grequests.map(async_list)
        
    def createRequest(self, line, userID):
        message = self.makeDict(line)
        if message is None:
            return {}
        request = {
                    "$schemaRef": "http://schemas.elite-markets.net/eddn/commodity/1",
                    "header": {
                        "uploaderID": userID,
                        "softwareName": "EliteOCR",
                        "softwareVersion": self.parent.appversion
                    },
                    "message": message
                   }
        return request
        
    def makeDict(self, line):
        numbers = [line[3],line[4],line[5],line[7]]
        buy = line[4] if line[4] != "" else 0
        stock = line[7] if line[7] != "" else 0
        sell = line[3] if line[3] != "" else 0
        demand = line[5] if line[5] != "" else 0
        
        if not buy is None:
            if buy != "":
                try:
                    int(buy)
                except:
                    return None
        if not stock is None:
            if stock != "":
                try:
                    int(stock)
                except:
                    return None
        if not sell is None:
            if sell != "":
                try:
                    int(sell)
                except:
                    return None
        if not demand is None:
            if demand != "":
                try:
                    int(demand)
                except:
                    return None
                    
        new_dict = { "systemName": line[0],
                     "stationName": line[1],
                     "itemName": line[2],
                     "buyPrice": (int(buy) if not buy is None else 0),
                     "stationStock": (int(stock) if not stock is None else 0),
                     "sellPrice": (int(sell) if not sell is None else 0),
                     "demand": (int(demand) if not demand is None else 0),
                     "timestamp": line[9],
                    }
        if line[8] != "":
            new_dict["supplyLevel"] = line[8]
        if line[6] != "":
            new_dict["demandLevel"] = line[6]
        return new_dict