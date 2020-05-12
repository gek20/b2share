FROM node:10 as react-build
#
# Install public-license-selector
#
WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git public-license-selector

WORKDIR /eudat/public-license-selector
RUN npm install
RUN npm install es6-promise #NTS: Is this needed
RUN npm run build

RUN node_modules/webpack/bin/webpack.js -p
RUN mkdir -p /eudat/b2share/webui/app/vendors
RUN cp dist/license-selector.* /eudat/b2share/webui/app/vendors/

#
# Install B2Share webui module and dependencies
#
WORKDIR /eudat/b2share
ADD webui webui

WORKDIR /eudat/b2share/webui
ADD ./webui/package.json package.json
ADD ./webui/copy_files.sh copy_files.sh

RUN npm install --unsafe-perm

RUN node_modules/webpack/bin/webpack.js -p

CMD ["cat /eudat/b2share/webui/app/b2share-bundle.js"]

# docker run --rm eudatb2share/b2share-ui cat /eudat/b2share/webui/app/b2share-bundle.js > ./b2share-bundle.js
