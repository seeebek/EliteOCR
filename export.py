# -*- coding: utf-8 -*-
<<<<<<< HEAD
import sys
=======
>>>>>>> master
import os
import codecs
import json
from datetime import datetime, timedelta
from time import strftime, strptime
from PyQt4.QtGui import QMessageBox, QFileDialog, QTableWidgetItem
from openpyxl import Workbook
from ezodf import newdoc, Sheet
#from pyexcel_ods import ODSWriter

class Export:
    def __init__(self, parent):
        self.parent = parent
        #self.translate()
    
    def translate(self, input):
<<<<<<< HEAD
        language = unicode(self.parent.settings["ocr_language"])
        file = codecs.open(self.parent.settings.app_path + ""+ os.sep +"commodities.json", 'r')
=======
        language = str(self.parent.settings["ocr_language"])
        file = codecs.open(self.parent.settings.app_path + os.sep + "commodities.json", 'r')
>>>>>>> master
        self.comm_list = json.loads(file.read())
        if language == "big" or language == "eng":
            return input
        else:
            self.comm_list = {v[language]:k for k, v in self.comm_list.iteritems()}
        
        levels = {u"deu":{u"NIEDRIG":u"LOW", u"MITTEL":u"MED", u"HOCH" :u"HIGH", u"":u""},
                  u"fra":{u"FAIBLE" :u"LOW", u"MOYEN" :u"MED", u"ÉLEVÉ":u"HIGH", u"":u""}}
        
        #print input
        translated = [input[0]]
        for line in input[1:]:
            if line[2].upper() in self.comm_list:
                commodity = self.comm_list[line[2].upper()].title()
            else:
                commodity = line[2]
            translated.append([line[0],line[1],commodity,line[3],line[4],line[5],
                               levels[language][line[6].upper()].title(),line[7],
                               levels[language][line[8].upper()].title(),line[9]])
        #print translated
        return translated
    
    def tableToList(self, allow_horizontal = False, allow_translate = False):
            all_rows = self.parent.result_table.rowCount()
            all_cols = self.parent.result_table.columnCount()
            result_list = [[u"System",u"Station",u"Commodity",u"Sell",u"Buy",u"Demand",u"",u"Supply",u"",u"Date"]]
            for row in xrange(0, all_rows):
                line = [self.safeStrToList(self.parent.result_table.item(row,9).text()),
                        self.safeStrToList(self.parent.result_table.item(row,0).text()),
                        self.safeStrToList(self.parent.result_table.item(row,1).text()),
                        self.safeStrToList(self.parent.result_table.item(row,2).text()),
                        self.safeStrToList(self.parent.result_table.item(row,3).text()),
                        self.safeStrToList(self.parent.result_table.item(row,4).text()),
                        self.safeStrToList(self.parent.result_table.item(row,5).text()),
                        self.safeStrToList(self.parent.result_table.item(row,6).text()),
                        self.safeStrToList(self.parent.result_table.item(row,7).text()),
                        self.safeStrToList(self.parent.result_table.item(row,8).text())]
                result_list.append(line)
            if allow_translate and self.parent.settings["translate_results"]:
                result_list = self.translate(result_list)
            if self.parent.settings['horizontal_exp'] and allow_horizontal:
                result_list = map(list, zip(*result_list))
            return result_list
        
    def safeStrToList(self, input):
        try:
            return int(input)
        except:
            return unicode(input)

    def exportToCsv(self, result, file):
        for row in result:
            if len(row[0]) == 0:
                QMessageBox.warning(self.parent,"No System Name", "There are rows missing system name! \nThe exported CSV file might be incompatible with some tools.")
                break
        towrite = ""
        for row in result:
            for cell in row:
                towrite += unicode(cell)+";"
            towrite += "\n"
        file = unicode(file).encode(sys.getfilesystemencoding())
        csv_file = codecs.open(file, "w", sys.getfilesystemencoding())
        csv_file.write(towrite)
        csv_file.close()

    def exportToOds(self, result, file):
        file = unicode(file)#.encode(sys.getfilesystemencoding())
        ods = newdoc(doctype='ods', filename=file)
        sheet = Sheet('Sheet 1', size=(len(result)+1, len(result[0])+1))
        ods.sheets += sheet
        
        for i in xrange(len(result)):
            for j in xrange(len(result[0])):
                sheet[i,j].set_value(result[i][j])
        ods.save()
    """
    def exportToOds2(self, result, file):
        odsresult = []
        for line in result:
            newline = []
            for cell in line:
                if cell == u"":
                    newline.append(None)
                    continue
                if str(cell)[:4] == u"2015":
                    newline.append(u"2015")
                else:
                    newline.append(cell)
            odsresult.append(newline)
        print odsresult
        file = unicode(file).encode('windows-1252')
        data = {}
        data["Sheet 1"] = odsresult
        writer = ODSWriter(file)
        writer.write(data)
        writer.close()
    """    

    def exportToXlsx(self, result, file):
        wb = Workbook()
        ws = wb.active

        for i in xrange(1,len(result)+1):
            for j in xrange(1,len(result[0])+1):
                ws.cell(row = i, column = j).value = result[i-1][j-1]
                
        file = unicode(file).encode(sys.getfilesystemencoding())
        wb.save(file)
        
    def bpcExport(self):
        name = unicode(self.parent.current_result.station.name.value).title().replace("'S", "'s")
        system = unicode(self.parent.result_table.item(0,9).text())
        time = strftime("%Y-%m-%dT%H.%M.%S")
