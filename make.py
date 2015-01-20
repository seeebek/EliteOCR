from subprocess import call
from shutil import copy, copytree, rmtree, move

try:
    rmtree("./dist/bin/")
    print "bin deleted"
except:
    print "bin not deleted"

try:
    retcode = call("pyinstaller --onedir EliteOCR.spec")
    print ""
    print "pyinstaller finished with code: " + str(retcode)
except:
    print "pyinstaller error"

"""    
try:
    rmtree("./dist/tessdata/")
    print "tessdata deleted"
except:
    print "tessdata not deleted"
"""    
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
    
try:
    copytree("./translations/", "./dist/EliteOCR/translations/")
    print "translations copied"
except:
    print "translations not copied"
    
try:
    copytree("./nn_scripts/", "./dist/EliteOCR/nn_scripts/")
    print "nn_scripts copied"
except:
    print "nn_scripts not copied"

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