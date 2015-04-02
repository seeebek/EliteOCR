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
    


    
    

