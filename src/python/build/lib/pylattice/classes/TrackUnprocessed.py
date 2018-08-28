# by Joh Schoeneberg 2018
# All rights reserved

import numpy as np
import math

import skimage
import json


class TrackUnprocessed:
    """Class for an unprocessed track.


    Attributes
    ----------
    pandasTrackData : pandas.df
        the dataframe that comes from the matlab2csv function

    latticeFrameShape : np.array([int,int,int])
        the shape of the original image where the tracks come from

    """
    def __init__(self,pandasTrackData):
        tracklength = int((pandasTrackData['tracklength'].values)[0])

        #trim the end of the track until you got rid of all the nans
        xCoordLastEntry = pandasTrackData[tracklength-1:tracklength]['x'].astype(float).values
        #print(xCoordLastEntry,tracklength)
        while np.isnan(xCoordLastEntry):
            tracklength = tracklength-1
            xCoordLastEntry = pandasTrackData[tracklength-1:tracklength]['x'].astype(float).values
            #print(xCoordLastEntry,tracklength)

        track = pandasTrackData[0:tracklength] # this function kills all the NaNs that come from matlab

        self.id = track['trackId'].astype(int).values[0]
        self.len = tracklength

        self.coords = track[['x','y','z']].astype(float).values


        self.cm = np.nanmean(self.coords,axis=0)
        self.maxDist = np.linalg.norm(self.coords[0]-self.coords[-1])

        self.particleIDs = track['particleId'].astype(int).values
        self.A = track['A'].astype(float).values
        self.Amean = np.nanmean(self.A)

        self.frameIDs = track['frameId'].astype(int).values

    def reveal(self):
        print('id',self.id)
        print('tracklength',self.len)
        print('center of mass',self.cm)
        print('coords',self.coords)
        print('particleIDs',self.particleIDs)
        print('A',self.A)
        print('frameIDs',self.frameIDs)


    def plot(self):
        plt.figure(dpi=300)
        ax = plt.axes(projection='3d')
        ax.plot3D(self.coords[:,0], self.coords[:,1], self.coords[:,2], 'grey')
        ax.scatter3D(self.coords[:,0], self.coords[:,1], self.coords[:,2],c=self.A, cmap='plasma',s=100);
        plt.xlabel('x [px]')
        plt.ylabel('y [px]')

    def writeBILD(self,BILDfilename,color='black',center=[]):
        filename=BILDfilename
        file = open(BILDfilename,'w')

        file.write(".transparency 0.5\n")
        file.write(".color "+color+"\n")

        line = ".comment trackID"+str(self.id)+"\n"
        file.write(line)



        for i in range(1,self.len):
            tzero = self.coords[i-1]
            tone = self.coords[i]
            if len(center) != 0:
                tzero = tzero-center
                tone = tone-center



            # Data for a three-dimensional line
            x0 = float(tzero[0])
            y0 = float(tzero[1])
            z0 = float(tzero[2])
            A0 = float(self.A[i-1])

            x1 = float(tone[0])
            y1 = float(tone[1])
            z1 = float(tone[2])
            A1 = float(self.A[i])

            if(math.isnan(x0) or math.isnan(y0) or math.isnan(z0) or math.isnan(x1) or math.isnan(y1) or math.isnan(z1)):
                line = ".arrow "+str(x0)+" "+str(y0)+" "+str(z0)+" "+str(x1)+" "+str(y1)+" "+str(z1)+"\n" #" "+str(radius)+"\n"
                print(line)
                file.write(".comment "+line)
                continue

            line = ".arrow "+str(x0)+" "+str(y0)+" "+str(z0)+" "+str(x1)+" "+str(y1)+" "+str(z1)+"\n" #" "+str(radius)+"\n"
            file.write(line)

        file.close()
