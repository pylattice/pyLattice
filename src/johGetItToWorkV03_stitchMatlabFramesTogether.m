% after having to do all the frame analysis one by one 
% (the parfor eats too much memory since matlab is too badly written),
% this script now stitches all the individual frames back together


resultsPath = '/Users/johannesschoeneberg/Desktop/PostDoc/drubin_lab/lattice_organoids/matlab_lsm_tools_aguet/';
movieLength = 10;

frameInfo(1:movieLength) = struct('x', [], 'y', [], 'z', [], 'A', [], 's', [], 'c', [],...
        'x_pstd', [], 'y_pstd', [], 'z_pstd', [], 'A_pstd', [], 'c_pstd', [],...
        'x_init', [], 'y_init', [], 'z_init', [],...
        'sigma_r', [], 'SE_sigma_r', [], 'RSS', [], 'pval_Ar', [], 'hval_Ar', [],  'hval_AD', [], 'isPSF', [],...
        'xCoord', [], 'yCoord', [], 'zCoord', [], 'amp', [], 'dRange', []);

for k = 1:movieLength


    filepath = sprintf('%s/Detection3D_%04i.mat',resultsPath,k)
    if exist(filepath, 'file')==2
        frameInfoSlice = load(filepath);
    else
        %fprintf(['runTracking: no detection data found for ' getShortPath(data) '\n']);
        fprintf('stitchTogether: no slice found for %s\n',filepath);
        return;
    end

    frameInfo(k)=frameInfoSlice.frameInfo;
    

end

save(sprintf('%s/Detection3D.mat',resultsPath),'frameInfo');