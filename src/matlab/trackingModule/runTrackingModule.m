% by Joh Schöneberg 2018

%%%%
% This file runs the 3D tracking module
%
% Input parameters for the pipeline are found in _inputParameters.csv
% Outputs the tracking results as .csv files, ready for further processing
% 

% this adds the folder and its subfolders to the matlab search path
addpath(genpath('./tools'))
addpath(genpath('./dependencies'))

% location of the input parameter file
paramFilePath = [pwd '/' '/../../input/imaging_data/_inputParameters.csv']

I_onlyDetection_framebyframe_nonParallel(paramFilePath)
II_stitchMatlabFramesTogether(paramFilePath)
III_onlyTracking(paramFilePath)
III_tracksRaw2csv(paramFilePath)
IV_onlyTrackingProcessing(paramFilePath)
IV_tracksProcessed2csv(paramFilePath) 