% by Joh Schöneberg, 2017/2018

function IV_tracksProcessed2csv()
disp('--------------------------------------------------------------')
disp('IV_tracksProcessed2csv(): start...')

    inputParametersMap = readParam();
    resultsPath = inputParametersMap('outputDataFolder');
    trackingFilename = inputParametersMap('ch0_trackingFilenameProcessed');
    trackingCsvFilename = inputParametersMap('ch0_trackingCsvFilenameProcessed');
    
    dfile = [resultsPath '/' trackingFilename];
    
    if exist(dfile, 'file')==2
        fileContent = load(dfile);
    else
        fprintf(['tracksFinal2csv: no tracking output file found.\n']);
        return;
    end

    tracks = fileContent.tracks;
    %disp('length(tracks)')
    %disp(length(tracks));
    %----
    % write csv file
    %----
    
    % write a CSV file
    csvPath = [resultsPath '/' trackingCsvFilename];
    disp(csvPath)
    fid= fopen(csvPath,'w');
    fprintf(fid,'trackId,tracklength,time[s],frameId,x,y,z,A,c,lifetime,catIdx,pValue\n');
    for i = 1:length(tracks)
        
       track = tracks(i);
       
       
       trackLength = length(track.t);
       
       for j = 1:trackLength
        
                t = track.t(j);
                f = track.f(j);
                x = track.x(j);
                y = track.y(j);
                z = track.z(j);
                A = track.A(j);
                c = track.c(j);
                pval_Ar = track.pval_Ar(j);
                lifetime_s = track.lifetime_s;
                catIdx = track.catIdx;
                

                fprintf(fid,'%i, %i, %d, %i, %d, %d, %d, %d, %d, %d, %i,%d\n',...
                           i,  trackLength, t,  f,  x,  y,  z,  A,  c,lifetime_s,catIdx,pval_Ar);

            
        end
        
    %    [xx,yy,zz] = ind2sub(size(mask),find(mask == 1));
        
        
    end
    %fclose(fid);
    
    
    
        
disp('IV_tracksProcessed2csv(): done.')        
end

    
    

%end