classdef  MovieObject < hgsetget
    % Abstract interface defining the analyis tools for movie objects
    % (movies, movie lists...)
%
% Copyright (C) 2017, Danuser Lab - UTSouthwestern 
%
% This file is part of u-track.
% 
% u-track is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% u-track is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with u-track.  If not, see <http://www.gnu.org/licenses/>.
% 
% 
    
    % Sebastien Besson, Jan 2012
    
    properties (SetAccess = protected)
        createTime_             % Object creation time
        processes_ = {};        % List of analysis processes
        packages_ = {};         % List of analysis packages
    end
    
    properties
        outputDirectory_ = '';  % Default output directory for analysis
        notes_                  % User notes
        
        omeroId_                % Identifier of an OMERO object
        omeroSave_ = false      % Status of the saving to OMERO
    end
    
    properties (Transient =true)
        omeroSession_           % Active session to an OMERO server
    end
    
    methods
        %% Set/get methods
        function set.outputDirectory_(obj, path)
            % Set the ouput
            endingFilesepToken = [regexptranslate('escape',filesep) '$'];
            path = regexprep(path,endingFilesepToken,'');
            obj.checkPropertyValue('outputDirectory_',path);
            obj.outputDirectory_=path;
        end
        
        function checkPropertyValue(obj,property, value)
            % Check if a property/value pair can be set up
            
            % Test if the property is unchanged
            if isequal(obj.(property),value), return; end
            
            % Test if the property is writable
            if(~obj.checkProperty(property))
                propName = lower(property(1:end-(property(end) == '_')));
                error('lccb:set:readonly',...
                    ['The ' propName ' has been set previously and cannot be changed!']);
            end
            
            % Test if the supplied value is valid
            if(~obj.checkValue(property,value))
                propName = lower(property(1:end-(property(end) == '_')));
                error('lccb:set:invalid',...
                    ['The supplied ' propName ' is invalid!']);
            end
        end
        
        function status = checkProperty(obj,property)
            % Returns true/false if the non-empty property is writable
            status = isempty(obj.(property));
            if status, return; end
            
            % Allow user to rewrite on some properties (paths, outputDirectory, notes)
            switch property
                case {'notes_'};
                    status = true;
                case {'outputDirectory_',obj.getPathProperty,obj.getFilenameProperty};
                    stack = dbstack;
                    if any(cellfun(@(x)strcmp(x,[class(obj) '.sanityCheck']),{stack.name})),
                        status  = true;
                    end
                    if any(cellfun(@(x)strcmp(x,[class(obj) '.relocate']),{stack.name})),
                        status  = true;
                    end
            end
        end
        
        function set.notes_(obj, value)
            % Set the notes
            obj.checkPropertyValue('notes_',value);
            obj.notes_=value;
        end
        
        function value = getPath(obj)
            % Retrieve the folder path to save the object
            value = obj.(obj.getPathProperty);
        end
        
        function setPath(obj, value)
            % Set the folder path for saving the object
            obj.(obj.getPathProperty) = value;
        end
        
        function value = getFilename(obj)
            % Retrieve the filename for saving the object
            value = obj.(obj.getFilenameProperty);
        end
        
        function setFilename(obj, value)
            % Set the filename for saving the object
            obj.(obj.getFilenameProperty) = value;
        end
        
        function fullPath = getFullPath(obj, askUser)
            % Retrieve the full path for saving the object
            
            if nargin < 2, askUser = true; end
            hasEmptyComponent = isempty(obj.getPath) || isempty(obj.getFilename);
            hasDisplay = feature('ShowFigureWindows');
            
            if any(hasEmptyComponent) && askUser && hasDisplay
                if ~isempty(obj.getPath),
                    defaultDir = obj.getPath;
                elseif ~isempty(obj.outputDirectory_)
                    defaultDir = obj.outputDirectory_;
                else
                    defaultDir = pwd;
                end
                
                % Open a dialog box asking where to save the movie object
                movieClass = class(obj);
                objName = regexprep(movieClass,'([A-Z])',' ${lower($1)}');
                defaultName = regexprep(movieClass,'(^[A-Z])','${lower($1)}');
                [filename,path] = uiputfile('*.mat',['Find a place to save your' objName],...
                    [defaultDir filesep defaultName '.mat']);
                
                if ~any([filename,path]),
                    fullPath=[];
                else
                    fullPath = [path, filename];
                    % Set new path and filename
                    obj.setPath(path);
                    obj.setFilename(filename);
                end
            else
                if all(hasEmptyComponent),
                    fullPath = '';
                else
                    fullPath = fullfile(obj.getPath(), obj.getFilename());
                end
            end
            
        end
        %% Backup functions
        function [backupPath, backupDir, fullPath] = getBackupPath(obj,timestamp)
            fileName = obj.getFilename();
            if(isempty(fileName) || isempty(obj.getPath()))
                backupPath = '';
                backupDir = '';
                fullPath = '';
            else
                sep = filesep;
                path = obj.getPath();
                % Should be equivalent to obj.getFullPath()
                fullPath = [path sep fileName];
                if(nargin < 2)
                    % ISO 8601, number 30
                    timestamp = datestr(now,'yyyymmddTHHMMSS');
                end
                % Append timestamp and move into a backup subdirectory
                fileName = [timestamp '_' fileName];
                backupDir = [path sep 'backups'];
                backupPath = [backupDir sep fileName];
            end
        end
        function success = moveToBackup(obj,varargin)
            % Move old file to getBackupPath
            [backupPath, backupDir, fullPath] = obj.getBackupPath(varargin{:});
            success = false;
            if ~isempty(fullPath) && ~isempty(backupPath)
                try
                    % Make directory if it does not exist
                    if(~exist(backupDir,'dir'))
                        mkdir(backupDir);
                    end
                    movefile(fullPath,backupPath,'f');
                    success = true;
                catch err
                    % Do not warn if fullPath does not exist
                    % It usually does, so we catch it rather than pretest
                    if(strcmp(err.identifier,'MATLAB:MOVEFILE:OSError') && ...
                       exist(fullPath,'file') ~= 2)
                    % MATLAB:MOVIEFILE:OSError is an undocumented error if
                    % the file does not exist
                    % do nothing
                    elseif(~strcmp(err.identifier,'MATLAB:MOVEFILE:FileDoesNotExist'))
                        warning('MovieObject:saveBackup:Failure', ...
                            'Failed to save backup\n%s to\n%s', ...
                            fullPath,backupPath);
                    end
                end
            end
        end

        %% Functions to manipulate process object array
        function addProcess(obj, newprocess)
            % Add new process to the processes list
            assert(isa(newprocess,'Process'));
            obj.processes_ = horzcat(obj.processes_, {newprocess});
        end
        
        function proc = getProcess(obj, i)
            % Return process corresponding to the specified index
            assert(insequence_and_scalar(i,1,numel(obj.processes_)), ['Process Index [' num2str(i) '] does Not exist!']);
            proc = obj.processes_{i};
        end
        
        function status = unlinkProcess(obj, process)
            % Unlink process from processes list
            
            id = [];
            status = false;
            if isa(process, 'Process')
                id = find(cellfun(@(x) isequal(x,process), obj.processes_), 1);
            elseif insequence_and_scalar(process, 1,numel(obj.processes_))
                id = process;
            end
            
            if ~isempty(id),
                obj.processes_(id) = [ ];
                status = true;
            end
        end
        
        function deleteProcess(obj, process)
            % Delete process from processes list and parent packages
            %
            % INPUT:
            %        process - Process object or index
            
            % Check input
            if isa(process, 'Process')
                pid = find(cellfun(@(x) isequal(x,process), obj.processes_),1);
                assert(~isempty(pid),'The given process is not in current movie processes list.');
            elseif isnumeric(process)
                pid = process;
                process = obj.getProcess(pid);
            else
                error('Please provide a Process object or a valid process index of movie data processes list.')
            end
            
            % Check process validity
            isValid = ~isempty(process) && process.isvalid;
            
            if isValid
                % Unassociate process from parent packages
                [packageID, procID] = process.getPackageIndex();
                for i=1:numel(packageID)
                    obj.getPackage(packageID(i)).setProcess(procID(i), []);
                end
            end
            
            if isValid && isa(process.owner_, 'MovieData')
                % Remove process from list for owner and descendants
                for movie = [process.owner_ process.owner_.getDescendants()]
                    movie.unlinkProcess(process);
                end
            else
                obj.unlinkProcess(process);
            end
            
            % Delete process object
            if isValid, delete(process); end
        end
        
        function replaceProcess(obj, pid, newprocess)
            % Replace process object by another in the processes list
            
            % Input check
            ip=inputParser;
            ip.addRequired('pid', @(x) isa(x,'Process') || ...
                isnumeric(x) && insequence(x, 1,numel(obj.processes_)));
            ip.addRequired('newprocess', @(x) isa(x,'Process'));
            ip.parse(pid, newprocess);
            
            % Retrieve process index if input is of process type
            if isa(pid, 'Process')
                pid = find(cellfun(@(x)(isequal(x,pid)), obj.processes_));
                assert(isscalar(pid))
            end
            
            [packageID, procID] = obj.getProcess(pid).getPackageIndex();
            
            % Check new process is compatible with parent packages
            if ~isempty(packageID)
                for i=1:numel(packageID)
                    isValid = isa(newprocess,...
                        obj.getPackage(packageID(i)).getProcessClassNames{procID(i)});
                    assert(isValid, 'Package class compatibility prevents process process replacement');
                end
            end
            
            % Delete old process and replace it by the new one
            oldprocess = obj.getProcess(pid);
            if isa(oldprocess.owner_, 'MovieData')
                % Remove process from list for owner and descendants
                for movie = [oldprocess.owner_ oldprocess.owner_.getDescendants()]
                    id = find(cellfun(@(x) isequal(x, oldprocess), movie.processes_),1);
                    if ~isempty(id), movie.processes_{id} = newprocess; end
                end
            else
                obj.processes_{pid} = newprocess;
            end
            delete(oldprocess);
            
            % Associate new process in parent packages
            if ~isempty(packageID),
                for i=1:numel(packageID)
                    obj.getPackage(packageID(i)).setProcess(procID(i),newprocess);
                end
            end
        end
        
        function iProc = getProcessIndex(obj, type, varargin)
            % Retrieve the existing process(es) of a given type
            if isa(type, 'Process'), type = class(type); end
            iProc = getIndex(obj.processes_, type, varargin{:});
        end
        
        %% Functions to manipulate package object array
        function addPackage(obj, newpackage)
            % Add a package object to the package list
            assert(isa(newpackage,'Package'));
            obj.packages_ = horzcat(obj.packages_ , {newpackage});
        end
        
        function package = getPackage(obj, i)
            % Return the package corresponding to the specified index
            assert(insequence_and_scalar(i,1,numel(obj.packages_)));
            package = obj.packages_{i};
        end
        
        function status = unlinkPackage(obj, package)
            % Unlink a package from the packages list
            
            id = [];
            status = false;
            if isa(package, 'Package')
                id = find(cellfun(@(x) isequal(x,package), obj.packages_), 1);
            elseif insequence_and_scalar(package, 1,numel(obj.packages_))
                id = package;
            end
            
            if ~isempty(id),
                obj.packages_(id) = [ ];
                status = true;
            end
        end
        
        function deletePackage(obj, package)
            % Remove thepackage object from the packages list
            
            % Check input
            if isa(package, 'Package')
                pid = find(cellfun(@(x) isequal(x, package), obj.packages_),1);
                assert(~isempty(pid),'The given package is not in current movie packages list.');
            elseif isnumeric(package)
                pid = package;
                package = obj.getPackage(pid);
            else
                error('Please provide a Package object or a valid package index of movie data processes list.')
            end
            
            % Check package validity
            isValid = ~isempty(package) && package.isvalid;
            
            if isValid && isa(package.owner_, 'MovieData')
                % Remove package from list for owner and descendants
                for movie = [package.owner_ package.owner_.getDescendants()]
                    movie.unlinkPackage(package);
                end
            else
                obj.unlinkPackage(package);
            end
            
            % Delete package object
            if isValid, delete(package); end
        end
        
        function iPackage = getPackageIndex(obj, type, varargin)
            % Retrieve the existing package(s) of a given type
            if isa(type, 'Package'), type = class(type); end
            iPackage = getIndex(obj.packages_, type, varargin{:});
        end
        
        %% Miscellaneous functions
        function askUser = sanityCheck(obj, varargin)
            % Check sanity of movie object
            %
            % Check if the path and filename stored in the movie object are
            % the same as the input if any. If they differ, call the
            % movie object relocation routine. Use a dialog interface to ask
            % for relocation if askUser is set as true and return askUser.
            ip = inputParser();
            ip.addOptional('path', '', @ischar);
            ip.addOptional('filename', '', @ischar);
            ip.addOptional('askUser', true, @isscalar);
            ip.addOptional('full', true, @isscalar);
            ip.parse(varargin{:});
            askUser = ip.Results.askUser;

            if ~isempty(ip.Results.path)
                % Remove ending file separators from paths
                endingFilesepToken = [regexptranslate('escape',filesep) '+$'];
                oldPath = regexprep(obj.getPath(),endingFilesepToken,'');
                newPath = regexprep(ip.Results.path,endingFilesepToken,'');
                
                % If different path
                hasDisplay = feature('ShowFigureWindows');
                if ~strcmp(oldPath, newPath)
                    full = ip.Results.full;  % flag for full relocation
                    if askUser && hasDisplay
                        if isa(obj,'MovieData')
                            type='movie';
                            components='channels';
                        elseif isa(obj,'MovieList')
                            type='movie list';
                            components='movies';
                        else
                            error('Non supported movie object');
                        end
                        relocateMsg=sprintf(['The %s and its analysis will be relocated from \n%s to \n%s.\n'...
                            'Should I relocate its %s as well?'],type,oldPath,newPath,components);
                        confirmRelocate = questdlg(relocateMsg,['Relocation - ' type],'Yes to all','Yes','No','Yes');
                        full = ~strcmp(confirmRelocate,'No');
                        askUser = ~strcmp(confirmRelocate,'Yes to all');
                    end

                    % Get old and new relocation directories
                    [oldRootDir, newRootDir]=getRelocationDirs(oldPath,newPath);
                    oldRootDir = regexprep(oldRootDir,endingFilesepToken,'');
                    newRootDir = regexprep(newRootDir,endingFilesepToken,'');
                    
                    % Relocate the object
                    fprintf(1,'Relocating analysis from %s to %s\n',oldRootDir,newRootDir);
                    obj.relocate(oldRootDir, newRootDir, full);
                end
            end
            if ~isempty(ip.Results.filename),
                obj.setFilename(ip.Results.filename);
            end
            
            if isempty(obj.outputDirectory_),
                warning('lccb:MovieObject:sanityCheck',...
                    'Empty output directory!');
            end
        end
        
        function relocate(obj,oldRootDir,newRootDir)
            % Relocate the paths of all components of the movie object
            %
            % The relocate method automatically relocates the output directory,
            % as well as the paths in each process and package of the movie
            % assuming the internal architecture of the  project is conserved.
            
            % Relocate output directory and set the ne movie path
            obj.outputDirectory_=relocatePath(obj.outputDirectory_,oldRootDir,newRootDir);
            obj.setPath(relocatePath(obj.getPath,oldRootDir,newRootDir));
            
            % Relocate the processes
            for i=1:numel(obj.processes_), obj.processes_{i}.relocate(oldRootDir,newRootDir); end
            
            % Relocate the packages
            for i=1:numel(obj.packages_), obj.packages_{i}.relocate(oldRootDir,newRootDir); end
        end
        
        function reset(obj)
            % Reset the analysis of the movie object
            obj.processes_={};
            obj.packages_={};
        end
        
        %% OMERO functions
        function status = isOmero(obj)
            % Check if the movie object is linked to an OMERO object
            status = ~isempty(obj.omeroId_);
        end
        
        function setOmeroSession(obj,session)
            % Set the OMERO session linked to the object
            obj.omeroSession_ = session;
        end
        
        function session = getOmeroSession(obj)
            % Retrieve the OMERO session linked to the object
            session = obj.omeroSession_;
        end
        
        function setOmeroSave(obj, status)
            % Set the saving status onto the OMERO server
            obj.omeroSave_ = status;
        end
        
        function id = getOmeroId(obj)
            % Retrieve the identifier of the OMERO object
            id = obj.omeroId_;
        end
        
        function setOmeroId(obj, id)
            % Set the identifier of the OMERO object
            obj.checkPropertyValue('omeroId_', id);
            obj.omeroId_ = id;
        end
        
        function status = canUpload(obj)
            % Checks if the object can be uploaded to the OMERO server
            status = obj.omeroSave_ && ~isempty(obj.getOmeroSession());
        end
        [ movieObject, process, processID ] = getOwnerAndProcess( movieObject, processClass, createProcessIfNoneExists, varargin );

    end
    
    methods(Static)

        function [obj, filepath] = loadMatFile(classname, filepath)
            % Load a movie object saves as a MAT file on disk
            
            % Retrieve the absolute path
            [status, f] = fileattrib(filepath);
            if(~status)
                if(ischar(f))
                    error('lccb:movieObject:invalidFilePath', ...
                        [f filepath]);
                else
                    error('lccb:movieObject:invalidFilePath', ...
                        ['Cannot obtain file attributes for ' filepath]);
                end
            else
                filepath = f.Name;
            end
                
            
            % Import movie object from MAT file
            try
                 % Load movie object
                 % (takes same time as checking vars via whos)
                data = load(filepath, '-mat');
            catch whosException
                ME = MException('lccb:movieObject:load', 'Fail to open file. Make sure it is a MAT file.');
                ME = ME.addCause(whosException);
                throw(ME);
            end
            
            vars = fieldnames(data);
            classes = structfun(@class,data,'UniformOutput',false);
            
            % Check if a single movie object is in the variables
            isMovie = cellfun(@(x) strcmp(x, classname) || ...
                any(strcmp(superclasses(x), classname)),struct2cell(classes));
            assert(any(isMovie),'lccb:movieObject:load', ...
                'No object of type %s is found in selected MAT file.', classname);
            assert(sum(isMovie)==1,'lccb:movieObject:load', ...
                'Multiple objects are found in selected MAT file.');
            assert(isequal(prod(cellfun('prodofsize',struct2cell(data))), 1),'lccb:movieObject:load', ...
                'Multiple objects are found in selected MAT file.');
            
            obj= data.(vars{isMovie});
        end
        
        function validator = getPropertyValidator(property)
            % Retrieve the validator for the specified property
            validator=[];
            switch(property)
                case 'outputDirectory_'
                    validator = @ischar;
                case 'notes_'
                    validator = @ischar;
                case 'omeroId_'
                    validator = @isposint;
            end
        end
        
        function status = isOmeroSession(session)
            % Check if the input is a valid OMERO session
            status = isa(session, 'omero.api.ServiceFactoryPrxHelper');
        end
        
    end
    methods (Static,Abstract)
        getPathProperty()
        getFilenameProperty()
    end
end

function iProc = getIndex(list, type, varargin)
% Find the index of a object of given class

% Input check
ip = inputParser;
ip.addRequired('list',@iscell);
ip.addRequired('type',@ischar);
ip.addOptional('nDesired',1,@isscalar);
ip.addOptional('askUser',true,@isscalar);
ip.parse(list, type, varargin{:});
nDesired = ip.Results.nDesired;
askUser = ip.Results.askUser;


iProc = find(cellfun(@(x) isa(x,type), list));
nProc = numel(iProc);

%If there are only nDesired or less processes found, return
if nProc <= nDesired, return; end

% If more than nDesired processes
if askUser
    isMultiple = nDesired > 1;
    names = cellfun(@(x) (x.getName()), list(iProc), 'UniformOutput', false);
    iSelected = listdlg('ListString', names,...
        'SelectionMode', isMultiple, 'ListSize', [400,400],...
        'PromptString', ['Select the desired ' type ':']);
    iProc = iProc(iSelected);
    assert(~isempty(iProc), 'You must select a process to continue!');
else
    warning('lccb:process', ['More than ' num2str(nDesired) ' objects '...
        'of class ' type ' were found! Returning most recent!'])
    iProc = iProc(end:-1:(end-nDesired+1));
end
end

