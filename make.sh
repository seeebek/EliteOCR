#!/bin/bash

# use this when building on OSX for distribution.

APPNAME=EliteOCR
VERSION=`python -c "import re; print re.search(r'^appversion\s*=\s*\"(.+)\"', file('EliteOCR.py').read(), re.MULTILINE).group(1)"`
MAJOR=`echo ${VERSION} | cut -d . -f 1,2`

# clean
rm -rf dist build

# build
python ./setup.py py2app

# warn about superfluous resource forks / metadata
xattr -r dist/${APPNAME}.app

# Sign
#codesign --deep -s "Developer ID Application: DEVELOPERNAME" ${APPNAME}.app

# Make zip for distribution, preserving signature
DIST=${APPNAME}_mac_${VERSION}.zip
pushd dist >/dev/null
ditto -ck --keepParent --sequesterRsrc ${APPNAME}.app ../${DIST}
popd >/dev/null

# Make appcast entry
DATE=`date -u | sed s/UTC/+0000/`
SIZE=`stat -f %z ${DIST}`
cat <<EOF > appcast_${VERSION}.xml

		<item>
			<title>Version ${VERSION}</title>
			<pubDate>${DATE}</pubDate>
			<enclosure
				url="http://sourceforge.net/projects/eliteocr/files/${MAJOR}/${DIST}/download"
				sparkle:version="${VERSION}"
				length="${SIZE}"
				type="application/zip"
			/>
		</item>
EOF
