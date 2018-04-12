% by Joh Schöneberg 2018

%%%%
% This file runs the full analysis pipeline
%
% Input parameters for the pipeline are found in _inputParameters.csv
%
%

% this adds the folder and its subfolders to the matlab search path
addpath(genpath('./tools'))
addpath(genpath('./dependencies'))

I_onlyDetection_framebyframe_nonParallel()
II_stitchMatlabFramesTogether()
III_onlyTracking()
III_tracksRaw2csv()
IV_onlyTrackingProcessing()
IV_tracksProcessed2csv()