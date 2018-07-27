% by Joh Schöneberg 2018

%%%%
% This file runs the 3D tracking module
%
% Input parameters for the pipeline are found in _inputParameters.csv
% Outputs the tracking results as .csv files, ready for further processing
% 

% Input file selection:

% option 1: set the path here
paramFilePath = ''
%paramFilePath = '/Users/johannesschoeneberg/git/JohSchoeneberg/pyLattice/run_test/imaging_data/_inputParameters.csv'

% option 2: use the UI to let the user select a file
if isequal(paramFilePath,'')
    [file,path] = uigetfile('*.csv');
    if isequal(file,0)
        disp('User selected Cancel');
    else
        disp(['User selected ', fullfile(path,file)]);
    end
end

paramFilePath = fullfile(path,file)


% this adds the folder and its subfolders to the matlab search path
addpath(genpath('./tools'))
addpath(genpath('./dependencies'))


% runnint the script

I_onlyDetection_framebyframe_nonParallel(paramFilePath)
II_stitchMatlabFramesTogether(paramFilePath)
III_onlyTracking(paramFilePath)
III_tracksRaw2csv(paramFilePath)
IV_onlyTrackingProcessing(paramFilePath)
IV_tracksProcessed2csv(paramFilePath) 