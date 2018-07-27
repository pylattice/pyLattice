% by Joh Schöneberg 2018

% based on llsmtools by F. Aguet 2014

function I_onlyDetection_framebyframe_nonParallel(parameterFile)
disp('--------------------------------------------------------------')
disp('I_onlyDetection_framebyframe_nonParallel(): Start detection...')

inputParametersMap = readParam(parameterFile);

filenames = getAllFiles(inputParametersMap('inputDataFolder'));
movieLength = str2num(inputParametersMap('movieLength'));
%allowedMaxNumDetectionsPerFrame = str2num(inputParametersMap('allowedMaxNumDetectionsPerFrame'));

tifFilenames = contains(filenames,".tif");
%remove all filenames that do not contain .tif
filenames = filenames(tifFilenames);

master_uniqueFilenameString = inputParametersMap('master_uniqueFilenameString');
master_wantedFilenames = contains(filenames,master_uniqueFilenameString);
master_filenames = sort(filenames(master_wantedFilenames));

slave_uniqueFilenameString = inputParametersMap('slave_uniqueFilenameString');
slave_wantedFilenames = contains(filenames,slave_uniqueFilenameString);
slave_filenames = sort(filenames(slave_wantedFilenames));

detectionAmplitudeCutoff = str2num(inputParametersMap('detectionAmplitudeCutoff'))
       
%disp(['detectionAmplitudeCutoff: ' detectionAmplitudeCutoff])        


if movieLength == 0
    movieLength = length(master_filenames);
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

