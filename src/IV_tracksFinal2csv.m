% by Joh Schöneberg, 2017/2018

%function tracksFinal2csv()

    inputParametersMap = readParam();
    resultsPath = inputParametersMap('resultsFolder')
    trackingFilename = inputParametersMap('trackingFilename')
    trackingCsvFilename = inputParametersMap('trackingCsvFilename')
    
    dfile = [resultsPath trackingFilename];
    if exist(dfile, 'file')==2
        trackedFeatures = load(dfile);
    else
        fprintf(['tracksFinal2csv: no tracking output file found.\n']);
        return;
    end

    
    %----
    % write csv file
    %----
    
    % write a CSV file
    csvPath = [resultsPath trackingCsvFilename];
    fid= fopen(csvPath,'w');
    fprintf(fid,'trackId,tracklength,frameId,particleId,x,y,z,A,noIdea1,noIdea2,noIdea3,noIdea4\n');
    for i = 1:length(trackedFeatures.tracksFinal)
        
        tracksFeatIndxCG_tmp = trackedFeatures.tracksFinal(i).tracksFeatIndxCG;
        [ntrackCandidatesInThisTrack, nParticlesInThisTrack] = size(tracksFeatIndxCG_tmp);
        tracksCoordAmpCG_tmp = trackedFeatures.tracksFinal(i).tracksCoordAmpCG;
        seqOfEvents_tmp = trackedFeatures.tracksFinal(i).seqOfEvents;
        
        % the track candidates are:
        % sometimes u-track detects a likely other particle in the same
        % frame that could participate in the same track
        % 
        for k = 1:ntrackCandidatesInThisTrack
            for j = 1:nParticlesInThisTrack
                % the tracksCoordAmpCG data structure always stores 8 elements
                % per particle

                x = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],1,j));
                y = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],2,j));
                z = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],3,j));
                A = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],4,j));
                noIdea1 = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],5,j));
                noIdea2 = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],6,j));
                noIdea3 = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],7,j));
                noIdea4 = tracksCoordAmpCG_tmp(k,sub2ind([8,nParticlesInThisTrack],8,j));

                fprintf(fid,'%i, %i, %i, %i, %d, %d, %d, %d, %d, %d, %d, %d \n',...
                               i,nParticlesInThisTrack, j, tracksFeatIndxCG_tmp(j),...
                               x,y,z,A,noIdea1,noIdea2,noIdea3,noIdea4);

            end
        end
        
    %    [xx,yy,zz] = ind2sub(size(mask),find(mask == 1));
        
        
    end
    %fclose(fid);
    
    
    
        
        
        
    %end

    
    

%end