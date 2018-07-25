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



def cropLatticeFrame(frame,center,margin):
    zMax,yMax,xMax = frame.shape
    startx = max(center[0]-margin[0],0)
    endx = min(center[0]+margin[0],xMax)

    starty = max(center[1]-margin[1],0)
    endy = min(center[1]+margin[1],yMax)

    startz = max(center[2]-margin[2],0)
    endz = min(center[2]+margin[2],xMax)

    return frame[startz:endz,starty:endy,startx:endx]


# taks a tiff file as a numpy array as input (what you get when you read a
# tiff file with scikit image)
# and computes the maximum intensity projection
def maxIntensityProjection(latticeMovieFrame):

    f, axarr = plt.subplots(1,3,dpi=300)

    axarr[0].imshow(np.max(latticeMovieFrame,axis=0))
    axarr[0].set_xlabel('x')
    axarr[0].set_ylabel('y')
    axarr[0].invert_yaxis()


    axarr[1].imshow(np.max(latticeMovieFrame,axis=1))
    axarr[1].set_xlabel('x')
    axarr[1].set_ylabel('z')
    axarr[1].invert_yaxis()



    axarr[2].imshow(np.max(latticeMovieFrame,axis=2))
    axarr[2].set_xlabel('y')
    axarr[2].set_ylabel('z')
    axarr[2].invert_yaxis()

    plt.tight_layout()

    plt.show()
