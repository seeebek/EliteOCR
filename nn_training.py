import random
import sys
import time
import ntpath
import os
from os.path import dirname, realpath
import cv2
import numpy
from settings import Settings


class nnTraining:
    def __init__(self):
        settings = Settings()
        self.trainingImageDir = dirname(settings.app_path + os.sep + "nn_training_images" + os.sep
        self.splitTrainingImageFolderName = 'split_training_images'
        self.splitTrainingImageDir = self.trainingImageDir + self.splitTrainingImageFolderName + os.sep

        self.checkAndMakeDir(self.trainingImageDir)
        self.checkAndMakeDir(self.splitTrainingImageDir)

        self.minSegmentArea = 600
        self.maxSegmentWidth = 0
        self.maxSegmentHeight = 0

    def checkAndMakeDir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def getImageList(self):
        #@TODO: store images already converted, and filter them from this list
        trainingImageNames = os.listdir(self.trainingImageDir)
        trainingImageNames.remove(self.splitTrainingImageFolderName)
        return map(lambda trainingImageNames: self.trainingImageDir + trainingImageNames, trainingImageNames)

    def processImages(self, imageFilePaths, objectColor, threshold):
        processedImages = []
        for i, imageFilePath in zip(range(0, len(imageFilePaths) - 1), imageFilePaths):
            if i%100 == 0.0:
                print 'Chopped', i, 'images so far...'
            processedImages.append(self.processImage(imageFilePath, objectColor, threshold))
        return processedImages

    def processImage(self, imageFilePath, objectColor, threshold):
        if type(imageFilePath) == list:
            return self.processImages(imageFilePath, objectColor, threshold)
        img = cv2.imread(imageFilePath)
        head, tail = ntpath.split(imageFilePath)
        value, rand = tail.split('_')
        res = [0, 0]  # @TODO: return original source image resolution
        imgBig = self.scaleImageToHeight(img, 100)
        segments = self.segmentImage(imgBig, objectColor, threshold)
        for val, segment in zip(value, segments):
            #cv2.imshow('asd', numpy.asarray(segment[0]))
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()

            cv2.imwrite(self.splitTrainingImageDir + val + '_' + rand + '.png', segment[0])
            s = segment[0]
            h = len(s)
            w = len(s[0])
            self.trackMaxSegmentSize(w, h)
        return [value, res, segments]

    def trackMaxSegmentSize(self, width, height):
        if width > self.maxSegmentWidth:
            self.maxSegmentWidth = width
        if height > self.maxSegmentHeight:
            self.maxSegmentHeight = height

    def segmentImage(self, img, objectColor, threshold):
        horizontalSlices = []
        verticalSlices = self.segmentImageVertical(img, objectColor, threshold)  #first we segment vertically
        for verticalSlice in verticalSlices:
            if len(verticalSlice):
                horizontalSlice = self.segmentImageHorizontal(verticalSlice, objectColor, threshold)  #then we segment those segments horizontally
                if len(horizontalSlice):
                    horizontalSlices.append(horizontalSlice)
        return horizontalSlices

    def scaleImageToHeight(self, img, newHeight):
        h = float(img.shape[0])
        w = float(img.shape[1])
        ratio = (newHeight / h)
        newWidth = int(round(w * ratio, 0))
        return cv2.resize(img, (newWidth, newHeight))

    def segmentImageHorizontal(self, img, objectColor, threshold):
        imgBig = img
        height = len(imgBig)
        width = len(imgBig[0])
        horizontalBounds = []
        topSide = -1
        matched = False
        for y in range(0, height - 1):
            for x in range(0, width - 1):
                if self.colorMatch(imgBig[y][x], objectColor, threshold):  #we found objectColor
                    matched = True
            if matched:
                if topSide < 0:  #we don't have a value for the topSide yet, so this must be the first horizontal
                    topSide = max(y - 1, 0)  #move one up (if we can) to capture any potential antialiasing we may have missed through threshold

            else:  #we're off objectColor
                if topSide >= 0:  #if we've already found the topSide, then this must be the bottom one
                    horizontalBounds.append([topSide, y])
                    topSide = -1
            matched = False

        #print 'image dimensions: ' + str(width) + 'x' + str(height), len(imgBig[0][0])
        imageSlices = []
        for horizontalBound in horizontalBounds:
            y = horizontalBound[0]
            h = horizontalBound[1] - y
            x = 0
            w = width
            if w * h > self.minSegmentArea:  #remove pesky commas/periods from the images
                imageSlices.append(numpy.array(imgBig[y:y + h, x:x + w]))
                #cv2.rectangle(imgBig, (x, y), (x + w, y + h), (0, 255, 0), 1)
        return numpy.array(imageSlices)

    def segmentImageVertical(self, img, objectColor, threshold):
        imgBig = img
        height = len(imgBig)
        width = len(imgBig[0])
        verticalBounds = []
        leftSide = -1
        matched = False

        for x in range(0, width - 1):
            for y in range(0, height - 1):
                if self.colorMatch(imgBig[y][x], objectColor, threshold):  #we found objectColor
                    matched = True
            if matched:
                if leftSide < 0:  #we don't have a value for the left side yet, so this must be the first vertical
                    leftSide = max(x - 1, 0)  #move one left (if we can) to capture any potential antialiasing we may have missed through threshold

            else:  #we are off objectColor
                if leftSide >= 0:  #if we've already found the left side, then this must be the right one
                    verticalBounds.append([leftSide, x + 1])
                    leftSide = -1
            matched = False

        #print 'image dimensions: ' + str(width) + 'x' + str(height), len(imgBig[0][0])
        imageSlices = []
        for verticalBound in verticalBounds:
            x = verticalBound[0]
            w = verticalBound[1] - x
            y = 0
            h = height
            if w * h > self.minSegmentArea:  #remove pesky commas/periods from the images
                imageSlices.append(numpy.array(imgBig[y:y + h, x:x + w]))
                #cv2.rectangle(imgBig, (x, y), (x + w, y + h), (0, 255, 0), 1)
        return imageSlices

    def colorMatch(self, color1, color2, threshold):
        dist = 0.0
        for c1, c2 in zip(color1, numpy.asarray(color2)):
            dist += pow((c1 - c2), 2)
        return pow(dist, 0.5) <= threshold


print 'Conversion of images beginning...'
train = nnTraining()
imgList = train.getImageList()
imgPaths = imgList  #[0:10]
#imgPaths = './nn_training_images/1462_1417536191-38695.png'
print 'Found', len(imgPaths), 'images to chop'
print 'Chopping...'
train.processImage(imgPaths, [0, 0, 0], 350)
print 'Chopping completed.'
print 'Max digit image dimensions:', train.maxSegmentWidth, train.maxSegmentHeight

cv2.waitKey(0)
