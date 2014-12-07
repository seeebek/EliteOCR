from os import listdir, remove, makedirs
from os.path import isdir
from subprocess import call

class BPC_Feeder():
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.delay = "5"
        self.writeIni()
        self.addCSVDir()
        self.deleteOldCSV()

    def addCSVDir(self):
        if not isdir(self.path+"\\plugins\\BPC_Feeder\\CSV"):
            makedirs(self.path+"\\plugins\\BPC_Feeder\\CSV")
    
    def writeIni(self):
        dir = (self.path+"\\plugins\\BPC_Feeder\\CSV\\")
        towrite = "[settings]\ntest mode = 1\ninput delay = "+self.delay+"\n"+\
            "EliteOCR CSV path = "+ dir+"\n"+\
            "Add Commod Prices open method = 1"
        file = self.path+"\\plugins\\BPC_Feeder\\bpc feeder.ini"
        ini_file = open(file, "w")
        ini_file.write(towrite)
        ini_file.close()

    def deleteOldCSV(self):
        path = self.path+"\\plugins\\BPC_Feeder\\CSV\\"
        dir = listdir(path)
        for file in dir:
            remove(path+file)
    
    def run(self):
        res = self.parent.current_result
        name = res.station.name.value
        file = self.path+"\\plugins\\BPC_Feeder\\CSV\\"+str(name).title()+".csv"
        allRows = self.parent.result_table.rowCount()
        towrite = ''
        for row in xrange(0, allRows):
            line = self.parent.result_table.item(row,0).text()+";"+\
                   self.parent.result_table.item(row,1).text()+";"+\
                   self.parent.result_table.item(row,2).text()+";"+\
                   self.parent.result_table.item(row,3).text()+";"+\
                   self.parent.result_table.item(row,4).text()+";"+\
                   self.parent.result_table.item(row,5).text()+";"+\
                   self.parent.result_table.item(row,6).text()+";"+\
                   self.parent.result_table.item(row,7).text()+";"+\
                   self.parent.result_table.item(row,8).text()+";"+\
                   self.parent.result_table.item(row,9).text()+";\n"
            towrite += line
        csv_file = open(file, "w")
        csv_file.write(towrite)
        csv_file.close()
        retcode = call(self.path+"\\plugins\\BPC_Feeder\\BPC feeder.exe")
        #for the case someting goes wrong
        self.deleteOldCSV()
