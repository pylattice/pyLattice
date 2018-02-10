


function tracking()

detectionFilename = 'Detection3D.mat'
    resultsPath = '/Users/johannesschoeneberg/Desktop/PostDoc/drubin_lab/lattice_organoids/matlab_lsm_tools_aguet/'



%onlyBrightOnes = 0*mask
%test = 'helloWorld2'
%-------------------------------------------------------------------------------
% 4) Tracking
%-------------------------------------------------------------------------------

dfile = [resultsPath detectionFilename];
if exist(dfile, 'file')==2
    dfile = load(dfile);
    movieInfo = dfile.frameInfo;
else
    %fprintf(['runTracking: no detection data found for ' getShortPath(data) '\n']);
    fprintf(['runTracking: no detection data found for SOMETHING\n']);
    return;
end

settings = loadTrackSettingsJoh('Radius', [3 6], 'MaxGapLength', 2);
saveResults.dir  = resultsPath
saveResults.filename  = 'trackedFeatures.mat'

trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
    settings.kalmanFunctions, 3, saveResults);


%trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
%    settings.kalmanFunctions, 3);

% i think aguet used an old utrack that took a different data structure
% so i leave the save out for a moment
%    settings.kalmanFunctions, 3, 'saveResults', 1);

end