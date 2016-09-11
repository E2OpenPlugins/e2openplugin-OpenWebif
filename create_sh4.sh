#!/bin/bash

D=$(pushd $(dirname $0) &> /dev/null; pwd; popd &> /dev/null)
P=${D}/ipkg.tmp.$$
B=${D}/ipkg.build.$$

pushd ${D} &> /dev/null
VER=$(head -n 3 CHANGES.md | grep -i '## Version' | sed 's/^## Version \([[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+\)/\1/')
GITVER=e2openpluginsgit$(git log -1 --format="%ci" | awk -F" " '{ print $1 }' | tr -d "-")
PKG=${D}/enigma2-plugin-extensions-openwebif_${VER}-${GITVER}_sh4.ipk
popd &> /dev/null

mkdir -p ${P}
mkdir -p ${P}/CONTROL
mkdir -p ${B}

cat > ${P}/CONTROL/control << EOF
Package: enigma2-plugin-extensions-openwebif
Version: ${VER}-${GITVER}-r0
Description: Control your receiver with a browser
Architecture: sh4
Section: extra
Priority: optional
Maintainer: E2OpenPlugins members
Homepage: https://github.com/E2OpenPlugins/e2openplugin-OpenWebif
Depends: rcs
Source: https://github.com/E2OpenPlugins/e2openplugin-OpenWebif
EOF

mkdir -p ${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/
cp -rp ${D}/plugin/* ${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/
for f in $(find ./locale -name *.po ); do
	l=$(echo ${f%} | sed 's/\.po//' | sed 's/.*locale\///')
	mkdir -p ${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/locale/${l%}/LC_MESSAGES
	msgfmt -o ${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/locale/${l%}/LC_MESSAGES/OpenWebif.mo ./locale/$l.po
done

perl -0pi -e "s#pressMenuRemote\('174'\)#pressMenuRemote('102')#s" "${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/main.tmpl"
perl -0pi -e "s#pressMenuRemote\((?:'|)174(?:'|)\)#pressMenuRemote('102')#s" ${P}/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/static/remotes/*.html
tar -C ${P} -czf ${B}/data.tar.gz . --exclude=CONTROL
tar -C ${P}/CONTROL -czf ${B}/control.tar.gz .

echo "2.0" > ${B}/debian-binary

cd ${B}
ls -la
ar -r ${PKG} ./debian-binary ./data.tar.gz ./control.tar.gz 
cd -

rm -rf ${P}
rm -rf ${B}
