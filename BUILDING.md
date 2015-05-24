Dependencies to run from source
--------------

#### Python 2.7

Windows:

* [https://www.python.org/downloads/](https://www.python.org/downloads/)

Mac:

* Use the pre-installed Python.

#### Numpy

Windows:

* [http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/](http://sourceforge.net/projects/numpy/files/NumPy/1.9.1/)

Mac:

* Use the pre-installed Numpy.

#### OpenCV

Windows:

* [http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.11/](http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.11/)
* Goto the opencv\build\python\2.7 folder.
* Copy cv2.pyd to C:\Python27\lib\site-packages.

Mac:

* [http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.11/opencv-2.4.11.zip](http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.11/opencv-2.4.11.zip)
* If you're aiming to build a standalone EliteOCR application, apply the following patch:

		diff -ur opencv-2.4.11-orig/CMakeLists.txt opencv-2.4.11/CMakeLists.txt
		--- opencv-2.4.11-orig/CMakeLists.txt	2015-02-25 03:10:30.000000000 +0000
		+++ opencv-2.4.11/CMakeLists.txt	2015-05-16 14:16:55.000000000 +0100
		@@ -339,8 +339,7 @@
		   endif()
		 endif()
		 
		-set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}")
		-set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
		+set(CMAKE_INSTALL_NAME_DIR ${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH})
		 
		 if(INSTALL_TO_MANGLED_PATHS)
		   set(OPENCV_INCLUDE_INSTALL_PATH ${OPENCV_INCLUDE_INSTALL_PATH}/opencv-${OPENCV_VERSION})
		diff -ur opencv-2.4.11-orig/cmake/OpenCVModule.cmake opencv-2.4.11/cmake/OpenCVModule.cmake
		--- opencv-2.4.11-orig/cmake/OpenCVModule.cmake	2015-02-25 03:10:30.000000000 +0000
		+++ opencv-2.4.11/cmake/OpenCVModule.cmake	2015-05-16 13:32:52.000000000 +0100
		@@ -589,7 +589,6 @@
		     ARCHIVE_OUTPUT_DIRECTORY ${LIBRARY_OUTPUT_PATH}
		     LIBRARY_OUTPUT_DIRECTORY ${LIBRARY_OUTPUT_PATH}
		     RUNTIME_OUTPUT_DIRECTORY ${EXECUTABLE_OUTPUT_PATH}
		-    INSTALL_NAME_DIR lib
		   )
		 
		   # For dynamic link numbering convenions

* Build a minimal configuration with:

		cmake . -DBUILD_ZLIB=OFF -DWITH_CUDA=OFF -DWITH_FFMPEG=OFF -DWITH_GSTREAMER=OFF -DWITH_JASPER=OFF -DWITH_JPEG=OFF -DWITH_OPENEXR=OFF -DWITH_PNG=OFF -DWITH_TIFF=OFF -DPYTHON_PACKAGES_PATH=/Library/Python/2.7/site-packages
		make install

#### Qt4
Windows:

* Included with PyQt4 below.

Mac:

* Download and install the "opensource" package from [http://download.qt.io/archive/qt/4.8/4.8.6/](http://download.qt.io/archive/qt/4.8/4.8.6/)

#### SIP
Windows:

* Included with PyQt4 below.

Mac:

* [http://www.riverbankcomputing.com/software/sip/download](http://www.riverbankcomputing.com/software/sip/download)
* Build with:

		python ./configure.py -b /usr/local/bin -e /usr/local/include -v /usr/local/share/sip
		make install

#### PyQt4

[http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)

Windows:

* Download and run the 32 or 64 bit installer for Qt4.8.6.

Mac:

* Download the "MacOS/X" source package and build with:

		python ./configure.py -b /usr/local/bin
    	make install

#### Other dependencies

    pip install qimage2ndarray openpyxl ezodf lxml python-Levenshtein pytz tzlocal requests grequests bitarray BeautifulSoup4


Running from source
--------------
Run EliteOCR.py


To create a standalone application
--------------

Windows:

    pip install pyinstaller
    python make.py

Mac:

* [https://github.com/sparkle-project/Sparkle/releases/latest](https://github.com/sparkle-project/Sparkle/releases/latest)
* Copy Sparkle.framework to /Library/Frameworks

    	easy_install -U py2app
    	./make.sh


Run on Ubuntu
--------------

It is useful to run EliteOCR from a separate computer and access the files as network shares
(screenshots, log files and AppConfig.xml).

#### Install dependencies

    sudo apt-get install python-pip python-qt4 python-opencv python-numpy python-openpyxl python-requests python-bitarray python-tz python-gevent python-levenshtein python-lxml
    sudo pip install tzlocal grequests qimage2ndarray ezodf
