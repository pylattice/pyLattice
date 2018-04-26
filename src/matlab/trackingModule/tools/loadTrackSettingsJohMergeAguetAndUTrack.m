% This is the loadTrackSettings from Francois Aguet, Nov 2010
% combined with the latest version of u-track:
% 'ScriptTrackGeneral' in 'trackWithGapClosing/Kalman'
% 
% Joh Schoneberg, Dec 2017

function trackSettings = loadTrackSettingsJohUTrack(varargin)

%inputParametersMap = readParam();
%resultsPath = inputParametersMap('outputDataFolder');
%detectionFilename = inputParametersMap('ch1_detectionFilename');
%movieLength = str2num(inputParametersMap('movieLength'));

ip = inputParser;
ip.CaseSensitive = false;
ip.addParamValue('Radius', []);
ip.addParamValue('GapRadius', [5 10]);
ip.addParamValue('LinkRadius', [5 10]);
ip.parse(varargin{:});

gapRadius = ip.Results.GapRadius;
linkRadius = ip.Results.LinkRadius;
if ~isempty(ip.Results.Radius)
    gapRadius = ip.Results.Radius;
    linkRadius = ip.Results.Radius;
end







gapCloseParam.timeWindow = 5;  % maximum allowed time gap (in frames) between a track segment end and a track segment start that allows linking them.
gapCloseParam.mergeSplit = 1;  % 1 if merging and splitting are to be considered, 2 if only merging is to be considered, 3 if only splitting is to be considered, 0 if no merging or splitting are to be considered.
gapCloseParam.minTrackLen = 1; % minimum length of track segments from linking to be used in gap closing.
gapCloseParam.diagnostics = 0; % 1 to plot a histogram of gap lengths in the end; 0 or empty otherwise.


% cost matrix for frame-to-frame linking

%function name
costMatrices(1).funcName = 'costMatRandomDirectedSwitchingMotionLink';

%parameters

parameters.linearMotion = 0; %use linear motion Kalman filter.
parameters.minSearchRadius = linkRadius(1); %minimum allowed search radius. The search radius is calculated on the spot in the code given a feature's motion parameters. If it happens to be smaller than this minimum, it will be increased to the minimum.
parameters.maxSearchRadius = linkRadius(2); %maximum allowed search radius. Again, if a feature's calculated search radius is larger than this maximum, it will be reduced to this maximum.
parameters.brownStdMult = 3; %multiplication factor to calculate search radius from standard deviation.

parameters.useLocalDensity = 1; %1 if you want to expand the search radius of isolated features in the linking (initial tracking) step.
parameters.nnWindow = gapCloseParam.timeWindow; %number of frames before the current one where you want to look to see a feature's nearest neighbor in order to decide how isolated it is (in the initial linking step).
parameters.kalmanInitParam = []; %Kalman filter initialization parameters.
% parameters.kalmanInitParam.searchRadiusFirstIteration = 10; %Kalman filter initialization parameters.
%optional input
parameters.diagnostics = []; %if you want to plot the histogram of linking distances up to certain frames, indicate their numbers; 0 or empty otherwise. Does not work for the first or last frame of a movie.

costMatrices(1).parameters = parameters;
clear parameters

% cost matrix for gap closing

%function name
costMatrices(2).funcName = 'costMatRandomDirectedSwitchingMotionCloseGaps';

%parameters
parameters.linearMotion = 0; %use linear motion Kalman filter.
parameters.minSearchRadius = gapRadius(1); %was 6, minimum allowed search radius.
parameters.maxSearchRadius = gapRadius(2); %was 6, maximum allowed search radius.
parameters.brownStdMult = 3*ones(gapCloseParam.timeWindow,1); %multiplication factor to calculate Brownian search radius from standard deviation.

parameters.brownScaling = [0.5 0.01]; % aguet has [0.5 0.01] here. power for scaling the Brownian search radius with time, before and after timeReachConfB (next parameter).
% parameters.timeReachConfB = 3; %before timeReachConfB, the search radius grows with time with the power in brownScaling(1); after timeReachConfB it grows with the power in brownScaling(2).
parameters.timeReachConfB = gapCloseParam.timeWindow; %before timeReachConfB, the search radius grows with time with the power in brownScaling(1); after timeReachConfB it grows with the power in brownScaling(2).
parameters.ampRatioLimit = [0 Inf]; % auge has [0 Inf] here. for merging and splitting. Minimum and maximum ratios between the intensity of a feature after merging/before splitting and the sum of the intensities of the 2 features that merge/split.
parameters.lenForClassify = 5; %minimum track segment length to classify it as linear or random.

parameters.useLocalDensity = 1; % auget has 1 here. 1 if you want to expand the search radius of isolated features in the gap closing and merging/splitting step.
parameters.nnWindow = gapCloseParam.timeWindow; %number of frames before/after the current one where you want to look for a track's nearest neighbor at its end/start (in the gap closing step).
parameters.linStdMult = 3*ones(gapCloseParam.timeWindow,1); %multiplication factor to calculate linear search radius from standard deviation.
parameters.linScaling = [1 0.01]; %power for scaling the linear search radius with time (similar to brownScaling).
% parameters.timeReachConfL = 4; %similar to timeReachConfB, but for the linear part of the motion.
parameters.timeReachConfL = gapCloseParam.timeWindow; %similar to timeReachConfB, but for the linear part of the motion.
parameters.maxAngleVV = 45; %was here. maximum angle between the directions of motion of two tracks that allows linking them (and thus closing a gap). Think of it as the equivalent of a searchRadius but for angles.

%optional; if not input, 1 will be used (i.e. no penalty)
parameters.gapPenalty = []; %aguet has [] here. penalty for increasing temporary disappearance time (disappearing for n frames gets a penalty of gapPenalty^(n-1)).

%optional; to calculate MS search radius
%if not input, MS search radius will be the same as gap closing search radius
parameters.resLimit = []; %resolution limit, which is generally equal to 3 * point spread function sigma.

%NEW PARAMETER
parameters.gapExcludeMS = 1; %flag to allow gaps to exclude merges and splits

%NEW PARAMETER
parameters.strategyBD = -1; %strategy to calculate birth and death cost

costMatrices(2).parameters = parameters;
clear parameters

% Kalman filter function names

kalmanFunctions.reserveMem  = 'kalmanResMemLM';
kalmanFunctions.initialize  = 'kalmanInitLinearMotion';
kalmanFunctions.calcGain    = 'kalmanGainLinearMotion';
kalmanFunctions.timeReverse = 'kalmanReverseLinearMotion';




trackSettings.costMatrices = costMatrices;
trackSettings.gapCloseParam = gapCloseParam;
trackSettings.kalmanFunctions = kalmanFunctions;