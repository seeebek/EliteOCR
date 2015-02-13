# -*- coding: utf-8 -*-
import codecs
import json
import sys
from datetime import datetime
from os.path import dirname

class XMLOutput():
    def __init__(self, language, input, output, item, result, system, w, h, translate):
        self.lang = language

        if getattr(sys, 'frozen', False):
            self.app_path = dirname(sys.executable)
        elif __file__:
            self.app_path = dirname(__file__)
        else:
            self.app_path = "./"
        
        if translate:
            self.translate(result)
            # translate the shit
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<ocrresult>\n'
        xml += '    <setup>\n'
        xml += '        <language>'+self.lang+'</language>\n'
        xml += '        <inputfile>'+input+'</inputfile>\n'
        xml += '        <resolution>'+str(w)+'x'+str(h)+'</resolution>\n'
        xml += '        <marketWidth>'+str(item.market_width)+'</marketWidth>\n'
        xml += '        <filetimestamp>'+item.timestamp+'</filetimestamp>\n'
        xml += '        <ocrtime>'+datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")+'</ocrtime>\n'
        xml += '    </setup>\n'
        xml += '    <location>\n'
        if system is None:
            xml += '        <system fromlog="true">'+item.system+'</system>\n'
        else:
            xml += '        <system fromlog="false">'+system+'</system>\n'
        xml += '        <station conf="'+str(result.station.name.confidence)+'">'+result.station.name.value.title().replace("'S", "'s")+'</station>\n'
        xml += '    </location>\n'
        xml += '    <market>\n'
        for entry in result.commodities:
            xml += '        <entry>\n'
            for index, name in zip(range(7),["commodity","sell","buy","demand","demandlevel","supply","supplylevel"]):
                text = entry.items[index].value.title().replace(",", "") if not entry.items[index] is None else ""
                conf = ' conf="'+str(entry.items[index].confidence)+'"' if not entry.items[index] is None else ""
                xml += '            <'+name+conf+'>'+text+'</'+name+'>\n'
            xml += '        </entry>\n'
        xml += '    </market>\n'
        xml += '</ocrresult>\n'
        
        #print xml
        file = unicode(output)
        xml_file = codecs.open(file, "w", "utf-8")
        xml_file.write(xml)
        xml_file.close()
        
    def translate(self, result):
        language = self.lang
        file = codecs.open(self.app_path + "\\commodities.json", 'r')
        self.comm_list = json.loads(file.read())
        levels = {u"LOW":{u"deu":u"NIEDRIG", u"fra":u"FAIBLE"},
                  u"MED":{u"deu":u"MITTEL", u"fra":u"MOYEN"},
                  u"HIGH":{u"deu":u"HOCH", u"fra":u"ÉLEVÉ"}}
        self.comm_list.update(levels)
        if language == "big" or language == "eng":
            return 
        else:
            self.comm_list = {v[language]:k for k, v in self.comm_list.iteritems()}
            self.lang = "eng"
        
        #print input
        res = result.commodities
        for i in range(len(res)):
            for j in range(len(res[i].items)):
                if not res[i].items[j] is None:
                    if res[i].items[j].value in self.comm_list:
                        res[i].items[j].value = self.comm_list[res[i].items[j].value]
            
        
        return 