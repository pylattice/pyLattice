
%function parsave(fname, x)
%    save(fname, 'x')
%end

%tic

function I_onlyDetection_framebyframe_nonParallel()
disp('--------------------------------------------------------------')
disp('I_onlyDetection_framebyframe_nonParallel(): Start detection...')

inputParametersMap = readParam();

filenames = getAllFiles(inputParametersMap('inputDataFolder'));
movieLength = str2num(inputParametersMap('movieLength'));
allowedMaxNumDetectionsPerFrame = str2num(inputParametersMap('allowedMaxNumDetectionsPerFrame'));

tifFilenames = contains(filenames,".tif");
%remove all filenames that do not contain .tif
filenames = filenames(tifFilenames);

uniqueFilenameString = inputParametersMap('ch1_uniqueFilenameString');
wantedFilenames = contains(filenames,uniqueFilenameString);
filenames = sort(filenames(wantedFilenames));

%filenames = {'DUP_S3P6-1-560-frame0.tif', ...
%            'DUP_S3P6-1-560-frame1.tif', ...
%            'DUP_S3P6-1-560-frame2.tif',...
%            'DUP_S3P6-1-560-frame3.tif', ...
%            'DUP_S3P6-1-560-frame4.tif', ...
%            'DUP_S3P6-1-560-frame5.tif',...
%            'DUP_S3P6-1-560-frame6.tif', ...
%            'DUP_S3P6-1-560-frame7.tif', ...
%            'DUP_S3P6-1-560-frame8.tif',...
%            'DUP_S3P6-1-560-frame9.tif'}
        
        
        



if movieLength == 0
    movieLength = length(filenames);
end

fmt = ['%.' num2str(ceil(log10(movieLength+1))) 'd'];

% this script is taken from runDetection3D.m and modified



%-------------------------------------------------------------------------------
    % 3) Detection
    %-------------------------------------------------------------------------------
    %ip.addParamValue('FileName', 'Detection3D.mat');

%-------

% double fields, multi-channel
dfields = {'x', 'y', 'z', 'A', 'c', 'x_pstd', 'y_pstd', 'z_pstd', 'A_pstd', 'c_pstd', 'sigma_r', 'SE_sigma_r', 'RSS', 'pval_Ar'};
% logical fields, multi-channel
lfields = {'hval_Ar', 'hval_AD', 'isPSF'};
% slave channel fields
sfields = [dfields {'hval_Ar', 'hval_AD'}]; % 'isPSF' is added later

rmfields = [dfields lfields {'x_init', 'y_init', 'z_init', 'mask_Ar'}];


       
    %detectionFilename = 'Detection3D.mat'
    resultsPath = inputParametersMap('outputDataFolder');
    
    sigma = str2num(inputParametersMap('sigma_detectionLoG'));

    
    mCh = 1; %master channel ID 
    nCh = 1; %number of channels
    %k = 1 %this is a remnant of the loop over a number of frames in the script

%-------

