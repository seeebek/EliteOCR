import cv2
import sys
import numpy as np
from PyQt4 import QtGui as qt

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
    
def adjustTableImg(img, factor):
    h, w, c = img.shape
    workimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b,g,r  = cv2.split(img)
    b = contBright(b, 100.0, 255.0)
    ret, b = cv2.threshold(b,100,255,cv2.THRESH_BINARY)
    b = cv2.GaussianBlur(b,(51,41),0)
    ret,b = cv2.threshold(b,1,255,cv2.THRESH_BINARY)
    workimg = cv2.subtract(workimg, b)
    #temp = cv2.resize(workimg, (0,0), fx=0.4, fy=0.4)
    #cv2.imshow('image', temp)
    #cv2.waitKey(0)
    return workimg

def removeTooBright(img, orig):
    workimg = img[:]
    workimg = contBright(workimg, 100.0, 255.0)
    ret, workimg = cv2.threshold(workimg,100,255,cv2.THRESH_BINARY)
    workimg = cv2.GaussianBlur(workimg,(51,41),0)
    ret,workimg = cv2.threshold(workimg,1,255,cv2.THRESH_BINARY)
    workimg = cv2.subtract(orig, workimg)
    return workimg
    
def stationOrange(img):
    workimg = img[:]
    b,g,r  = cv2.split(workimg)
    b_inv = np.subtract(255.0, b)
    new = np.maximum(np.subtract(b, b_inv), 0.0)
    workimg = np.subtract(255.0, new)
    workimg = toCV(workimg)
    return workimg
    
def stationBlue(img):
    workimg = img[:]
    b,g,r  = cv2.split(workimg)
    new = np.subtract(255.0, r)
    workimg = contBright(new, 0, 160)
    #workimg = toCV(workimg)
    #cv2.imshow('image', workimg)
    #cv2.waitKey(0)
    return workimg

def cleanOrange(img):
    workimg = img[:]
    b,g,r  = cv2.split(workimg)
    r = np.add(r, 0.0) 
    new = np.subtract(np.add(r,g), 128.0)
    new = toCV(new)
    workimg = removeTooBright(b, new)
    workimg = 255.0 - workimg
    workimg = toCV(workimg)
    return workimg
 
def cleanBlue(img):
    workimg = img[:]
    b,g,r  = cv2.split(workimg)
    #r = np.add(r, 0.0) 
    new = np.add(r, 255.0-b)
    new = toCV(new)
    workimg = contBright(new, 0, 180)
    #workimg = removeTooBright(b, new)
    #workimg = 255.0 - workimg
    #workimg = toCV(workimg)
    #cv2.imshow('image', workimg)
    #cv2.waitKey(0)
    return workimg
    
def makeCleanImage(img, item):
    if item.hud_color == 0:
        return cleanOrange(img)
    elif item.hud_color == 1:
        return cleanBlue(img)
    else:
        return cleanOrange(img)
       
def makeCleanStationImage(img, item):
    if item.hud_color == 0:
        return stationOrange(img)
    elif item.hud_color == 1:
        return stationBlue(img)
    else:
        return stationOrange(img)
    
    

