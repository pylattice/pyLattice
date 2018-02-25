function out = readParam()


allParams = readtable('_inputParameters.csv','Delimiter',',','ReadVariableNames',false);
%disp(allParams{1,1})
%disp(allParams{1,2})


inputParameters = containers.Map('KeyType','char','ValueType','char');
for i = 1:size(allParams)
    %disp(allParams{i,1})
    %disp(allParams{i,2})
    inputParameters(char(allParams{i,1}))=char(allParams{i,2});
end



out = inputParameters;
%out = rightRow;




