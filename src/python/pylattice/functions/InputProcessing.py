# by Joh Schoeneberg 2018
# All rights reserved

from os import listdir
from os.path import isfile, join
import fnmatch
import numpy as np


def getInputParameter(inputParametersPandas,key):
    """
    Parameters:
    -----------
    inputParametersPandas : pandas.df
        pandas dataframe with two columns
    key : string
        key string.
    Returns:
    -----------
    string
        the respective parameter value in the df
    """
    #this locates the row, gets the result out of its array form and strips whitespaces away
    return (((inputParametersPandas.loc[inputParametersPandas['key'] == key]).values)[0,1]).strip()




def getFilenamesOfInputTiffFiles(inputDataFolder,uniqueFilenameString):
    """
    Parameters:
    -----------
    inputDataFolder : string
        path string e.g. /something/somewhere/
    uniqueFilenameString : string
        string that occurs only in the files you want to select, e.g. '_488nm_'
    Returns:
    -----------
    array(string)
        array of filennames that match the given parameters
    """

    folder = inputDataFolder
    print('--- folder searched in: '+folder)

    filesOfInterest = []
    for file in listdir(inputDataFolder):
        if isfile(join(inputDataFolder, file)) and fnmatch.fnmatch(file, '*'+uniqueFilenameString+'*.tif'):
            filesOfInterest.append(file)
    filesOfInterest=np.sort(filesOfInterest)



    print('--- example of files found: '+filesOfInterest[0])
    print('--- number of files found: '+str(len(filesOfInterest)))

    return(filesOfInterest)
