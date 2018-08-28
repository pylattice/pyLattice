import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def determineApiBasoBoundary(punctaFilePaths,xrange = [0,500],yrange = [0,700], nbins = 20,verbose=False):

    allAverageZs = []
    for punctaFilePath in punctaFilePaths:


        data = pd.read_csv(punctaFilePath,header=0)
        data.columns = ["x","y","z","A"]

        # get all puncta

        idx = data.index[data['A'] > 0]

        # every axis is flippped in the matlab code (weird, I know)
        x = ((data['x']).loc[idx])
        y = ((data['y']).loc[idx])
        z = ((data['z']).loc[idx])

        #yrange = [np.min(y),np.max(y)]
        #xrange = [np.min(x),np.max(x)]

        xbinsize = (yrange[1]-yrange[0])/nbins
        ybinsize = (xrange[1]-xrange[0])/nbins

        xbins = np.arange(xrange[0], xrange[1]+1, xbinsize )
        ybins = np.arange(yrange[0], yrange[1]+1, ybinsize )
        zValues = []
        #print(bins)
        for i in range(1,len(xbins)):
            for j in range(1,len(ybins)):
                xleftThreshold = xbins[i-1]
                xrightThreshold = xbins[i]
                yleftThreshold = ybins[j-1]
                yrightThreshold = ybins[j]

                #filter out the z's that have the correct x range
                idx = data.index[(data['y'] > yleftThreshold)&(data['y'] < yrightThreshold)&(data['x'] > xleftThreshold)&(data['x'] < xrightThreshold)]
                z = ((data['z']).loc[idx])
                zValues.append([xleftThreshold,xrightThreshold,yleftThreshold,yrightThreshold,z.values])

        #print(zValues)
        averageZs = []
        for zValuePerBin in zValues:
            averageZs.append(np.array([zValuePerBin[0]+(zValuePerBin[1]-zValuePerBin[0])/2,zValuePerBin[2]+(zValuePerBin[3]-zValuePerBin[2])/2,np.average(zValuePerBin[-1])]))

        averageZs = np.array(averageZs)


        allAverageZs.append(averageZs)


    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')

    # load some test data for demonstration and plot a wireframe
    #X, Y, Z = axes3d.get_test_data(0.1)
    #ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5)

    #averageZs = allAverageZs[0]

    averagedThresholdOverAllFrames = np.nanmean(allAverageZs[0:-1],axis=0)
    averageZs = averagedThresholdOverAllFrames

    if(verbose):
        plt.figure(dpi=300)

        ax = plt.axes(projection='3d')
        #    plt.title(title)
        # Data for a three-dimensional line
        x = averageZs[:,0]
        y = averageZs[:,1]
        z = averageZs[:,2]

        #    ax.plot3D(x, y, z, 'gray')
        ax.scatter3D(x, y, z, cmap='cool',alpha=0.5,s=5);
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        xangle = 0#90
        yangle = -90
        ax.view_init(xangle, yangle)


    # postprocess the thresholds so that they work !
    # flip the z (mirror it)
    averagedThresholdOverAllFrames[:,2]=abs(averagedThresholdOverAllFrames[:,2]-120)
    return averagedThresholdOverAllFrames





def classifyTracks_lifetimeCohorts_apicalLateralBasal(trackIdsUsed, data, lifetimeCohorts, averagedThresholdOverAllFrames, interSpaceMargins,flipApiBaso=False, xrange = [0,500],yrange = [0,700], nbins = 20,SlaveMaxAfterPercentCohortLength=0.6):
    '''
    input:
    trackIdsUsed = [1,4,83,2] array of trackIds that get classified by this function
    data = pd.df dataframe that contains all information about all tracks
    lifetimeCohorts = [[0, 6], [6,12],[12,18],[18,24],[24,30],[30,70]] list of lifetime cohorts in seconds
    averagedThresholdOverAllFrames = this is the middle line in the cell layer
    interSpaceMargins = [15,5] #this is the value added[0]/subtracted[1] from the middle line for the inter classification
    flipApiBaso = False # depending on how the organoid sits, I have to flip apical and basolateral

    '''
