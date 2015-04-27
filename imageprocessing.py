# -*- coding: utf-8 -*-
import cv2
import sys
import numpy as np
from PyQt4 import QtGui as qt

"""
def memory():
    import os
    from wmi import WMI
    w = WMI('.')
    result = w.query("SELECT WorkingSet FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=%d" % os.getpid())
    print int(result[0].WorkingSet)/1048576
    return int(result[0].WorkingSet)
"""

def contBright(value, in_min, in_max):
    """ Adjust brightness and contrast of image provided as array
    in value. Comparable to "Levels" in GIMP.
    """
    value = np.divide(np.subtract(value, float(in_min)), (float(in_max)-float(in_min)))
    value = np.multiply(value, 255.0)
    value = np.clip(value, 0, 255)
    value = value.astype(np.uint8)
    #temp = cv2.resize(value, (0,0), fx=0.4, fy=0.4)
    #cv2.imshow('image', temp)
    #cv2.waitKey(0)
    return value
    
def toCV(value):
    value = np.clip(value, 0, 255)
    value = value.astype(np.uint8)
    return value
    
def whiteBalance(value):
    hist = cv2.calcHist([value],[0],None,[100],[0,256])
    cv2.normalize(hist,hist,0,1000,cv2.NORM_MINMAX)
    #print max(hist)
    minimum = 0
    min_flag = True
    maximum = 255
    for i in range(len(hist)):
        if min_flag and hist[i] < 990:
            minimum = i
        else:
            min_flag = False
        if not min_flag and hist[i] > 0.75:
            maximum = i
            
    #if maximum > 240:
    #    maximum = 240
    value = contBright(value, maximum+30, maximum+40)
    return value

