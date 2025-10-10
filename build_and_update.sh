# remove previous builds in dist folder
rm  dist/*
python -m build
python -m twine upload dist/*