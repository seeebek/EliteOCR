EliteOCR
==============
EliteOCR is a Python script that runs optical character recognition on screenshots
from Elite: Dangerous commodities market. 

Installation
--------------
### Requirements

1. Python 2.7 \
[https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Numpy \
[http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/](http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/)

3. OpenCV \
[http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.10/](http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.10/) \
Goto opencv/build/python/2.7 folder. \
Copy cv2.pyd to C:/Python27/lib/site-packages.

4. Python-Tesseract \
[https://bitbucket.org/3togo/python-tesseract/downloads/](https://bitbucket.org/3togo/python-tesseract/downloads/)

5. PyQt4 \
[http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)

6. qimage2ndarray \
pip install qimage2ndarray \
[http://pypi.python.org/pypi/qimage2ndarray](http://pypi.python.org/pypi/qimage2ndarray)

Prerequisites
--------------
EliteOCR is capable of recognising the commodities in screenshots.
Those should be at least 1920 by 1080 pixel in size and have an aspect ratio
of 16:9. Best results (100% accuracy) are achieved with screenshots
of 3840 by 2160 pixel (4K).
You can make screenshots in game by pressing F10. You find them usually in
C:\Users\USERNAME\Pictures\Frontier Developments\Elite Dangerous

Owners of Nvidia video cards and use DSR technology to increase the resolution 
for screenshots and revert it back to normal without leaving the game.

Usage
--------------
Run EliteOCR.py
Click "Choose Image" and select your screenshot.
Check if the values have been recognised properly. Optionally correct them and click
on "Save and Next" to continue to next line. 
You can edit the values in the table by double clicking on the entry.

After processing one screenshot you can add another of the same station. Should
there be repeated entry, you can click "Skip" to continue to next line without
adding current one to the list.

When you have all the entries of one stations commodity market in the table click
on "Export" to save your results to a csv-file. (separated by ; )
CSV can be opened by most spreadsheet editors like Excel, LibreOffice Calc etc.
