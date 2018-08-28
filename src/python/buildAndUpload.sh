#https://packaging.python.org/tutorials/packaging-projects/
rm -r build
rm -r dist
rm -r pylattice.egg-info
python3 setup.py sdist bdist_wheel
twine upload dist/*
