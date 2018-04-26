% by Joh Schöneberg 2018

function IV_tracksProcessed2csv(parameterFile)
disp('--------------------------------------------------------------')
disp('IV_tracksProcessed2csv(): start...')

    inputParametersMap = readParam(parameterFile);
    resultsPath = inputParametersMap('outputDataFolder');
    trackingFilename = inputParametersMap('trackingFilenameProcessed');
    dfile = [resultsPath filesep trackingFilename];
    if exist(dfile, 'file')==2
        fileContent = load(dfile);
    else
        fprintf(['tracksFinal2csv: no tracking output file found.\n']);
        return;
    end

    tracks = fileContent.tracks;
    
    
    trackingCsvFilename = inputParametersMap('trackingCsvFilenameProcessed');
    
    
    

    %disp('length(tracks)')
    %disp(length(tracks));
    %----
    % write csv file
    %----
    
    % write a CSV file
    csvPath = [resultsPath  filesep trackingCsvFilename];
    disp(csvPath)
    fid= fopen(csvPath,'w');
    fprintf(fid,'trackId,tracklength,time[s],frameId,lifetime,catIdx, m_x,m_y,m_z,m_A,m_c,m_pValue, s_x,s_y,s_z,s_A,s_c,s_pValue\n');
    for i = 1:length(tracks)
        
       track = tracks(i);
       
       
       trackLength = length(track.t);
       
       for j = 1:trackLength
        
                t = track.t(:,j);
                f = track.f(:,j);
                x = track.x(:,j);
                y = track.y(:,j);
                z = track.z(:,j);
                A = track.A(:,j);
                c = track.c(:,j);
                pval_Ar = track.pval_Ar(:,j);
                lifetime_s = track.lifetime_s;
                catIdx = track.catIdx;
                
                fprintf(fid,'%i, %i, %d, %i, %d, %i, %d, %d, %d, %d, %d, %d,  %d, %d, %d, %d, %d, %d\n',...
                           i,  trackLength, t,  f, lifetime_s,catIdx, x(1),  y(1),  z(1),  A(1),  c(1),pval_Ar(1),x(2),  y(2),  z(2),  A(2),  c(2),pval_Ar(2));

            
        end
        
    %    [xx,yy,zz] = ind2sub(size(mask),find(mask == 1));
        
        
    end
    %fclose(fid);
    
    
    
        
disp('IV_tracksProcessed2csv(): done.')        
end

    
    

%end