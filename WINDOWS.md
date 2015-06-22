Dependencies to run from source on Windows
--------------

#### Python 2.7

* [https://www.python.org/downloads/](https://www.python.org/downloads/)

#### Numpy

* [http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/](http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/)

#### OpenCV

* [http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.11/](http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.11/)
* Goto the opencv\build\python\2.7 folder.
* Copy cv2.pyd to C:\Python27\lib\site-packages.

#### Qt4

* Included with PyQt4 below.

#### SIP

* Included with PyQt4 below.

#### PyQt4

[http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* Download and run the 32 or 64 bit installer for Qt4.8.6.


#### Other dependencies

    pip install qimage2ndarray openpyxl ezodf lxml python-Levenshtein pytz tzlocal requests grequests bitarray BeautifulSoup4


Running from source
--------------
Run EliteOCR.py

To create a standalone application
--------------
    pip install pyinstaller
    python make.py
