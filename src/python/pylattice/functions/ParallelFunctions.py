

import numpy as np
import skimage.external.tifffile
import os
import matplotlib.pyplot as plt
from PIL import Image

def cropLatticeFrame_core(frame,center,margin):
    zMax,yMax,xMax = frame.shape
    startx = max(center[0]-margin[0],0)
    endx = min(center[0]+margin[0],xMax)

    starty = max(center[1]-margin[1],0)
    endy = min(center[1]+margin[1],yMax)

    startz = max(center[2]-margin[2],0)
    endz = min(center[2]+margin[2],xMax)

    return frame[startz:endz,starty:endy,startx:endx]

def cropLatticeFrame(inputFolder,outputFolder,file,center,margin):
    inputPath = os.path.join(inputFolder, file)

    latticeMovieStack = open3dTiff(inputPath)
    #print(latticeMovieStack.shape)

    latticeMovieStack_processed = cropLatticeFrame_core(latticeMovieStack,center, margin)

    #output_folder = Path(outputFolder)
    outputPath = os.path.join(outputFolder, file)
    #print(outputPath)
    skimage.external.tifffile.imsave(outputPath,latticeMovieStack_processed.astype('uint16'))

    return outputPath


def open3dTiff(path):

    img = Image.open(path)

    numFrames = img.n_frames
    imgArray = np.zeros( ( numFrames,img.size[1], img.size[0] ),np.uint16 )

    for i in range(0,numFrames):
        img.seek(i)
        imgArray[i,:,:] = np.array(img)

    return imgArray

def rotate180_parallel(inputFolder,outputFolder,file):

    inputPath = os.path.join(inputFolder, file)

    #print(inputPath)

# this alternative somehow wont work
#    latticeMovieStack = skimage.external.tifffile.imread(inputPath)

    latticeMovieStack = open3dTiff(inputPath)
    #print(latticeMovieStack.shape)

    latticeMovieStack_rotated = np.rot90(latticeMovieStack,k=2, axes=(1, 2))

    #output_folder = Path(outputFolder)
    outputPath = os.path.join(outputFolder, file)
    #print(outputPath)
    skimage.external.tifffile.imsave(outputPath,latticeMovieStack_rotated.astype('uint16'))

    return outputPath



def reslice_top_parallel(inputFolder,outputFolder,file):

    inputPath = os.path.join(inputFolder, file)

    #print(inputPath)

# this alternative somehow wont work
#    latticeMovieStack = skimage.external.tifffile.imread(inputPath)

    latticeMovieStack = open3dTiff(inputPath)
    #print(latticeMovieStack.shape)

    atticeMovieStack_resliced = np.swapaxes(latticeMovieStack, 0,1)

    #output_folder = Path(outputFolder)
    outputPath = os.path.join(outputFolder, file)
    #print(outputPath)
    skimage.external.tifffile.imsave(outputPath,atticeMovieStack_resliced.astype('uint16'))

    return outputPath
