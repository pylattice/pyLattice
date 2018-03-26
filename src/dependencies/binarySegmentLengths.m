%[lengths, value] = binarySegmentLengths(signal) returns the lengths of the successive sequences of 0s and 1s in a binary signal
% Example: for the signal [0 1 1 0 0 0 1], lengths = [1 2 3 1], value = [0 1 0 1]

% Francois Aguet, 08/08/2012

function [lengths, value] = binarySegmentLengths(signal)

d = diff(signal);

changeIdx = find([0 d]~=0);

lengths = diff([1 changeIdx numel(signal)+1]);
value = signal([1 changeIdx]);