#initialize the trackId array sorted by lifetime cohort
    trackIdsAssignedToCohorts_api = []
    trackIdsAssignedToCohorts_baso = []
    trackIdsAssignedToCohorts_inter = []
    for i in range(0,len(lifetimeCohorts)):
        trackIdsAssignedToCohorts_api.append(np.array([]))
        trackIdsAssignedToCohorts_baso.append(np.array([]))
        trackIdsAssignedToCohorts_inter.append(np.array([]))


    baso = False

    basoFirstXYZ=[]
    basoLifetimes=[]
    baso_mAmplitude=[]
    baso_sAmplitude=[]

    apiFirstXYZ=[]
    apiLifetimes=[]
    api_mAmplitude=[]
    api_sAmplitude=[]

    interFirstXYZ=[]
    interLifetimes=[]
    inter_mAmplitude=[]
    inter_sAmplitude=[]

    maxXIdxValue = max(averagedThresholdOverAllFrames[:,0])
    maxYIdxValue = max(averagedThresholdOverAllFrames[:,1])

    condition = -1 #0,1,2; api,inter,baso
    for trackId in trackIdsUsed:
        track = data[data['trackId'] == trackId]
        tracklength = track['tracklength'].values[0]
        m_intensity = track['m_A'].values.astype(float)
        s_intensity = track['s_A'].values.astype(float)
        maxIdx = np.argmax(s_intensity)
        # only include those tracks that do not have the dynamin peak in the first three frames

        m_firstX = track['m_x'].values.astype(float)[0]
        m_firstY = track['m_y'].values.astype(float)[0]
        m_firstZ = track['m_z'].values.astype(float)[0]

        xbinsize = (yrange[1]-yrange[0])/nbins
        ybinsize = (xrange[1]-xrange[0])/nbins

        #determine into which x-y-bin for the zThreshold this track belongs
        xIdxValue = int(np.floor(m_firstX/xbinsize))*xbinsize +xbinsize/2
        yIdxValue = int(np.floor(m_firstY/ybinsize))*ybinsize +ybinsize/2

        # if the puncta happens to be outside the grid, catch it again
        if(xIdxValue>maxXIdxValue):
            xIdxValue = maxXIdxValue
        if(yIdxValue>maxYIdxValue):
            yIdxValue = maxYIdxValue

        #print("{}. {}".format(xIdxValue,yIdxValue))
        indexForThresholdArray = np.where((averagedThresholdOverAllFrames[:,0]==xIdxValue)&(averagedThresholdOverAllFrames[:,1]==yIdxValue))

        if(len(indexForThresholdArray[0])>0):
            zThreshold_apibaso =  averagedThresholdOverAllFrames[indexForThresholdArray][0][-1]
            zThreshold_api = zThreshold_apibaso-interSpaceMargins[1]
            zThreshold_baso = zThreshold_apibaso+interSpaceMargins[0]
            if (np.isnan(zThreshold_apibaso)):
                zThreshold_apibaso = 0

            if(m_firstZ < zThreshold_api):
                condition = 0
                apiFirstXYZ.append([m_firstX,m_firstY,m_firstZ])
                apiLifetimes.append(tracklength)
                api_mAmplitude.append(m_intensity)
                api_sAmplitude.append(s_intensity)
            else:
                if(m_firstZ > zThreshold_baso):
                    condition = 1
                    basoFirstXYZ.append([m_firstX,m_firstY,m_firstZ])
                    basoLifetimes.append(tracklength)
                    baso_mAmplitude.append(m_intensity)
                    baso_sAmplitude.append(s_intensity)
                else:
                    condition=2
                    interFirstXYZ.append([m_firstX,m_firstY,m_firstZ])
                    interLifetimes.append(tracklength)
                    inter_mAmplitude.append(m_intensity)
                    inter_sAmplitude.append(s_intensity)




            for i in range(0,len(lifetimeCohorts)):
                lifetimeLength = lifetimeCohorts[i][1]-lifetimeCohorts[i][0]
                #if(maxIdx >=maxIndexSlaveMustBeLargerThan):
                if(maxIdx >=SlaveMaxAfterPercentCohortLength*lifetimeLength):

                    if((tracklength >lifetimeCohorts[i][0]) & (tracklength <=lifetimeCohorts[i][1])):
                        if(condition==0):
                            trackIdsAssignedToCohorts_api[i] = np.append(trackIdsAssignedToCohorts_api[i],trackId)
                        if(condition==1):
                            trackIdsAssignedToCohorts_baso[i] = np.append(trackIdsAssignedToCohorts_baso[i],trackId)
                        if(condition==2):
                            trackIdsAssignedToCohorts_inter[i] = np.append(trackIdsAssignedToCohorts_inter[i],trackId)

        else:
            #print(averagedThresholdOverAllFrames)
            print(indexForThresholdArray)
            print(m_firstX)
            print(m_firstY)
            print(m_firstZ)
            print(xIdxValue)
            print(yIdxValue)
            print('what?')
    trackIdsAssignedToCohorts_api = np.array(trackIdsAssignedToCohorts_api)
    trackIdsAssignedToCohorts_baso = np.array(trackIdsAssignedToCohorts_baso)
    trackIdsAssignedToCohorts_inter = np.array(trackIdsAssignedToCohorts_inter)
    # depending on organoid orientation, it might be necessary to flip the sign
    # the output order is always:
    # apical, lateral, basolateral
    if(flipApiBaso):
        return([[trackIdsAssignedToCohorts_api,trackIdsAssignedToCohorts_baso,trackIdsAssignedToCohorts_inter],
                [basoFirstXYZ,interFirstXYZ,apiFirstXYZ],
                [basoLifetimes,interLifetimes,apiLifetimes],
                [baso_mAmplitude,inter_mAmplitude,api_mAmplitude],
                [baso_sAmplitude,inter_sAmplitude,api_sAmplitude]]
                )
    else:
        return([[trackIdsAssignedToCohorts_api,trackIdsAssignedToCohorts_baso,trackIdsAssignedToCohorts_inter],
                [apiFirstXYZ,interFirstXYZ,basoFirstXYZ],
                [apiLifetimes,interLifetimes,basoLifetimes],
                [api_mAmplitude,inter_mAmplitude,baso_mAmplitude],
                [api_sAmplitude,inter_sAmplitude,baso_sAmplitude]]
                )





