import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylattice",
    version="0.1.3",
    author="Joh Schoeneberg",
    author_email="joh@schoeneberglab.org",
    description="A python library for lattice light-sheet image analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JohSchoeneberg/pyLattice",
    packages=setuptools.find_packages(),
    #packages=['pylattice'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ),
    install_requires=[
    ],
)