%parfor k = 1:movieLength
for k = 1:movieLength
    
     %this is the output accumulator
    
    frameInfo = struct('x', [], 'y', [], 'z', [], 'A', [], 's', [], 'c', [],...
    'x_pstd', [], 'y_pstd', [], 'z_pstd', [], 'A_pstd', [], 'c_pstd', [],...
    'x_init', [], 'y_init', [], 'z_init', [],...
    'sigma_r', [], 'SE_sigma_r', [], 'RSS', [], 'pval_Ar', [], 'hval_Ar', [],  'hval_AD', [], 'isPSF', [],...
    'xCoord', [], 'yCoord', [], 'zCoord', [], 'amp', [], 'dRange', []);
    


    % big test data set, 350mb, 5min processing time
    %path = '/Users/johannesschoeneberg/Desktop/PostDoc/drubin_lab/daphne_lattice_organoids/data_/2016_04_25Daphne/Sample3_CD_10ulMG/Position5_Basal_apical_ObjScan/matlab_decon/S3P5_488_150mw_560_300mw_Objdz150nm_ch1_CAM1_stack0000_560nm_0000000msec_0090116101msecAbs_000x_000y_003z_0000t_decon.tif'
    path = char(filenames(k));
    disp(path)

    % small test data set, 10mb, 10s processing time
    %path = '/Users/johannesschoeneberg/Desktop/PostDoc/drubin_lab/daphne_lattice_organoids/matlab_lsm_tools_aguet/DUP_S3P6-1-RFP-frame1_better_signal.tif'
    %frame = double(readtiff(data.framePathsDS{mCh}{k})); %#ok<PFBNS>
    frame = double(readtiff(path)); %#ok<PFBNS>
    frame(frame==0) = NaN; % to avoid border effects

        [ny,nx,nz] = size(frame);

    %[pstruct, mask] = pointSourceDetection3D(frame, sigma(mCh,:), 'Alpha', opts.Alpha,...
    %        'Mask', opts.CellMask, 'RemoveRedundant', opts.RemoveRedundant,...
    %        'RefineMaskLoG', false, 'WindowSize', opts.WindowSize); %#ok<PFBNS>

    % Alpha:
        [pstruct, mask] = pointSourceDetection3D(frame, sigma,'RefineMaskLoG', false );


    %test = 'helloWorld'
    %[xx,yy,zz] = ind2sub(size(mask),find(mask == 1));
    %scatter3(xx,yy,zz,0.3)
    %%%maskPath = '/Users/johannesschoeneberg/Desktop/PostDoc/drubin_lab/daphne_lattice_organoids/matlab_lsm_tools_aguet/DUP_S3P6-1-RFP-frame1_better_signal__mask.tif'
    %%%writetiff(uint8(255*mask), maskPath);

    %-------------------------------------------------------------------------------
    % joh: filter out the low amplitude pucta
    % this removes the data density to a manageable level.
    % remove all the bad ones for every field in the pstruct
    % names = fieldnames(pstruct)
    sortedAmplitudes = sort(pstruct.A);
    if length(sortedAmplitudes) > allowedMaxNumDetectionsPerFrame
        amplitudeCutoff = sortedAmplitudes(end-allowedMaxNumDetectionsPerFrame)
        idx = find(pstruct.A >amplitudeCutoff);
    else
        idx = find(pstruct.A >0);
    end
    amplitudeCutoff = 5000;
    idx = find(pstruct.A >amplitudeCutoff);
    pstruct.x             = pstruct.x(idx);
    pstruct.y             = pstruct.y(idx);
    pstruct.z             = pstruct.z(idx);
    pstruct.A             = pstruct.A(idx);
    pstruct.c             = pstruct.c(idx);
    pstruct.x_pstd        = pstruct.x_pstd(idx);
    pstruct.y_pstd        = pstruct.y_pstd(idx);
    pstruct.z_pstd        = pstruct.z_pstd(idx);
    pstruct.A_pstd        = pstruct.A_pstd(idx);
    pstruct.c_pstd        = pstruct.c_pstd(idx);
    pstruct.x_init        = pstruct.x_init(idx);
    pstruct.y_init        = pstruct.y_init(idx);
    pstruct.z_init        = pstruct.z_init(idx);
    pstruct.sigma_r       = pstruct.sigma_r(idx);
    pstruct.SE_sigma_r    = pstruct.SE_sigma_r(idx);
    pstruct.RSS           = pstruct.RSS(idx);
    pstruct.pval_Ar       = pstruct.pval_Ar(idx);
    pstruct.hval_Ar       = pstruct.hval_Ar(idx);
    pstruct.hval_AD       = pstruct.hval_AD(idx);
    pstruct.isPSF         = pstruct.isPSF(idx);
    %pstruct.xCoord        = pstruct.xCoord(idx)
    %pstruct.yCoord        = pstruct.yCoord(idx)
    %pstruct.zCoord        = pstruct.zCoord(idx)
    %pstruct.amp           = pstruct.amp(idx)



    %
    %-------------------------------------------------------------------------------


    
    

    
     if ~isempty(pstruct)
         
        
        pstruct.s = sigma;
        pstruct = rmfield(pstruct, 's_pstd');
        
        %curly brackets define an array
        pstruct.dRange{mCh} = [min(frame(:)) max(frame(:))];
        np = numel(pstruct.x);
        
        % expand structure for slave channels
        for f = 1:length(dfields)
            tmp = NaN(nCh, np);
            tmp(mCh,:) = pstruct.(dfields{f});
            pstruct.(dfields{f}) = tmp;
        end
        for f = 1:length(lfields)
            tmp = false(nCh, np);
            tmp(mCh,:) = pstruct.(lfields{f});
            pstruct.(lfields{f}) = tmp;
        end
        
        % retain only mask regions containing localizations
        CC = bwconncomp(mask);
        labels = labelmatrix(CC);
        loclabels = labels(sub2ind([ny nx nz], pstruct.y_init, pstruct.x_init, pstruct.z_init));
        idx = setdiff(1:CC.NumObjects, loclabels);
        CC.PixelIdxList(idx) = [];
        CC.NumObjects = length(CC.PixelIdxList);
        
        % clean mask
        labels = labelmatrix(CC);
        mask = labels~=0;
        
        %disp('<difference>')
        %disp('nCh')
        %disp(nCh)
        %disp('mCh')
        %disp(mCh)
        %disp(setdiff(1:nCh, mCh))
        %disp('</difference>')
        
        % if I have only one channel, this loop is not called
        % the loop takes the master channel detections and then
        % uses their coordinates to read out the slave channel intensities
        % the function estGaussianAmplitude3D is not available to me.
        for ci = setdiff(1:nCh, mCh)
            %frame = double(readtiff(data.framePathsDS{ci}{k}));
            frame = double(readtiff(path)); 
            pstruct.dRange{ci} = [min(frame(:)) max(frame(:))];
            X = [pstruct.x(mCh,:)' pstruct.y(mCh,:)' pstruct.z(mCh,:)'];
            
            %joh: we done have this function. However it is not called as
            %long as we only have one channel and not multiple.
            [A_est, c_est] = estGaussianAmplitude3D(frame, sigma(ci,:));
            % linear index of positions
            linIdx = sub2ind(size(frame), roundConstr(X(:,2),ny), roundConstr(X(:,1),nx), roundConstr(X(:,3),nz));
            pstructSlave = fitGaussians3D(frame, X, A_est(linIdx), sigma(ci,:), c_est(linIdx), 'Ac');
            
            % localize, and compare intensities & (x,y)-coordinates. Use localization result if it yields better contrast
            pstructSlaveLoc = fitGaussians3D(frame, X, pstructSlave.A, sigma(ci,:), pstructSlave.c, 'xyAc');
            idx = sqrt((pstruct.x(mCh,:)-pstructSlaveLoc.x).^2 ...
                + (pstruct.y(mCh,:)-pstructSlaveLoc.y).^2) < 3*sigma(mCh,1) & pstructSlaveLoc.A > pstructSlave.A;
            
            % fill slave channel information
            for f = 1:length(sfields)
                pstruct.(sfields{f})(ci,~idx) = pstructSlave.(sfields{f})(~idx);
                pstruct.(sfields{f})(ci,idx) = pstructSlaveLoc.(sfields{f})(idx);
            end
            
            nanIdx = isnan(pstructSlave.x); % points within slave channel border, remove from detection results
            for f = 1:length(rmfields)
                pstruct.(rmfields{f})(:,nanIdx) = [];
            end
            
            pstruct.isPSF(ci,:) = ~pstruct.hval_AD(ci,:);
        end
        
        % add fields for tracker
        pstruct.xCoord = [pstruct.x(mCh,:)' pstruct.x_pstd(mCh,:)'];
        pstruct.yCoord = [pstruct.y(mCh,:)' pstruct.y_pstd(mCh,:)'];
        pstruct.zCoord = [pstruct.z(mCh,:)' pstruct.z_pstd(mCh,:)'];% * data.zAniso; , joh: dont have the anisotropy yet
        pstruct.amp =    [pstruct.A(mCh,:)' pstruct.A_pstd(mCh,:)'];
        frameInfo = orderfields(pstruct, fieldnames(frameInfo)); %#ok<PFOUS>
        else
        frameInfo.dRange{mCh} = [min(frame(:)) max(frame(:))];
        for ci = setdiff(1:nCh, mCh)
            %frame = double(imread(data.framePathsDS{ci}{k}));
            frame = double(readtiff(path)); 
            frameInfo.dRange{ci} = [min(frame(:)) max(frame(:))];
        end
        frameInfo.s = sigma;
     end
    
%--------------------------------------------------------------------------------
% output
     
    % write mask to a TIFF file
    maskPath = [resultsPath filesep 'dmask_' num2str(k, fmt) '.tif'];
    writetiff(uint8(255*mask), maskPath);


    % write a CSV file
    csvPath = [resultsPath filesep 'puncta_' num2str(k, fmt) '.csv'];
    fid= fopen(csvPath,'w');
    fprintf(fid,'#x[px], y[px], z[px], A\n');
    for i = 1 : length(frameInfo.x)
        fprintf(fid,'%d, %d, %d, %d \n',frameInfo.x(i),frameInfo.y(i),frameInfo.z(i),frameInfo.A(i));
    end
    fclose(fid);
    
    % save cannot be called in a parallel loop
    % (https://www.mathworks.com/matlabcentral/answers/135285-how-do-i-use-save-with-a-parfor-loop-using-parallel-computing-toolbox)
    %save([resultsPath detectionFilename], 'frameInfo');
    save(sprintf('%s/Detection3D_%04i.mat',resultsPath,k),'frameInfo')
    %parsave(sprintf('%s/Detection3D_%04i.mat',resultsPath,k),frameInfo);

end


disp('I_onlyDetection_framebyframe_nonParallel(): done.')

end


%%%%  function tracking()



%onlyBrightOnes = 0*mask
%test = 'helloWorld2'
%-------------------------------------------------------------------------------
% 4) Tracking
%-------------------------------------------------------------------------------

%%%%  dfile = [resultsPath detectionFilename];
%%%%  if exist(dfile, 'file')==2
%%%%      dfile = load(dfile);
%%%%      movieInfo = dfile.frameInfo;
%%%%  else
%%%%      %fprintf(['runTracking: no detection data found for ' getShortPath(data) '\n']);
%%%%      fprintf(['runTracking: no detection data found for SOMETHING\n']);
%%%%      return;
%%%%  end
%%%%  
%%%%  settings = loadTrackSettings('Radius', [3 6], 'MaxGapLength', 2);

%%%%  trackCloseGapsKalmanSparse(movieInfo, settings.costMatrices, settings.gapCloseParam,...
%%%%      settings.kalmanFunctions, 3);
%%%%  % i think aguet used an old utrack that took a different data structure
%%%%  % so i leave the save out for a moment
%%%%  %    settings.kalmanFunctions, 3, 'saveResults', 1);
%%%%  
%%%%  end

%toc