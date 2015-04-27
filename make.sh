#!/bin/bash

# use this when building on OSX. It'll do most of the same things as make.py,
# just without the dual build of EliteOCR & EliteOCRcmd

rm -rf dist build

pyinstaller --onedir --hidden-import=scipy.special._ufuncs_cxx EliteOCR.py

for i in tessdata translations nn_scripts text.xml plugins help commodities.json LICENSE README.md; do
	cp -r "$i" dist/EliteOCR/
done