%rmfields = [dfields lfields {'x_init', 'y_init', 'z_init', 'mask_Ar'}];
% joh: remove mask_Ar, if left in, errors later when this is set to []
rmfields = [dfields lfields {'x_init', 'y_init', 'z_init'}];



    %joh: initialize 2D array of sigmas
    sigma = [str2num(inputParametersMap('master_sigma_detectionLoG')); str2num(inputParametersMap('slave_sigma_detectionLoG'))]
 
    
    mCh = 1; %master channel ID 
    nCh = 2; %number of channels
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
    
    disp("k")
    disp(k)
    disp(master_filenames)

    path = char(master_filenames(k));
    disp(path)
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
    
    %sortedAmplitudes = sort(pstruct.A);
    %if length(sortedAmplitudes) > allowedMaxNumDetectionsPerFrame
    %    amplitudeCutoff = sortedAmplitudes(end-allowedMaxNumDetectionsPerFrame)
    %    idx = find(pstruct.A >amplitudeCutoff);
    %else
    %    idx = find(pstruct.A >0);
    %end
    
    %amplitudeCutoffFirstFrame = 7000;
    %amplitudeCutoffLastFrame = 3500;
    %amplitudeCutoffDeltaPerFrame = (amplitudeCutoffFirstFrame-amplitudeCutoffLastFrame)/movieLength;
    %amplitudeCutoff = amplitudeCutoffFirstFrame-k*amplitudeCutoffDeltaPerFrame;
    
    amplitudeCutoff = detectionAmplitudeCutoff;
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
        
        % joh: if I have only one channel, this loop is not called
        % the loop takes the master channel detections and then
        % uses their coordinates to read out the slave channel intensities
        % the function estGaussianAmplitude3D is not available to me.
        % update: I reverse engineered it. It is working now.
        for ci = setdiff(1:nCh, mCh)
            fprintf('do work on slave channel id: %d ...', ci)
            %frame = double(readtiff(data.framePathsDS{ci}{k}));
            path = char(slave_filenames(k));
            disp(path)
            frame = double(readtiff(path)); 
            pstruct.dRange{ci} = [min(frame(:)) max(frame(:))];
            %Joh: this is a three column table with the x,y,z positions of
            %the master detections
            X = [pstruct.x(mCh,:)' pstruct.y(mCh,:)' pstruct.z(mCh,:)'];
            
            %joh: we done have this function. However it is not called as
            %long as we only have one channel and not multiple.
            [A_est, c_est] = estGaussianAmplitude3D(frame, sigma(ci,:));
            % linear index of positions
            %linIdx = sub2ind(size(frame), roundConstr(X(:,2),ny), roundConstr(X(:,1),nx), roundConstr(X(:,3),nz));
            %pstructSlave = fitGaussians3D(frame, X, A_est(linIdx), sigma(ci,:), c_est(linIdx), 'Ac');
            linIdx = sub2ind(size(frame), roundConstr(X(:,2),nx), roundConstr(X(:,1),ny), roundConstr(X(:,3),nz));
            %frame(linIdx)
%            disp('setae')
%            disp(ci)
%            sigma(ci,:)
            pstructSlave = fitGaussians3D(frame, X, A_est(linIdx),sigma(ci,:), c_est(linIdx), 'Ac');
            
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
        frameInfo = orderfields(pstruct, fieldnames(frameInfo)); 
        else
        frameInfo.dRange{mCh} = [min(frame(:)) max(frame(:))];
        for ci = setdiff(1:nCh, mCh)
            fprintf('2nd: do work on slave channel id: %d ...\n', ci)
            %frame = double(readtiff(data.framePathsDS{ci}{k}));
            path = char(slave_filenames(k));
            disp(path)
            frame = double(readtiff(path)); 
            frameInfo.dRange{ci} = [min(frame(:)) max(frame(:))];
        end
        frameInfo.s = sigma;
     end
    
%--------------------------------------------------------------------------------
% output
           
    %detectionFilename = 'Detection3D.mat'
    resultsPath = inputParametersMap('outputDataFolder');
    master_outputDataFolder = inputParametersMap('master_outputDataFolder');
    if exist([resultsPath filesep master_outputDataFolder filesep], 'file')==0
        mkdir([resultsPath filesep master_outputDataFolder filesep])
    end
        
    slave_outputDataFolder = inputParametersMap('slave_outputDataFolder');
    if exist([resultsPath filesep slave_outputDataFolder filesep], 'file')==0
        mkdir([resultsPath filesep slave_outputDataFolder filesep])
    end
 

     
    % write mask to a TIFF file
    maskPath = [resultsPath filesep master_outputDataFolder filesep 'dmask_' num2str(k, fmt) '.tif'];
    writetiff(uint8(255*mask), maskPath);


    % write a CSV file master
    csvPath = [resultsPath filesep master_outputDataFolder filesep 'puncta_' num2str(k, fmt) '.csv'];
    fid= fopen(csvPath,'w');
    fprintf(fid,'#x[px], y[px], z[px], A\n');
    for i = 1 : length(frameInfo.x)
        fprintf(fid,'%d, %d, %d, %d \n',frameInfo.x(1,i),frameInfo.y(1,i),frameInfo.z(1,i),frameInfo.A(1,i));
    end
    fclose(fid);
    
     % write a CSV file slave
    if(nCh == 2)
        csvPath = [resultsPath filesep slave_outputDataFolder filesep 'puncta_' num2str(k, fmt) '.csv'];
        fprintf('csvPath %s \n',csvPath);
        fid= fopen(csvPath,'w');
        fprintf(fid,'#x[px], y[px], z[px], A\n');
        for i = 1 : length(frameInfo.x)
            fprintf(fid,'%d, %d, %d, %d \n',frameInfo.x(2,i),frameInfo.y(2,i),frameInfo.z(2,i),frameInfo.A(2,i));
        end
        fclose(fid);
    end
        
    
    % save cannot be called in a parallel loop
    % (https://www.mathworks.com/matlabcentral/answers/135285-how-do-i-use-save-with-a-parfor-loop-using-parallel-computing-toolbox)
    %save([resultsPath detectionFilename], 'frameInfo');
    save(sprintf('%s/Detection3D_%04i.mat',resultsPath,k),'frameInfo')
    %parsave(sprintf('%s/Detection3D_%04i.mat',resultsPath,k),frameInfo);

end


disp('I_onlyDetection_framebyframe_nonParallel(): done.')

end


