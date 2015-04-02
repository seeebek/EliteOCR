EliteOCR
==============
EliteOCR is a Python script that runs optical character recognition on screenshots
from Elite: Dangerous commodities market. 

Prerequisites
--------------
EliteOCR is capable of reading the entries in Elite: Dangerous markets screenshots.
Best results are achieved with screenshots of 3840 by 2160 pixel (4K) or more.
You can make screenshots in game by pressing F10. You find them usually in
C:\Users\USERNAME\Pictures\Frontier Developments\Elite Dangerous
Screenshots made with ALT+F10 have lower recognition rate!

Owners of Nvidia video cards can use DSR technology to increase the resolution 
for screenshots and revert it back to normal without leaving the game.

Usage
--------------
Run EliteOCR.exe
Click "+" and select your screenshots. Select multiple files by holding CTRL or add them one by one.
Select one file and click the OCR button. Check if the values have been recognised properly.
Optionally correct them or choose alternative from the drop down list. Click on "Add and Next"
to continue to next line. You can edit the values in the table by double clicking on the entry.

After processing one screenshot you can choose the next file in the list and click the ORC Button
again. Should there be a corrupted entry, you can click "Skip" to continue to next line without adding
current one to the list. Duplicate entries are by default filtered out. To change this behaviour
go to Settings.

When finished click on "Export" to save your results to a csv-file(separated by ; ). CSV can be
opened by most spreadsheet editors like Excel, LibreOffice Calc etc. or alternatively text editors.


Dependencies to run from source
--------------

### Requirements

###### Python 2.7 

[https://www.python.org/downloads/](https://www.python.org/downloads/)

###### Numpy 

[http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/](http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/)

###### OpenCV 

[http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.10/](http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.10/) 

Goto opencv/build/python/2.7 folder. 

Copy cv2.pyd to C:/Python27/lib/site-packages.

######PyQt4 

[http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)

###### qimage2ndarray 

pip install qimage2ndarray 

[http://pypi.python.org/pypi/qimage2ndarray](http://pypi.python.org/pypi/qimage2ndarray)

###### Openpyxl 

pip install openpyxl

[https://pypi.python.org/pypi/openpyxl](https://pypi.python.org/pypi/openpyxl)
    
###### Ezodf 

pip install ezodf

[https://pypi.python.org/pypi/ezodf](https://pypi.python.org/pypi/ezodf)

###### Lxml

pip install lxml

[https://pypi.python.org/pypi/lxml](https://pypi.python.org/pypi/lxml)

###### python-Levenshtein

pip install python-Levenshtein

[https://pypi.python.org/pypi/python-Levenshtein/](https://pypi.python.org/pypi/python-Levenshtein/)

###### PyTZ

pip install pytz

###### tzlocal

pip install tzlocal

###### Requests

pip install requests




Run EliteOCR.py

To create a standalone exe file
--------------

pip install pyinstaller

pyinstaller --onedir EliteOCR.py