<<<<<<< HEAD
        dir = self.parent.settings["export_dir"]+ os.sep +system+"."+name+"."+time+".bpc"
=======
        dir = self.parent.settings["export_dir"]+os.sep+system+"."+name+"."+time+".bpc"
>>>>>>> master
        if self.parent.settings["native_dialog"]:
            file = QFileDialog.getSaveFileName(None, 'Save', dir, "Slopey's Best Price Calculator CSV-File (*.bpc)",
                                          "Slopey's Best Price Calculator CSV-File (*.bpc)")
        else:
            file = QFileDialog.getSaveFileName(None, 'Save', dir, "Slopey's Best Price Calculator CSV-File (*.bpc)",
                                          "Slopey's Best Price Calculator CSV-File (*.bpc)", QFileDialog.DontUseNativeDialog)

        if not file:
            return

        result = self.translate(self.tableToList(False))

        all_rows = self.parent.result_table.rowCount()
        """
        for row in xrange(0, all_rows):
            if int(self.parent.result_table.item(row,10).text()) < 1185:
                QMessageBox.warning(self.parent,"Screenshots too small", "The market table in some of your screenshots is under 1190 pixel wide. This is too little for reliable OCR result. There were too many faulty contributions in the past caused by such screenshots. Export aborted. ")
                return
        """

        id = self.parent.settings['userID']
        bpc_format = [["userID","System","Station","Commodity","Sell","Buy","Demand","","Supply","","Date"]]
        allowedtime = datetime.utcnow() - timedelta(hours = 2)
        for row in result[1:]:
            
            if len(row[0]) == 0:
                QMessageBox.warning(self.parent,"No System Name", "There are rows missing system name! Could not export to BPC format.")
                return
            #if row[0].upper() == row[1].upper():
            #    QMessageBox.warning(self.parent,"System and station names identical", "There are rows where system and station names are identical. Export aborted.")
            #    return
            timescreenshot = datetime.strptime(row[9],"%Y-%m-%dT%H:%M:%S+00:00")
            if allowedtime > timescreenshot:
                QMessageBox.warning(self.parent,"Too old for BPC", "You have been using at least one screenshot which is too old. BPC format only allows screenshots younger than 2 hours. Export aborted.")
                return
            
            bpc_format.append([unicode(id)]+row)
            
        self.exportToCsv(bpc_format, file)
        self.parent.statusbar.showMessage ("To support the community consider exporting your data to EDDN", 4000)
        
    def eddnExport(self):
        all_rows = self.parent.result_table.rowCount()
        allowedtime = datetime.utcnow() - timedelta(hours = 2)
        to_send = []
        sent_rows = []
        
        result = self.translate(self.tableToList(False))[1:]
        
        for row in xrange(0, all_rows):
            """
            if int(self.parent.result_table.item(row,10).text()) < 1185:
                newitem = QTableWidgetItem("Too small resolution")
                self.parent.result_table.setItem(row, 11, newitem)
                continue
            """
            if len(self.parent.result_table.item(row,9).text()) == 0:
                newitem = QTableWidgetItem("No system name")
                self.parent.result_table.setItem(row, 11, newitem)
                continue
                
            timescreenshot = datetime.strptime(unicode(self.parent.result_table.item(row,8).text()),"%Y-%m-%dT%H:%M:%S+00:00")

            if allowedtime > timescreenshot:
                newitem = QTableWidgetItem("Data too old")
                self.parent.result_table.setItem(row, 11, newitem)
                continue

            if not self.parent.result_table.item(row,11) is None:
                if unicode(self.parent.result_table.item(row,11).text()) == "True":
                    continue
            
            line = result[row]
            
            to_send.append(line)
            newitem = QTableWidgetItem("True")
            self.parent.result_table.setItem(row, 11, newitem)
            sent_rows.append(row)
        
        notsent = list(set(range(all_rows))-set(sent_rows))
        """
        if len(to_send) < all_rows:
            QMessageBox.warning(self.parent,"Warning", "Following rows will not be exported to EDDN:\n "+\
            unicode(notsent)+"\n"+\
            "Possible reasons:\n"+\
            "- Rows were sent already once before\n"+\
            "- Rows contain no system name\n"+\
            "- Rows contain data older than two hours\n")
        """
        if len(to_send) > 0:
            self.parent.eddn_button.setEnabled(False)
            self.parent.statusbar.clearMessage()
            self.parent.eddnthread.execute(to_send, unicode(self.parent.settings["userID"]))

    def eddnFinished(self, result):
        self.parent.statusbar.showMessage("EDDN Export finished: "+result)
        self.parent.eddn_button.setEnabled(True)
        
    def eddnUpdate(self, done, outof):
        self.parent.statusbar.showMessage("EDDN Export processed "+unicode(done)+" out of "+unicode(outof))

    def exportToFile(self):
        if self.parent.settings['last_export_format'] == "":
            self.parent.settings.setValue('last_export_format', "csv")
            self.parent.settings.sync()
            
        if self.parent.settings['last_export_format'] == "xlsx":
            filter = "Excel Workbook (*.xlsx)"
        elif self.parent.settings['last_export_format'] == "ods":
            filter = "OpenDocument Spreadsheet (*.ods)"
        elif self.parent.settings['last_export_format'] == "csv":
            filter = "CSV-File (*.csv)"
        else:
            self.parent.settings.setValue('last_export_format', "csv")
            filter = "CSV-File (*.csv)"
            self.parent.settings.sync()
            
        name = unicode(self.parent.current_result.station.name.value).title().replace("'S", "'s")
        system = unicode(self.parent.result_table.item(0,9).text())
        time = strftime("%Y-%m-%dT%H.%M.%S")
