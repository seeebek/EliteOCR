from datetime import datetime
import codecs

class XMLOutput():
    def __init__(self, language, input, output, item, result, system, w, h):
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<ocrresult>\n'
        xml += '    <setup>\n'
        xml += '        <language>'+language+'</language>\n'
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