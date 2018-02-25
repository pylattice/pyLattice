


function tracking()

inputParametersMap = readParam();

resultsPath = inputParametersMap('resultsFolder')
detectionFilename = inputParametersMap('detectionFilename')
trackingFilename = inputParametersMap('trackingFilename')





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
saveResults.filename  = trackingFilename

trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
    settings.kalmanFunctions, 3, saveResults);


%trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
%    settings.kalmanFunctions, 3);

% i think aguet used an old utrack that took a different data structure
% so i leave the save out for a moment
%    settings.kalmanFunctions, 3, 'saveResults', 1);

end