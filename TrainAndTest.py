# TrainAndTest.py

import cv2
import numpy as np
import operator
import os


# module level variables ##########################################################################
MIN_CONTOUR_AREA = 18

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

CONFIX_FOR_INV = 128
CONFIX_DISTANCE = 13000000.
###################################################################################################
class ContourWithData():

    # member variables ############################################################################
    npaContour = None           # contour
    boundingRect = None         # bounding rect for contour
    intRectX = 0                # bounding rect top left corner x location
    intRectY = 0                # bounding rect top left corner y location
    intRectWidth = 0            # bounding rect width
    intRectHeight = 0           # bounding rect height
    fltArea = 0.0               # area of contour

    def calculateRectTopLeftPointAndWidthAndHeight(self):               # calculate bounding rect info
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
        if self.fltArea < MIN_CONTOUR_AREA: return False        # much better validity checking would be necessary
        return True

###################################################################################################
def recg(img):
    allContoursWithData = []                # declare empty lists,
    validContoursWithData = []              # we will fill these shortly

    try:
        npaClassifications = np.loadtxt("/var/www/flask_detect_number/classifications.txt", np.float32)                  # read in training classifications
    except:
        print ("error, unable to open classifications.txt, exiting program\n")
        #os.system("pause")
        return "1"
    # end try

    try:
        npaFlattenedImages = np.loadtxt("/var/www/flask_detect_number/flattened_images.txt", np.float32)                 # read in training images
    except:
        print ("error, unable to open flattened_images.txt, exiting program\n")
        #os.system("pause")
        return "2"
    # end try

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train
    #return "2.1"
    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object
    #return "2.2"
    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)
    #return "2.3"
    imgTestingNumbers = cv2.imread(img)          # read in testing numbers image
    #return "3"
    if imgTestingNumbers is None:                           # if image was not read successfully
        print ("error: image not read from file \n\n")      # print error message to std out
        #os.system("pause")                                  # pause so user can see error message
        return "4"                                              # and exit function (which exits program)
    # end if

    imgTestingNumbers = cv2.fastNlMeansDenoisingColored(imgTestingNumbers,None,20,20,7,21) #Denoise
    imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)       # get grayscale image
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    # blur

    ret,imgThresh = cv2.threshold(imgBlurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    FOR_INV = np.mean(imgThresh)
    
    if FOR_INV > CONFIX_FOR_INV:                                        # Checking Background-color Black/White
        imgThresh = cv2.bitwise_not(imgThresh)                          # invert so foreground will be white, background will be black

    kernel=np.ones((7,3),np.uint8)                                      # Kernel for Dilating
    #imgThresh = cv2.dilate(imgThresh,kernel,iterations=1)               # The Dilate increase image border size
    imgThresh = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, kernel)    # The Closing increase image border size
        
    imgThreshCopy = imgThresh.copy()        # make a copy of the thresh image, this in necessary b/c findContours modifies the image

    npaContours, npaHierarchy = cv2.findContours(imgThreshCopy,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

    for npaContour in npaContours:                             # for each contour
        contourWithData = ContourWithData()                                             # instantiate a contour with data object
        contourWithData.npaContour = npaContour                                         # assign contour to contour with data
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                    # get bounding rect info
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
        allContoursWithData.append(contourWithData)                                     # add contour with data object to list of all contours with data
    # end for

    for contourWithData in allContoursWithData:                 # for all contours
        if contourWithData.checkIfContourIsValid():             # check if valid
            validContoursWithData.append(contourWithData)       # if so, append to valid contour list
        # end if
    # end for

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))         # sort contours from left to right
    strFinalString = ""         # declare final string, this will have the final number sequence by the end of the program

    for contourWithData in validContoursWithData:            # for each contour
                                                # draw a green rect around the current char
        cv2.rectangle(imgTestingNumbers,                                        # draw rectangle on original testing image
                      (contourWithData.intRectX, contourWithData.intRectY),     # upper left corner
                      (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),      # lower right corner
                      (0, 255, 0),              # green
                      2)                        # thickness

        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,     # crop char out of threshold image
                           contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             # resize image, this will be more consistent for recognition and storage

        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))      # flatten image into 1d numpy array

        npaROIResized = np.float32(npaROIResized)       # convert from 1d numpy array of ints to 1d numpy array of floats

        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)     # call KNN function find_nearest
        
        if dists > CONFIX_DISTANCE:  #if Distance more standad
            continue
            

        strCurrentChar = str(chr(int(npaResults[0][0])))            # get character from results

        strFinalString = strFinalString + strCurrentChar            # append current char to full string
        
    # end for

    cv2.destroyAllWindows()             # remove windows from memory

    return strFinalString

###################################################################################################
if __name__ == "__main__":
    b = "test8.png"
    var = recg(b)
    print(var)

# end if
