# by Joh Schoeneberg 2018
# All rights reserved

import pandas as pd

#http://www.cgl.ucsf.edu/pipermail/chimera-users/2010-November/005715.html
def pandasData2bildFile(data,filename='puncta.bild'):
    file = open(filename,'w')
    radius = 1
    #.transparency value
    file.write(".transparency 0.5\n")
    file.write(".color red\n")
    file.write(".dot 0 0 0\n")
    #Set the transparency of subsequently defined items. The value can range from 0.0 (not transparent) to 1.0 (completely transparent).
    for i in range(0,len(data)):
        dataLine = data.iloc[i].values
        line = ".sphere "+str(dataLine[0])+" "+str(dataLine[1])+" "+str(dataLine[2])+" "+str(radius)+"\n"
        file.write(line)
    file.close()