def createBufferForLifetimeCohort(data,listOfTrackIdsAssignedToCohort,    m_backgroundIntensity , s_backgroundIntensity):


    trackIdArray = listOfTrackIdsAssignedToCohort

    m_buffer = []
    s_buffer = []

    bufferSize = 200
    bufferZero = 100


    m_buffer = np.full(( len(trackIdArray),bufferSize), m_backgroundIntensity,dtype=float)
    s_buffer = np.full(( len(trackIdArray),bufferSize), s_backgroundIntensity,dtype=float)


    #for i in range(0,bufferSize):
    #    m_buffer.append([])
    #    s_buffer.append([])

    counter = 0

    for trackId in trackIdArray:
        track = data[data['trackId'] == trackId]
        tracklength = track['tracklength'].values[0]
        m_intensity = track['m_A'].values.astype(float)
        s_intensity = track['s_A'].values.astype(float)
        maxIdx = np.argmax(s_intensity)


        for i in range(0,len(track)):
            if(not np.isnan(m_intensity[i])):
                m_buffer[counter][bufferZero-maxIdx+i]=(m_intensity[i])
            if(not np.isnan(s_intensity[i])):
                s_buffer[counter][bufferZero-maxIdx+i]=(s_intensity[i])


        counter = counter+1;


    return (m_buffer,s_buffer)






def createBufferForLifetimeCohort_normalized(data,listOfTrackIdsAssignedToCohort,    backgroundIntensity ):


    trackIdArray = listOfTrackIdsAssignedToCohort

    m_buffer = []
    s_buffer = []

    bufferSize = 200
    bufferZero = 100


    m_buffer = np.full(( len(trackIdArray),bufferSize), backgroundIntensity,dtype=float)
    s_buffer = np.full(( len(trackIdArray),bufferSize), backgroundIntensity,dtype=float)


    #for i in range(0,bufferSize):
    #    m_buffer.append([])
    #    s_buffer.append([])

    counter = 0

    for trackId in trackIdArray:
        track = data[data['trackId'] == trackId]
        tracklength = track['tracklength'].values[0]
        m_intensity = track['m_A'].values.astype(float)
        s_intensity = track['s_A'].values.astype(float)
        maxIdx = np.argmax(s_intensity)
        m_maxIntensity = np.nanmax(m_intensity)
        s_maxIntensity = np.nanmax(s_intensity)


        for i in range(0,len(track)):
            if(not np.isnan(m_intensity[i])):
                m_buffer[counter][bufferZero-maxIdx+i]=(m_intensity[i])/m_maxIntensity
            if(not np.isnan(s_intensity[i])):
                valueToPut = (s_intensity[i])/s_maxIntensity
                #print(valueToPut)
                s_buffer[counter][bufferZero-maxIdx+i]=(s_intensity[i])/s_maxIntensity
                #print(s_buffer[counter])

        counter = counter+1;


    return (m_buffer,s_buffer)




