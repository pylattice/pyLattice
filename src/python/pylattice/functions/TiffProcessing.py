# by Joh Schoeneberg 2018
# All rights reserved

import numpy as np
import matplotlib.pyplot as plt


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

def cropLatticeFrame(frame,center,margin):
    zMax,yMax,xMax = frame.shape
    startx = max(center[0]-margin[0],0)
    endx = min(center[0]+margin[0],xMax)

    starty = max(center[1]-margin[1],0)
    endy = min(center[1]+margin[1],yMax)

    startz = max(center[2]-margin[2],0)
    endz = min(center[2]+margin[2],xMax)

    return frame[startz:endz,starty:endy,startx:endx]
