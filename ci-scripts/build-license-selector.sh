#!/bin/bash

set -exu

# License selector
git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git
cd public-license-selector || exit
npm install
node --version && npm --version
mv webpack.config.js webpack.config.js.0
echo "require('es6-promise').polyfill();" > webpack.config.js
cat webpack.config.js.0 >> webpack.config.js
npm install es6-promise
npm run build
node_modules/webpack/bin/webpack.js -p
mkdir -p ../webui/app/vendors
cp dist/license-selector.* ../webui/app/vendors/
cd .. || exit
