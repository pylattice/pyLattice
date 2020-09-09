.. pyLattice documentation master file, created by
   sphinx-quickstart on Fri Jul 27 11:53:40 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   
.. http://dont-be-afraid-to-commit.readthedocs.io/en/latest/documentation.html


.. http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer

************
pyLattice
************

A python library for advanced lattice light-sheet image analysis.

Welcome!

Visit `pyLattice on Github <https://github.com/JohSchoeneberg/pyLattice>`_

.. image:: pyLattice_logo.png
    :width: 1200px
    :align: center
    :alt: fig1
	

Installation
************

clone or download the repository
::
	pip install pylattice
	pip install -r requirements.txt
	cd src/jupyter
	jupyter notebook


You can find the package on `pypi`_.

in browser open 
::
	src/jupyter/latticeFrame_showFrame.ipynb

Test data
************

A small test data set can be found here:
https://www.dropbox.com/sh/znznvp1lmvwfykp/AADzJB456aFHll1bYCPzdQhNa?dl=0

Manual
************

Please read the `manual`_ to get started.

Tutorials
************

Please find tutorials to pyLattice `here`_

FAQ
************

[Lattice Light-Sheet Microscopy](https://en.wikipedia.org/wiki/Lattice_light-sheet_microscopy)

Cite
************

Please `cite`_ our work if you find pyLattice useful: 

- pyLattice: https://doi.org/10.1091/mbc.E18-06-0375
- pyLattice deep_learning: https://doi.org/10.1109/BIBM47256.2019.8983012


Contribute
************

Please help us to make LLSM imaging more accessible to the community!
Fork the repo, add code and create a pull request.
Here you can find our `Contributor Guidelines`.: https://docs.google.com/document/d/1Gd5Fr0_sTnez1NEBM7xfisXZ2jR5IbkoLws6EY2Cg2Y/edit?usp=sharing


.. _dataset: https://www.dropbox.com/sh/znznvp1lmvwfykp/AADzJB456aFHll1bYCPzdQhNa?dl=0
.. _manual: https://pylattice.readthedocs.io/en/latest/index.html
.. _here: https://github.com/JohSchoeneberg/pyLattice_tutorials
.. _llsmFAQ: https://en.wikipedia.org/wiki/Lattice_light-sheet_microscopy
.. _cite: https://doi.org/10.1091/mbc.E18-06-0375
.. _pypi: https://pypi.org/project/pylattice/

References
************

- scikit http://scikit-image.org
- ChimeraX https://www.cgl.ucsf.edu/chimerax/
- llsm tools https://github.com/francois-a/llsmtools
- utrack https://www.utsouthwestern.edu/labs/danuser/software/#utrack_ancs
- Joh Schöneberg http://www.schoeneberglab.org
- The Betzig Lab https://www.janelia.org/lab/betzig-lab
- The Drubin/Barnes Lab https://drubinbarneslab.berkeley.edu	
	





.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   installation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
