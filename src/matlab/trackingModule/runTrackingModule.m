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
%paramFilePath = [pwd '/' '/../../../input/big_data_cutoff7000_bleachCorrected/_inputParameters.csv']
%paramFilePath = [pwd '/' '/../../../input/big_data_DMSO_cutoff7000_bleachCorrected/_inputParameters.csv']
%paramFilePath = [pwd '/' '/../../../input/big_data_JASP_cutoff7000_bleachCorrected/_inputParameters.csv']
paramFilePath = [pwd '/' '/../../../input/big_data_LY_cutoff7000_bleachCorrected/_inputParameters.csv']

I_onlyDetection_framebyframe_nonParallel(paramFilePath)
II_stitchMatlabFramesTogether(paramFilePath)
III_onlyTracking(paramFilePath)
III_tracksRaw2csv(paramFilePath)
IV_onlyTrackingProcessing(paramFilePath)
IV_tracksProcessed2csv(paramFilePath) 