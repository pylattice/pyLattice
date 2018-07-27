Debugging Matlab on Mac
=======================

If matlab throws errors like this::


	Invalid MEX-file
	'/Users/johannesschoeneberg/git/JohSchoeneberg/pyLattice/src/matlab/trackingModule/dependencies/u-track/software/mex/createDistanceMatrix.mexmaci64':
	dlopen(/Users/johannesschoeneberg/git/JohSchoeneberg/pyLattice/src/matlab/trackingModule/dependencies/u-track/software/mex/createDistanceMatrix.mexmaci64,
	6): Library not loaded: @loader_path/libmex.dylib
	Referenced from:
	/Users/johannesschoeneberg/git/JohSchoeneberg/pyLattice/src/matlab/trackingModule/dependencies/u-track/software/mex/createDistanceMatrix.mexmaci64
	Reason: image not found.

The solution can be found here:

https://stackoverflow.com/questions/48458660/library-not-loaded-loader-path-libmex-dylib-in-matlab


First, find out your matlab version::

	find /Applications/ -maxdepth 1 -type d -name 'MAT*'

In my case this is::

	MATLAB_R2017b.app	
	
In the subsequent steps, the 2017b matlab version is used. If you have a different version, replace ``MATLAB_R2017b.app`` with your version below.

You have to add the libraries to your matlab startup script::

	/Applications/MATLAB_R2017b.app/bin/.matlab7rc.sh.

Add::

	DYLD_LIBRARY_PATH="/Applications/MATLAB_R2017b.app/bin/maci64:/Applications/MATLAB_R2017b.app/sys/os/maci64"

Then startup matlab from the command line::

	/Applications/MATLAB_R2017b.app/bin/matlab