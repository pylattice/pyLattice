% reverse engineered version of estGaussian3D.m
% the estGaussian3D does not come with the llsm-tools box
% I used the code from pointSourceDetection3D.m and coaxed in returning the
% required output
% Joh Schoeneberg 2018

function [A_est, c_est] = estGaussianAmplitude3D(vol, sigma)

% Parse inputs
ip = inputParser;
ip.CaseSensitive = false;
ip.KeepUnmatched = true;
ip.addRequired('vol', @isnumeric);
ip.addRequired('sigma', @isnumeric);
ip.addParamValue('Mode', 'xyzAc', @ischar);
ip.addParamValue('Alpha', 0.05, @isscalar);
ip.addParamValue('Mask', [], @(x) isnumeric(x) || islogical(x));
ip.addParamValue('FitMixtures', false, @islogical);
ip.addParamValue('MaxMixtures', 5, @(x) numel(x)==1 && x>0 && round(x)==x);
ip.addParamValue('RemoveRedundant', true, @islogical);
ip.addParamValue('RedundancyRadius', 0.25, @isscalar);
ip.addParamValue('RefineMaskLoG', false, @islogical);
ip.addParamValue('RefineMaskValid', false, @islogical);
ip.addParamValue('ConfRadius', []); % Default: 2*sigma, see fitGaussians3D.
ip.addParamValue('WindowSize', []); % Default: 2*sigma, see fitGaussians3D.


if ~isa(vol, 'double')
    vol = double(vol);
end

if numel(sigma)==1
    sigma = [sigma sigma];
end

%ws = ip.Results.WindowSize;
ws = [];
if isempty(ws)
    ws = ceil(2*sigma);
elseif numel(ws)==1
    ws = [ws ws];
end

%-------------------------------------------------------------------------------------------
% Convolutions
%-------------------------------------------------------------------------------------------
% right-hand side of symmetric kernels
gx = exp(-(0:ws(1)).^2/(2*sigma(1)^2));
gz = exp(-(0:ws(2)).^2/(2*sigma(2)^2));
fg = conv3fast(vol, gx, gx, gz);
fu =  conv3fast(vol,    ones(1,ws(1)+1), ones(1,ws(1)+1), ones(1,ws(2)+1));
fu2 = conv3fast(vol.^2, ones(1,ws(1)+1), ones(1,ws(1)+1), ones(1,ws(2)+1));

% Laplacian of Gaussian-filtered input
gx2 = (0:ws(1)).^2 .*gx;
gz2 = (0:ws(2)).^2 .*gz;
fgx2 = conv3fast(vol, gx2, gx, gz);
fgy2 = conv3fast(vol, gx, gx2, gz);
fgz2 = conv3fast(vol, gx, gx, gz2);
imgLoG = (2/sigma(1)^2+1/sigma(2)^2)*fg - ((fgx2+fgy2)/sigma(1)^4 + fgz2/sigma(2)^4);
clear fgx2 fgy2 fgz2;

% Gaussian kernel (spatial)
[x,y,z] = meshgrid(-ws(1):ws(1),-ws(1):ws(1),-ws(2):ws(2));
g = exp(-(x.^2+y.^2)/(2*sigma(1)^2)) .* exp(-z.^2/(2*sigma(2)^2));
n = numel(g);
gsum = sum(g(:));
g2sum = sum(g(:).^2);

% solution to linear system
A_est = (fg - gsum*fu/n) / (g2sum - gsum^2/n);
c_est = (fu - A_est*gsum)/n;

end