def createBufferForDistances(data,listOfTrackIdsAssignedToCohort,backgroundIntensity=0,bufferSize = 200, bufferZero = 100):


    trackIdArray = listOfTrackIdsAssignedToCohort

    m_buffer = []
    s_buffer = []



    m_buffer = np.full(( len(trackIdArray),bufferSize), backgroundIntensity)
    s_buffer = np.full(( len(trackIdArray),bufferSize), backgroundIntensity)


    #for i in range(0,bufferSize):
    #    m_buffer.append([])
    #    s_buffer.append([])

    counter = 0

    for trackId in trackIdArray:
        track = data[data['trackId'] == trackId]
        tracklength = track['tracklength'].values[0]
        m_intensity = track['m_A'].values.astype(float)
        s_intensity = track['s_A'].values.astype(float)

        m_x = track['m_x'].values.astype(float)
        m_y = track['m_y'].values.astype(float)
        m_z = track['m_z'].values.astype(float)
        m_distances = []
        for i in range(1,len(track)):
            v1 = np.array([m_x[i-1],m_y[i-1],m_z[i-1]])
            v2 = np.array([m_x[i],m_y[i],m_z[i]])
            dist = np.linalg.norm(v2-v1)
#            m_distances.append(dist)
#            dist = m_z[i-1]-m_z[i]
        m_distances = np.array(m_distances)

        m_distancesToStart = []
        for i in range(0,len(track)):
            v1 = np.array([m_x[0],m_y[0],m_z[0]])
            v2 = np.array([m_x[i],m_y[i],m_z[i]])
            dist = np.linalg.norm(v2-v1)
#            dist = m_z[0]-m_z[i]
#            dist = m_y[0]-m_y[i]
#            print('m')
#            print(dist)
            m_distancesToStart.append(dist)
        m_distancesToStart = np.array(m_distancesToStart)

        s_x = track['s_x'].values.astype(float)
        s_y = track['s_y'].values.astype(float)
        s_z = track['s_z'].values.astype(float)
        s_distances = []
        for i in range(1,len(track)):
            v1 = np.array([s_x[i-1],s_y[i-1],s_z[i-1]])
            v2 = np.array([s_x[i],s_y[i],s_z[i]])
            dist = np.linalg.norm(v2-v1)
#            dist = s_z[i-1]-s_z[i]
            s_distances.append(dist)
        s_distances = np.array(s_distances)

        s_distancesToStart = []
        for i in range(0,len(track)):
            v1 = np.array([s_x[0],s_y[0],s_z[0]])
            v2 = np.array([s_x[i],s_y[i],s_z[i]])
            dist = np.linalg.norm(v2-v1)
#            dist = s_z[0]-s_z[i]
#            dist = s_y[0]-s_y[i]
            s_distancesToStart.append(dist)
#            print('s')
#            print(dist)
        s_distancesToStart = np.array(s_distancesToStart)

        maxIdx = 0#np.argmax(s_intensity)

        #plt.plot(s_distances)
        plt.show()
        for i in range(0,len(m_distances)):
            if(not np.isnan(m_intensity[i])):
                m_buffer[counter][bufferZero-maxIdx+i]=(m_distances[i])
        for i in range(0,len(s_distances)):
            if(not np.isnan(s_intensity[i])):
                s_buffer[counter][bufferZero-maxIdx+i]=(s_distances[i])


        counter = counter+1;


    return (m_buffer,s_buffer)





#-----

