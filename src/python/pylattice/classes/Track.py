# by Joh Schoeneberg 2018
# All rights reserved

import numpy as np
import math

import skimage
import json

import matplotlib.pyplot as plt

class Track:
    """Class for a processed track.


    Attributes
    ----------
    pandasTrackData : pandas.df
        the dataframe that comes from the matlab2csv function

    latticeFrameShape : np.array([int,int,int])
        the shape of the original image where the tracks come from

    """
    def __init__(self,pandasTrackData):
        tracklength = int((pandasTrackData['tracklength'].values)[0])


        track = pandasTrackData[0:tracklength]

        self.id = track['trackId'].astype(int).values[0]
        self.frameId = []


        for frameID in track['frameId'].values:
            if(frameID == ' NaN'):
                self.frameId.append(None)
            else:
                self.frameId.append(int(frameID))
        self.len = tracklength

        self.m_coords = track[['m_x','m_y','m_z']].astype(float).values
        self.s_coords = track[['s_x','s_y','s_z']].astype(float).values


        self.m_cm = np.nanmean(self.m_coords,axis=0)
        self.s_cm = np.nanmean(self.s_coords,axis=0)
        self.m_maxDist = np.linalg.norm(self.m_coords[0]-self.m_coords[-1])
        self.s_maxDist = np.linalg.norm(self.s_coords[0]-self.s_coords[-1])

        #self.particleIDs = track['particleId'].astype(int).values
        self.m_A = track['m_A'].astype(float).values
        self.m_Amean = np.nanmean(self.m_A)

        self.s_A = track['m_A'].astype(float).values
        self.s_Amean = np.nanmean(self.s_A)

        #self.frameIDs = track['frameId'].astype(int).values

    def reveal(self):
        print('id',self.id)
        print('tracklength',self.len)
        print('center of mass',self.cm)
        print('coords',self.coords)
        #print('particleIDs',self.particleIDs)
        print('A',self.A)
        print('frameIDs',self.frameIDs)


    def plot(self):
        plt.figure(dpi=300)
        ax = plt.axes(projection='3d')
        ax.plot3D(self.coords[:,0], self.coords[:,1], self.coords[:,2], 'grey')
        ax.scatter3D(self.coords[:,0], self.coords[:,1], self.coords[:,2],c=self.A, cmap='plasma',s=100);
        plt.xlabel('x [px]')
        plt.ylabel('y [px]')

    def plot_xz(self):
        plt.figure(dpi=300)
        plt.plot(self.coords[:,0], self.coords[:,2], 'grey')
        plt.scatter(self.coords[:,0], self.coords[:,2],c=self.A, cmap='plasma',s=100);
        plt.xlabel('x [px]')
        plt.ylabel('z [px]')

    def plot_yz(self):
        plt.figure(dpi=300)
        plt.plot(self.coords[:,1], self.coords[:,2], 'grey')
        plt.scatter(self.coords[:,1], self.coords[:,2],c=self.A, cmap='plasma',s=100);
        plt.xlabel('y [px]')
        plt.ylabel('z [px]')



    def writeBILD(self,BILDfilename,latticeFrameShape,color='black',radius=0.5,center=[]):
        filename=BILDfilename
        file = open(BILDfilename,'w')

        file.write(".transparency 0.5\n")
        if(isinstance(color, str)):
            file.write(".color "+color+"\n")
        if(len(color)==3):
            file.write(".color "+str(color[0])+" "+str(color[1])+" "+str(color[2])+" \n")


        line = ".comment trackID"+str(self.id)+"\n"
        file.write(line)



        for i in range(1,self.len):
            tzero = self.m_coords[i-1]
            tone = self.m_coords[i]
            if len(center) != 0:
                tzero = tzero-center
                tone = tone-center



            # Data for a three-dimensional line
            x0 = float(tzero[0])
            y0 = float(tzero[1])
            z0 = np.abs(float(tzero[2]) - latticeFrameShape[2])
            A0 = float(self.m_A[i-1])

            x1 = float(tone[0])
            y1 = float(tone[1])
            z1 = np.abs(float(tone[2])- latticeFrameShape[2])
            A1 = float(self.m_A[i])

            if(math.isnan(x0) or math.isnan(y0) or math.isnan(z0) or math.isnan(x1) or math.isnan(y1) or math.isnan(z1)):
                line = ".arrow "+str(x0)+" "+str(y0)+" "+str(z0)+" "+str(x1)+" "+str(y1)+" "+str(z1)+" "+str(radius)+"\n" #" "+str(radius)+"\n"
                print(line)
                file.write(".comment "+line)
                continue

            line = ".arrow "+str(x0)+" "+str(y0)+" "+str(z0)+" "+str(x1)+" "+str(y1)+" "+str(z1)+" "+str(radius)+"\n" #" "+str(radius)+"\n"
            file.write(line)

        file.close()
