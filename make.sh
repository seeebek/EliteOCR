#!/bin/bash

# use this when building on OSX for distribution.

APPNAME=EliteOCR
VERSION=`python -c "import re; print re.search(r'^appversion\s*=\s*\"(.+)\"', file('EliteOCR.py').read(), re.MULTILINE).group(1)"`

# clean
rm -rf dist build

# build
python ./setup.py py2app

# warn about superfluous resource forks / metadata
xattr -r dist/${APPNAME}.app

# Sign
#codesign --deep -s "Developer ID Application: DEVELOPERNAME" ${APPNAME}.app

# Make zip for distribution, preserving signature
pushd dist >/dev/null
ditto -ck --keepParent --sequesterRsrc ${APPNAME}.app ../${APPNAME}_${VERSION}.zip
popd >/dev/null
