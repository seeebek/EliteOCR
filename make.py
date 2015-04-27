# -*- coding: utf-8 -*-
from subprocess import call
from shutil import copy, copytree, rmtree, move

try:
    copy("./EliteOCR.py", "./EliteOCRcmd.py")
    print "EliteOCRcmd.py created"
except:
    print "EliteOCRcmd.py not created"

try:
    rmtree("./dist/bin/")
    print "bin deleted"
except:
    print "bin not deleted"
    
try:
    rmtree("./dist/EliteOCRcmd/")
    print "EliteOCRcmd deleted"
except:
    print "EliteOCRcmd not deleted"

try:
    retcode = call("pyinstaller --onedir EliteOCR.spec")
    print ""
    print "pyinstaller finished with code: " + unicode(retcode)
except:
    print "pyinstaller error"
    
try:
    retcode = call("pyinstaller --onedir EliteOCRcmd.spec")
    print ""
    print "pyinstaller finished with code: " + unicode(retcode)
except:
    print "pyinstaller error"

try:
    copy("./dist/EliteOCRcmd/EliteOCRcmd.exe", "./dist/EliteOCR/EliteOCRcmd.exe")
    print "EliteOCRcmd.exe copied"
except:
    print "EliteOCRcmd.exe not copied"
    
try:
    copy("./dist/EliteOCRcmd/EliteOCRcmd.exe.manifest", "./dist/EliteOCR/EliteOCRcmd.exe.manifest")
    print "EliteOCRcmd.exe.manifest copied"
except:
    print "EliteOCRcmd.exe.manifest not copied"
"""
try:
    rmtree("./dist/tessdata/")
    print "tessdata deleted"
except:
    print "tessdata not deleted"
 
try:
    copytree("./tessdata/", "./dist/tessdata/")
    print "tessdata copied"
except:
    print "tessdata not copied"
    
try:
    copytree("./tessdata/", "./dist/EliteOCR/tessdata/")
    print "tessdata copied to bin"
except:
    print "tessdata not copied to bin"
"""    
try:
    copytree("./translations/", "./dist/EliteOCR/translations/")
    print "translations copied"
except:
    print "translations not copied"
"""    
try:
    copytree("./nn_scripts/", "./dist/EliteOCR/nn_scripts/")
    print "nn_scripts copied"
except:
    print "nn_scripts not copied"
"""
try:
    copy("./letters.xml", "./dist/EliteOCR/letters.xml")
    print "letters.xml copied"
except:
    print "letters.xml not copied"
    
try:
    copy("./numbers.xml", "./dist/EliteOCR/numbers.xml")
    print "numbers.xml copied"
except:
    print "numbers.xml not copied"
    
try:
    copy("./station.xml", "./dist/EliteOCR/station.xml")
    print "station.xml copied"
except:
    print "station.xml not copied"
    
try:
    copytree("./plugins/", "./dist/EliteOCR/plugins/")
    print "plugins copied"
except:
    print "plugins not copied"
    
try:
    copytree("./help/", "./dist/EliteOCR/help/")
    print "help copied"
except:
    print "help not copied"
    
try:
    copytree("./trainingdata/", "./dist/EliteOCR/trainingdata/")
    print "trainingdata copied"
except:
    print "trainingdata not copied"
    
try:
    copy("./commodities.json", "./dist/EliteOCR/commodities.json")
    print "commodities copied"
except:
    print "commodities not copied"
    
try:
    copy("./LICENSE", "./dist/LICENSE")
    print "LICENSE copied"
except:
    print "LICENSE not copied"

try:
    copy("./README.md", "./dist/README.md")
    print "README.md copied"
except:
    print "README.md not copied"
    
try:
    move("./dist/EliteOCR/", "./dist/bin/")
    print "EliteOCR renamed to bin"
except:
    print "EliteOCR not renamed"