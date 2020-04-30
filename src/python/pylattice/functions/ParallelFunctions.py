#by Joh Schoeneberg 2019, all rights reserved

import numpy as np
import skimage.external.tifffile
import os
import matplotlib.pyplot as plt
from PIL import Image



# open tiff windows proof -------------------------------------------------------------------------------------


from PIL import Image
def open2dTiff(path):

    img = Image.open(path)

    numFrames = img.n_frames
    imgArray = np.zeros( ( numFrames,img.size[1], img.size[0] ),np.uint16 )

    img.seek(0)
    imgArray = np.array(img)

    return imgArray


def open3dTiff(path):

    img = Image.open(path)

    numFrames = img.n_frames
    imgArray = np.zeros( ( numFrames,img.size[1], img.size[0] ),np.uint16 )

    for i in range(0,numFrames):
        img.seek(i)
        imgArray[i,:,:] = np.array(img)

    return imgArray


# rescaling 2D -------------------------------------------------------------------------------------

# not windows proof
from skimage.transform import rescale, resize
def rescale2D_16bit(inputFolder,outputFolder,file,scalingFactor):


    inputPath = os.path.join(inputFolder, file)


    image2D = open2dTiff(inputPath)
    #print(latticeMovieStack.shape)

    image2D_processed = resize(image2D, (image2D.shape[0] / scalingFactor, image2D.shape[1] / scalingFactor),anti_aliasing=True)
    image2D_processed = image2D_processed/np.max(image2D_processed)*65535


    #output_folder = Path(outputFolder)
    outputPath = os.path.join(outputFolder, file)
    #print(outputPath)
    skimage.external.tifffile.imsave(outputPath,image2D_processed.astype('uint16'))

    return outputPath




# cropping -------------------------------------------------------------------------------------

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

# correct decon artifacts ----------------------------------------------------------------------

def correct_decon_boundary_artifact_for_single_slice(oneSlice,margin=20,verbose=False):

    summed = np.sum(oneSlice,axis=0)
    all_zero = np.where(summed==0)[0]
    all_nonZero = np.where(summed!=0)[0]

    middle = np.average(np.where(summed!=0))
    leftBoundary = np.max(all_zero[all_zero<middle])
    rightBoundary = np.min(all_zero[all_zero>middle])


    #correctedSlice = np.copy(stack[sliceIndex])
    correctedSlice = oneSlice
    correctedSlice[:,0:leftBoundary+margin]=0
    correctedSlice[:,rightBoundary-margin:correctedSlice.shape[1]]=0


    if(verbose):
        print("0:"+str(leftBoundary+margin))
        print(str(rightBoundary-margin)+":"+str(correctedSlice.shape[1]))

        plt.figure(dpi=150)
        plt.plot(summed,color='grey')
        #plt.axvline(middle,color='red')
        plt.axvline(leftBoundary, color='black')
        plt.axvline(rightBoundary, color='black')

        plt.axvline(leftBoundary+margin, color='blue')
        plt.axvline(rightBoundary-margin, color='blue')
        plt.show()

        plt.figure(dpi=150)
        plt.imshow(correctedSlice)

    return(correctedSlice)

def correctDecon_parallel(inputFolder,outputFolder,file,margin):

    inputPath = os.path.join(inputFolder, file)



    latticeMovieStack = open3dTiff(inputPath)
    #print(latticeMovieStack.shape)

    for i in range(0,latticeMovieStack.shape[0]):
    #remove the first and last slices from the new stack
        oneSlice = latticeMovieStack[i]
        if (i == 0 or i == latticeMovieStack.shape[0]-1):
            latticeMovieStack[i] = oneSlice[:,:]=0
        else:
            latticeMovieStack[i] = correct_decon_boundary_artifact_for_single_slice(oneSlice,verbose=False)

    outputPath = os.path.join(outputFolder, file)

    skimage.external.tifffile.imsave(outputPath,latticeMovieStack.astype('uint16'))


    return outputPath


# rotate -------------------------------------------------------------------------------------

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


# reslice -------------------------------------------------------------------------------------
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