def plotLifetimeCohorts(cohortBuffers,backgroundIntensity, framerate_msec, lengthTreshold = 1, bufferSize = 200, bufferZero = 100):

    plt.figure(dpi=300)

    #m_colors = ['magenta','red','crimson']
    #s_colors = ['mediumspringgreen','lawngreen','lime']
    m_colors = ['magenta','magenta','magenta','magenta','red','blue']
    s_colors = ['lime','lime','lime','lime','green','cyan']
    #timeShift = [0,40,95] this shift shifts everything to t=-40



    cltrPeakPerCohort = []
    dnm2PeakPerCohort = []
    cltrPeakPerCohort_std = []
    dnm2PeakPerCohort_std = []

    timeShift = np.array([0,30,70,120,160,200]) +30
    alph = 0.05 #plot line transparency
    liwi = 3 #plot line width




    cohortIdx = 5
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):

        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)


        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )


    #--------

    cohortIdx = 4
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):
        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)


        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )

    #-------

    cohortIdx = 3
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):
        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)

        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )

    #--------

    cohortIdx = 2
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):
        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)


        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )

    #------

    cohortIdx = 1
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):
        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)


        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )

    #------

    cohortIdx = 0
    m_buffer,s_buffer = cohortBuffers[cohortIdx]
    print(cohortIdx,len(m_buffer))
    if(len(m_buffer)>lengthTreshold):
        m_buffer_average = np.nanmean(m_buffer,axis=0)-backgroundIntensity
        s_buffer_average = np.nanmean(s_buffer,axis=0)-backgroundIntensity
        m_buffer_std = np.nanstd(m_buffer,axis=0)
        s_buffer_std = np.nanstd(s_buffer,axis=0)
        time = framerate_msec/1000*(np.array(range(0,bufferSize))-bufferZero)+timeShift[cohortIdx]

        plt.plot(time,m_buffer_average,c=m_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,m_buffer_average-m_buffer_std,m_buffer_average+m_buffer_std,facecolor=m_colors[cohortIdx],alpha=alph)

        plt.plot(time,s_buffer_average,c=s_colors[cohortIdx],lw=liwi)
        plt.fill_between(time,s_buffer_average-s_buffer_std,s_buffer_average+s_buffer_std,facecolor=s_colors[cohortIdx],alpha=alph)

        cltrPeakPerCohort.append(np.max(m_buffer_average))
        dnm2PeakPerCohort.append(np.max(s_buffer_average))
        cltrPeakPerCohort_std.append( m_buffer_std[np.argmax(m_buffer_average)] )
        dnm2PeakPerCohort_std.append( s_buffer_std[np.argmax(s_buffer_average)] )

    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.xlim(-20,200)
    plt.ylim(-7000,45000)
    plt.xlabel('time[s]')
    plt.ylabel('fluorescence intensity [AU]')


    print("cltrPeakPerCohort, avg, std")
    print(cltrPeakPerCohort)
    cltrPeakPerCohort = cltrPeakPerCohort[::-1]
    cltrPeakPerCohort_std = cltrPeakPerCohort_std[::-1]
    print(cltrPeakPerCohort)
    print(cltrPeakPerCohort_std)
    print()
    print(np.diff(cltrPeakPerCohort))
    print(np.diff(cltrPeakPerCohort)/cltrPeakPerCohort[0])
    avg = np.average(np.diff(cltrPeakPerCohort)/cltrPeakPerCohort[0])
    std = np.std(np.diff(cltrPeakPerCohort)/cltrPeakPerCohort[0])
    print("intensity increase = {}+-{}".format(np.round(avg,decimals=2),np.round(std,decimals=2)))
    print()
    print("dnm2PeakPerCohort, avg, std")
    dnm2PeakPerCohort = dnm2PeakPerCohort[::-1]
    dnm2PeakPerCohort_std = dnm2PeakPerCohort_std[::-1]
    print(dnm2PeakPerCohort)
    print(dnm2PeakPerCohort_std)
    print()
    print(np.diff(dnm2PeakPerCohort))
    print(np.diff(dnm2PeakPerCohort)/dnm2PeakPerCohort[0])
    avg = np.average(np.diff(dnm2PeakPerCohort)/dnm2PeakPerCohort[0])
    std = np.std(np.diff(dnm2PeakPerCohort)/dnm2PeakPerCohort[0])
    print("intensity increase = {}+-{}".format(np.round(avg,decimals=2),np.round(std,decimals=2)))
