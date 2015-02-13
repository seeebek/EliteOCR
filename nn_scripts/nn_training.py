import ntpath
import os
import pickle
import glob

import cv2
import numpy as np
from shutil import move
from sklearn.externals import joblib
# workaround
import sklearn.utils.sparsetools._graph_validation
import sklearn.utils.lgamma
import sklearn.utils.weight_vector

from Singleton import Singleton



# Max digit image dimensions: 88 70
# Min digit image dimensions: 25 52

@Singleton
class nnTraining():
    def __init__(self, param):
        self.appPath = '.'
        if type(param) is not type(None):
            if param['app_path']:
                self.appPath = param['app_path']
        self.trainingImageDir = self.appPath + "/nn_training_images/"
        self.alreadyProcessedImageDir = self.trainingImageDir + "already_processed/"
        self.splitTrainingImageFolderName = 'split_training_images'
        self.splitTrainingImageDir = self.trainingImageDir + self.splitTrainingImageFolderName + "/"

        self.scriptsPath = self.appPath + "/nn_scripts/"
        self.logisticClassifierPickleFile = self.scriptsPath + 'logistic_classifier joblib 1418261392.04.pkl'  # 'logistic_classifier joblib 1418157939.2.pkl'
        self.rbmClassifierPickleFile = self.scriptsPath + 'rbm_classifier joblib 1418261392.06.pkl'  #'rbm_classifier joblib 1418157939.21.pkl'
        self.classifier = None

        self.checkAndMakeDir(self.trainingImageDir)
        self.checkAndMakeDir(self.splitTrainingImageDir)
        self.checkAndMakeDir(self.alreadyProcessedImageDir)

        self.segmentObjectColor = [0, 0, 0]
        self.segmentObjectColorThreshold = 149

        #This may be excessive
        self.resizeImageToHeight = 40
        self.resizeImageToHeightBeforeSave = self.resizeImageToHeight  #can save out to different dimensions
        self.paddedSegmentHeight = 40
        self.paddedSegmentWidth = 40

        #Improve accuracy by removing some antialiasing in places which confuse the NN (such as the gap in the number 6)
        self.cutoffPixelGrayscaleValue = 180

        #set all pixels to pure black if they are not pure white
        #Training was performed with this set to false!!!!!!!!
        self.convertGrayscaleToBlackAndWhite = False

        # Minimum pixel area to allow to be saved (this removes the , and . in number strings)
        self.minSegmentArea = self.resizeImageToHeight * 3

        self.maxSegmentWidth = 0
        self.maxSegmentHeight = 0
        self.minSegmentWidth = 500
        self.minSegmentHeight = 500

        #SEGMENTS; horizontal_segmentation, vertical_segmentation, segmentation_matching, segmentation_image, segmentation_text
        self.debugModes = []  #['horizontal_segmentation', 'vertical_segmentation', 'segmentation_image', 'segmentation_text']  #,        'segmentation_matching']


    def checkAndMakeDir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def doDigitPrediction(self, img):
        segments, errorflag = self.processImageToSegment(img, self.segmentObjectColor, self.segmentObjectColorThreshold)

        #np.reshape(digit, (-1, 40 * 40))[0]
        resultDigit = ''
        for segment in segments:
            imgPixelsAsFloat = np.asarray(self.convertSegmentPixelsToFloat(segment))
            rdigit = np.asarray(np.reshape(imgPixelsAsFloat, (-1, 40 * 40))[0], np.float32)
            result = self.classifier.predict(rdigit)
            resultDigit += str(int(result))
            #results.append(result)

        return (resultDigit, errorflag)

    def convertAllImagesToSegmentFiles(self):
        print 'Chopping of images to segments beginning...'
        unprocessedImageList = self.getUnprocessedImageList()
        imgPaths = unprocessedImageList  #[0:10]
        #imgPaths = './nn_training_images/1462_1417536191-38695.png'
        print 'Found', len(imgPaths), 'images to chop'
        print 'Chopping...'
        #processedImages =
        self.processImageFilesToSegments(imgPaths, self.segmentObjectColor, self.segmentObjectColorThreshold)
        print 'Chopping completed.'
        print 'Max digit image dimensions:', self.maxSegmentWidth, 'x', self.maxSegmentHeight
        print 'Min digit image dimensions:', self.minSegmentWidth, 'x', self.minSegmentHeight
        #return processedImages

    validClassifiers = ['logistic', 'rbm']

    def setClassifier(self, classifierType='logistic'):
        #print 'Setting classifier to: ' + classifierType
        if classifierType in self.validClassifiers:
            if classifierType == 'logistic':
                self.classifier = self.loadClassifierFromFile(self.logisticClassifierPickleFile)
            if classifierType == 'rbm':
                self.classifier = self.loadClassifierFromFile(self.rbmClassifierPickleFile)
        else:
            raise Exception("InvalidClassifierType")

    def loadClassifierFromFile(self, filePath):
        #print 'Loading classifier pickle file: ' + filePath
        if os.path.isfile(filePath):
            return joblib.load(filePath)
        else:
            print 'Classifier pickle file not found: ' + filePath
            raise Exception("ClassifierPickleFileNotFound")

    def convertSegmentPixelsToFloat(self, segment):
        segmentFloatArray = []
        for row in segment:
            for pixel in row:
                # we're dealing with grayscale, only need to check one value for speed
                segmentFloatArray.append(float(pixel[0]) / 255.0)
        return np.asarray(segmentFloatArray)

    def convertSegmentPixelsToInt(self, segment):
        segmentFloatArray = []
        for row in segment:
            for pixel in row:
                # we're dealing with grayscale, only need to check one value for speed
                segmentFloatArray.append(pixel[0])
        return np.asarray(segmentFloatArray)

    def getUnprocessedImageList(self):
        #@TODO: store images already converted, and filter them from this list
        return glob.glob(self.trainingImageDir + "*.*")

    def getUnprocessedSegmentsList(self, getPerturbs=False):
        #@TODO: store images already converted, and filter them from this list
        if not getPerturbs:
            def f(n):
                return not ('!' in n)

            return filter(f, glob.glob(self.splitTrainingImageDir + "*.*"))
        return glob.glob(self.splitTrainingImageDir + "*.*")

    def getAllSegmentArrayTuples(self, size='all', getPerturbs=False):
        segmentArrayFiles = self.getUnprocessedSegmentsList(getPerturbs)  #self.getUntrainedArraysList()
        if size is not 'all':
            rand = np.random.RandomState(321)
            shuffle = rand.permutation(len(segmentArrayFiles))
            segmentArrayFiles = np.asarray(segmentArrayFiles)[shuffle[0: size]]
        segments = []
        values = []
        for segmentArrayFile in segmentArrayFiles:
            segmentNameInfo = self.getInfoFromImageFilepath(segmentArrayFile)
            img = cv2.imread(segmentArrayFile)
            imgPixelsAsFloat = np.asarray(self.convertSegmentPixelsToFloat(img))
            segments.append(imgPixelsAsFloat)  #[:, :]
            values.append(segmentNameInfo['value'])
        return [np.asarray(np.float32(segments)), np.asarray(np.float32(values)), segmentArrayFiles]

    def processImageFilesToSegments(self, imageFilePaths, objectColor, threshold):
        segments = []
        total = float(len(imageFilePaths))
        '''imageFilePaths = [  'C:/Users/NoOne/Desktop/ED/EliteOCR/nn_training_images/1237751_1080x1920-1417761000-30842.png',
                            'C:/Users/NoOne/Desktop/ED/EliteOCR/nn_training_images/10453_1080x1920-1417862311-96480.png',
                            'C:/Users/NoOne/Desktop/ED/EliteOCR/nn_training_images/1094_1080x1920-1417862365-19282.png',
                            'C:/Users/NoOne/Desktop/ED/EliteOCR/nn_training_images/48096_1080x1920-1417889636-20600.png'
        ]'''
        for i, imageFilePath in enumerate(imageFilePaths):
            if i % 100 == 0.0:
                print 'Chopped', i, 'images so far', '(' + str(round(100.0 * float(i) / total, 4)) + '%)...'
            processedSegments = self.processImageFileToSegment(imageFilePath, objectColor, threshold)
            if processedSegments:
                #if there were multiple segments returned, as is usually the case, add them to the array
                segments = segments + processedSegments
                #Move image to avoid processing it again in future
                move(imageFilePath, self.alreadyProcessedImageDir)

        return segments

    def processImageToSegment(self, img, objectColor, threshold):
        segments = []
        imgBig = self.scaleImageToHeight(img, self.resizeImageToHeight)
        segments = self.segmentImage(imgBig, objectColor, threshold)
        #Make pixels lighter than a certain cutoff value whiter, help deal with problematic antialiasing (such as the gap in the number 6)
        paddedSegments = []
        errorflag = False

        for s, segment in enumerate(segments):
            for y, row in enumerate(segment[0]):
                for x, col in enumerate(row):
                    #print '!!!'
                    #print segments[s][0][y][x]
                    if self.convertGrayscaleToBlackAndWhite:
                        segments[s][0][y][x] = [0, 0, 0] if col[0] < self.cutoffPixelGrayscaleValue else [255, 255, 255]
                    else:
                        segments[s][0][y][x] = [255, 255, 255] if col[0] > self.cutoffPixelGrayscaleValue else col

            #make image fit into the bounds
            imgBig = self.scaleImageToHeight(segment[0], self.resizeImageToHeightBeforeSave)
            #print segment[0]
            h = len(imgBig)
            w = len(imgBig[0])
            # pad all the images- it's a trade-off between computation time (exponentially increasing neurons required) and accuracy (we don't want to miss any pixels)
            top_padding = int(round(float(self.paddedSegmentHeight - h) / 2.0, 0))
            bottom_padding = self.paddedSegmentHeight - top_padding - h
            left_padding = int(round(float(self.paddedSegmentWidth - w) / 2.0, 0))
            right_padding = self.paddedSegmentWidth - left_padding - w
            try:
                #cv2.rectangle(imgBig, (0, 0), (abs(w), abs(h)), (0, 0, 255), 1)
                #self.showImageAndWait(img)
                padded_s = cv2.copyMakeBorder(imgBig, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT, value=[255, 255, 255])
                paddedSegments.append(padded_s)
            except:
                errorflag = True
                print 'Failed to pad successfully!'
                print w, h, top_padding, bottom_padding, left_padding, right_padding

        return (paddedSegments, errorflag)

    def processImageFileToSegment(self, imageFilePath, objectColor, threshold, saveFile=False, doPerturb=False):
        """
        :type objectColor: list
        :type threshold: int
        :type imageFilePath: str
        """
        if type(imageFilePath) == list:
            return self.processImageFilesToSegments(imageFilePath, objectColor, threshold)
        processedSegments = []
        info = self.getInfoFromImageFilepath(imageFilePath)
        if info['value']:
            img = cv2.imread(imageFilePath)
            segments = []
            try:
                segments = self.processImageToSegment(img, objectColor, threshold)
            except:
                print 'ERROR MAKING PADDED IMAGE IN NN_TRAINING.PY @~218'
                print imageFilePath
                exit(0)

            if len(info['value']) != len(segments):
                print 'VALUE AND SEGMENTS MISMATCH: ', 'value:', [info['value'], len(info['value'])], 'segment length:', len(segments), imageFilePath
                return []

            for i, (val, segment) in enumerate(zip(info["value"], segments)):

                #save image out
                if saveFile:
                    segmentImageName = val + '_' + ((info['original_filename'].split('_'))[1]).replace('.' + info['ext'], '') + ' ' + str(i) + '.' + info['ext']
                    cv2.imwrite(self.splitTrainingImageDir + segmentImageName, segment)

                if doPerturb:
                    perturpedSegments = self.perturbSegment(segment)
                    for x, perturpedSegment in enumerate(perturpedSegments):
                        segmentImageName = val + '_' + ((info['original_filename'].split('_'))[1]).replace('.' + info['ext'], '') + ' ' + str(i) + '!perturb' + str(x) + '.' + info['ext']
                        cv2.imwrite(self.splitTrainingImageDir + segmentImageName, segment)

                if self.checkDebugMode('padded_segment'):
                    print 'Showing processed, padded segment'
                    self.showImageAndWait(segment)
                processedSegments.append([segment, info])

                #self.trackMaxSegmentSize(w, h)
        else:
            print 'could not find value from image!'
            print imageFilePath
        return processedSegments

    def perturbSegment(self, padded_s):
        perturbedSegments = []
        h = len(padded_s)
        w = len(padded_s[0])
        for xdir in range(1, 3):
            for ydir in range(1, 3):
                xMovement = 1 if xdir % 2 == 0 else -1
                yMovement = 1 if ydir % 2 == 0 else -1
                M = np.float32([[1, 0, xMovement], [0, 1, yMovement]])
                movedSegment = cv2.warpAffine(padded_s, M, (w, h))
                emptySides = []
                emptySides.append('left' if xMovement > 0 else 'right')
                emptySides.append('top' if yMovement > 0 else 'bottom')
                movedSegment = self.removeFullyBlackBoundary(movedSegment, emptySides)
                perturbedSegments.append(movedSegment)
        return perturbedSegments

    def removeFullyBlackBoundary(self, image, side='top'):
        if type(side) is not str:
            for s in side:
                image = self.removeFullyBlackBoundary(image, s)
            return image
        w = len(image[0])
        h = len(image)

        if side == 'top' or side == 'bottom':
            y = 0 if side == 'top' else h - 1
            for x in range(0, w):
                image[y][x] = [255, 255, 255]

        if side == 'left' or side == 'right':
            x = 0 if side == 'left' else w - 1
            for y in range(0, h):
                image[y][x] = [255, 255, 255]

        return image

    def getInfoFromImageFilepath(self, imageFilepath):
        filepath, imageName = ntpath.split(imageFilepath)
        return self.getInfoFromImageName(imageName)

    def getInfoFromImageName(self, imageFileName):
        #Starting imageName: 4_1080x1920-1417631392-19510 1.png
        info = {'value': '', 'resolution': [], 'timestamp': '', 'rand': '', 'ext': '', 'original_filename': imageFileName, 'sequence': ''}
        #4,  1080x1920-1417631392-19510 1.png
        info['value'], rightSide = imageFileName.split('_')
        #1080x1920,    1417631392,   19510 1.png
        resString, info['timestamp'], randAndExt = rightSide.split('-')
        #1080, 1920
        info['resolution'] = resString.split('x')
        if ' ' in randAndExt:
            #19510, 1.png
            info['rand'], seqAndExt = randAndExt.split(' ')
            info['sequence'], info['ext'] = seqAndExt.split('.')
        else:
            #19510, png
            info['rand'], info['ext'] = randAndExt.split('.')

        return info

    def trackMaxSegmentSize(self, width, height):
        self.maxSegmentWidth = max(self.maxSegmentWidth, width)
        self.maxSegmentHeight = max(self.maxSegmentHeight, height)
        self.minSegmentWidth = min(self.minSegmentWidth, width)
        self.minSegmentHeight = min(self.minSegmentHeight, height)

    def segmentImage(self, img, objectColor, threshold):
        horizontalSlices = []
        verticalSlices = self.segmentImageVertical(img, objectColor, threshold)  #first we segment vertically
        for verticalSlice in verticalSlices:
            if len(verticalSlice):
                horizontalSlice = self.segmentImageHorizontal(verticalSlice, objectColor, threshold)  #then we segment those segments horizontally
                if len(horizontalSlice):
                    horizontalSlices.append(horizontalSlice)
                else:
                    if self.checkDebugMode(['segmentation_text']):
                        print 'did not append slice: ', horizontalSlice
        return horizontalSlices

    def scaleImageToHeight(self, img, newHeight):
        """
        :type img: list
        :type newHeight: int
        """
        h = float(len(img))
        w = float(len(img[0]))
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
        if self.checkDebugMode(['horizontal_segmentation', 'segmentation_text']):
            print 'horizontal segmenting...'
            self.showImageAndWait(imgBig)
        for y in range(0, height):
            for x in range(0, width):
                if self.colorMatch(imgBig[y][x], objectColor, threshold):  #we found objectColor
                    matched = True
                    if self.checkDebugMode(['horizontal_segmentation', 'segmentation_matching', 'segmentation_text']):
                        print 'MATCH: ', imgBig[y][x]
                else:
                    if self.checkDebugMode(['horizontal_segmentation', 'segmentation_matching', 'segmentation_text']):
                        img[y][x] = [0, 255, 0]
                        print 'NOMATCH: ', imgBig[y][x]
            if matched:
                if topSide < 0:  #we don't have a value for the topSide yet, so this must be the first horizontal
                    topSide = max(y - 1, 0)  #move one up (if we can) to capture any potential antialiasing we may have missed through threshold
                else:
                    if y >= height - 1:
                        if self.checkDebugMode(['horizontal_segmentation', 'segmentation_text']):
                            print 'Ran into end of image during horizontal bounds check- setting bottom to end of image.'
                        horizontalBounds.append([topSide, y])
                        topSide = -1

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

            if self.checkDebugMode(['horizontal_segmentation', 'segmentation_text']):
                print 'Width * Height of segment: ', str(w * h), [w, h]
            if w * h > self.minSegmentArea:  #remove pesky commas/periods from the images
                imageSlices.append(np.array(imgBig[y:y + h, x:x + w]))
                if self.checkDebugMode(['horizontal_segmentation', 'segmentation_image']):
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    self.showImageAndWait(img)
            else:
                if self.checkDebugMode(['horizontal_segmentation', 'segmentation_text']):
                    print 'Skipping segment with w * h of: ' + str(w * h) + ' in horizontal segmentation '
                if self.checkDebugMode(['horizontal_segmentation', 'segmentation_image']):
                    self.showImageAndWait(img)
        return np.array(imageSlices)

    def segmentImageVertical(self, img, objectColor, threshold):
        imgBig = img
        height = len(imgBig)
        width = len(imgBig[0])
        verticalBounds = []
        leftSide = -1
        matched = False
        if self.checkDebugMode(['vertical_segmentation', 'segmentation_text']):
            print 'vertical segmenting...'
        for x in range(0, width):
            for y in range(0, height):
                if self.colorMatch(imgBig[y][x], objectColor, threshold):  #we found objectColor
                    matched = True
                    if self.checkDebugMode(['vertical_segmentation', 'segmentation_matching', 'segmentation_text']):
                        print 'MATCH: ', imgBig[y][x]
                else:
                    if self.checkDebugMode(['vertical_segmentation', 'segmentation_matching', 'segmentation_text']):
                        img[y][x] = [0, 255, 0]
                        print 'NOMATCH: ', imgBig[y][x]
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
        if self.checkDebugMode(['vertical_segmentation', 'segmentation_text']):
            print 'number of vertical bounds: ' + str(len(verticalBounds))
            print verticalBounds
        for verticalBound in verticalBounds:
            x = verticalBound[0]
            w = verticalBound[1] - x
            y = 0
            h = height
            #if w * h > self.minSegmentArea:  #remove pesky commas/periods from the images
            imageSlices.append(np.array(imgBig[y:y + h, x:x + w]))
            if self.checkDebugMode(['vertical_segmentation', 'segmentation_image']):
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)
                self.showImageAndWait(imgBig)
                #else:
                #    if self.checkDebugMode('vertical_segmentation'):
                #        print 'Skipping segment with w * h of: ' + str(w * h) + ' in vertical segmentation '

        return imageSlices

    def checkDebugMode(self, debugMode):
        if type(debugMode) is not list:
            return debugMode in self.debugModes
        else:
            debugIsSet = True
            for dm in debugMode:
                if dm not in self.debugModes:
                    debugIsSet = False
            return debugIsSet


    def colorMatch(self, color1, color2, threshold):
        dist = 0.0
        #for c1, c2 in zip(color1, np.asarray(color2)):
        #    dist += pow((c1 - c2), 2)
        #return pow(dist, 0.5) <= threshold
        #Shortcut for grayscale images
        return abs(color1[0] - color2[0]) < threshold

    def showImageAndWait(self, image, windowName='temp', timeToWait=0):
        cv2.imshow(windowName, image)
        cv2.waitKey(timeToWait)
        cv2.destroyWindow(windowName)


'''
def joinImgBelowSourceImg(sourceImg, ImgToJoin):
    #To stack vertically (img2 under img1):
    return np.concatenate((sourceImg, ImgToJoin), axis=0)


def joinImgToRightOfSourceImg(sourceImg, ImgToJoin):
    #To stack horizontally (img2 to the right of img1):
    return np.concatenate((sourceImg, ImgToJoin), axis=1)
'''

if __name__ == '__main__':

    from settings import Settings

    settings = Settings()
    param = {'app_path': settings.app_path}
    train = nnTraining.Instance(param)
    assert isinstance(train, type(nnTraining))

    # This is to convert all images into a usable form for training
    # train.convertAllImagesToSegmentFiles()

    testingFile = train.scriptsPath + 'ocr_test_image.png'
    img = cv2.imread(testingFile)
    train.setClassifier('logistic')
    print train.doDigitPrediction(img)
    cv2.waitKey(0)