<<<<<<< HEAD
        dir = self.parent.settings["export_dir"]+ os.sep +system+"."+name+"."+time+"."+self.parent.settings['last_export_format']+'"'
=======
        dir = self.parent.settings["export_dir"]+os.sep+system+"."+name+"."+time+"."+self.parent.settings['last_export_format']+'"'
>>>>>>> master
        if self.parent.settings["native_dialog"]:
            file = QFileDialog.getSaveFileName(None, 'Save', dir, "CSV-File (*.csv);;OpenDocument Spreadsheet (*.ods);;Excel Workbook (*.xlsx)",
                                          filter)
        else:
            file = QFileDialog.getSaveFileName(None, 'Save', dir, "CSV-File (*.csv);;OpenDocument Spreadsheet (*.ods);;Excel Workbook (*.xlsx)",
                                          filter, QFileDialog.DontUseNativeDialog)

        if not file:
            return

        
        
        if file.split(".")[-1] == "csv":
            self.parent.settings.setValue('last_export_format', "csv")
            self.parent.settings.sync()
            self.exportToCsv(self.tableToList(True, True), file)
        elif file.split(".")[-1] == "ods":
            self.parent.settings.setValue('last_export_format', "ods")
            self.parent.settings.sync()
            self.exportToOds(self.tableToList(True, True), file)
        elif file.split(".")[-1] == "xlsx":
            self.parent.settings.setValue('last_export_format', "xlsx")
            self.parent.settings.sync()
            self.exportToXlsx(self.tableToList(True, True), file)
        self.parent.statusbar.showMessage ("To support the community consider exporting your data to EDDN", 4000)
