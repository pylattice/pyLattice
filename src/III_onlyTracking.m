


function III_onlyTracking()
disp('--------------------------------------------------------------')
disp('III_onlyTracking(): start...')

inputParametersMap = readParam();

resultsPath = inputParametersMap('outputDataFolder');
detectionFilename = inputParametersMap('detectionFilename');
trackingFilename = inputParametersMap('trackingFilename');





%onlyBrightOnes = 0*mask
%test = 'helloWorld2'
%-------------------------------------------------------------------------------
% 4) Tracking
%-------------------------------------------------------------------------------

dfile = [resultsPath '/' detectionFilename];
if exist(dfile, 'file')==2
    dfile = load(dfile);
    movieInfo = dfile.frameInfo;
else
    %fprintf(['runTracking: no detection data found for ' getShortPath(data) '\n']);
    fprintf(['runTracking: no detection data found for ' dfile '\n']);
    return;
end

%settings = loadTrackSettingsJoh('Radius', [3 6], 'MaxGapLength', 2);
settings = loadTrackSettingsAguet('Radius', [3 6], 'MaxGapLength', 2);
%settings = loadTrackSettingsJohUTrack('Radius', [3 6], 'MaxGapLength', 2);
%settings = loadTrackSettingsJohMergeAguetAndUTrack('Radius', [3 6]);


saveResults.dir  = resultsPath;
saveResults.filename  = trackingFilename;

trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
    settings.kalmanFunctions, 3, saveResults);


%trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
%    settings.kalmanFunctions, 3);

% joh: i think aguet used an old utrack that took a different data structure
% so i leave the save out for a moment
%    settings.kalmanFunctions, 3, 'saveResults', 1);
disp([resultsPath '/' trackingFilename]);
disp('III_onlyTracking(): done.')

end