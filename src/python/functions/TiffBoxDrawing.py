# by Joh Schoeneberg 2018
# All rights reserved

import numpy as np
import matplotlib.pyplot as plt

def getCubeMeshIndexes(cubeSize = 5, center=[0,0,0]):
# this is 5 on each side of the center
#center=np.array([224.29615185,362.37867407,45.60376889])
    indexes = []
    limits = np.array([-cubeSize,+cubeSize])
    for i in range(limits[0]-2,limits[1]+2):
        for j in  range(limits[0]-2,limits[1]+2):
            for k in range(limits[0]-2,limits[1]+2):
                value = 0
                if i in (limits+center[0]) and j in (limits+center[1]) and ((k > (limits+center[2])[0]) and (k < (limits+center[2])[1])) :
    #                print(limits+centerOfImage[0]+coord[0])
    #                print(limits+centerOfImage[1]+coord[1])
                    indexes.append([i,j,k])
                if j in limits+center[1] and k in limits+center[2] and ((i > (limits+center[0])[0]) and (i < (limits+center[0])[1])) :
                    indexes.append([i,j,k])
                if k in limits+center[2] and i in limits+center[0] and ((j > (limits+center[1])[0]) and (j < (limits+center[1])[1])) :
                    indexes.append([i,j,k])
    return(indexes)




def getRidOfNegativeIndexes(indexesArray):
    newIndexes = []
    for index in indexesArray:
        if(np.min(index)>=0):
            newIndexes.append(index)
    return(np.array(newIndexes))



def getIndexesWhereAllArrayEntriesArePositive(indexesArray):
    ''' used to draw boxes around coordinates in a tiff file '''
    newIndexes = []
    for i in range(0,len(indexesArray)):
        index=indexesArray[i]
        if(np.min(index)>=0):
            newIndexes.append(i)
    return(np.array(newIndexes))


def indexOk(index, imageSize):
    if index[0] < 0:
        return False
    if index[1] <0:
        return False
    if index[2] < 0:
        return False
    if index[0] >= imageSize[0]:
        return False
    if index[1] >= imageSize[1]:
        return False
    if index[2] >= imageSize[2]:
        return False
    return True



def cropLatticeFrame(frame,center,margin):
    zMax,yMax,xMax = frame.shape
    startx = max(center[0]-margin[0],0)
    endx = min(center[0]+margin[0],xMax)

    starty = max(center[1]-margin[1],0)
    endy = min(center[1]+margin[1],yMax)

    startz = max(center[2]-margin[2],0)
    endz = min(center[2]+margin[2],xMax)

    return frame[startz:endz,starty:endy,startx:endx]


def cropLatticeFrameFillWithZero(frame,center,margin,shape):
    #e.g. [100,100,100]
    image = np.zeros(shape)

    zMax,yMax,xMax = frame.shape
    startx = max(center[0]-margin[0],0)
    endx = min(center[0]+margin[0],xMax)

    starty = max(center[1]-margin[1],0)
    endy = min(center[1]+margin[1],yMax)

    startz = max(center[2]-margin[2],0)
    endz = min(center[2]+margin[2],zMax)

    croppedImage = frame[startx:endx,starty:endy,startz:endz]

    for x in range(startx-center[0]-margin[0],endx-center[0]-margin[0]):
        for y in range(starty-center[1]-margin[1],endy-center[1]-margin[1]):
            for z in range(startz-center[2]-margin[2],endz-center[2]-margin[2]):
                image[x,y,z] = croppedImage[x-(startx-center[0]-margin[0]),y-(starty-center[1]-margin[1]),z-(startz-center[2]-margin[2])]

    return image
