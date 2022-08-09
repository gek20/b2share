# Use builder image. It has some preinstalled dependencies
FROM eudat-docker.artifactory.ci.csc.fi/builder-cos7 AS base

# LABEL maintainer Petri Laihonen <petri.laihonen@csc.fi>
LABEL maintainer Johannes Lares <johannes.lares@csc.fi>

EXPOSE 5000

# # Supposedly helps with pip time-outs.
# ENV PIP_DEFAULT_TIMEOUT=100

RUN \
    yum -y update && \
    # yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install wget gcc-c++ make openssl-devel \
                   postgresql-devel mysql-devel supervisor \
                   git libffi-devel python-devel libxml2-devel libxml2 \
                   libxslt-devel zlib-devel libxslt http-parser && \
    yum -y install python36 python36-pip python36-devel uwsgi-plugin-python36 uwsgi && \
    curl -sL https://rpm.nodesource.com/setup_14.x | bash - && \
    yum install -y nodejs && \
    yum clean all && \
    # define locale
    localedef -c -f UTF-8 -i en_US en_US.UTF-8 && \
    python3 -m pip install --upgrade pip setuptools==57.5.0 wheel && \
    python3 --version && \
    pip3 --version

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"
ENV B2SHARE_WEBUI_MATOMO_URL=''
ENV B2SHARE_WEBUI_MATOMO_SITEID=''

#
# Install public-license-selector
#

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git && \
    cd public-license-selector && \
    npm install && \
    node --version && npm --version && \
    mv webpack.config.js webpack.config.js.0 && \
    echo "require('es6-promise').polyfill();" > webpack.config.js && \
    cat webpack.config.js.0 >> webpack.config.js && \
    npm install es6-promise && \
    npm run build && \
    node_modules/webpack/bin/webpack.js -p  && \
    mkdir -p /eudat/b2share/webui/app/vendors && \
    cp dist/license-selector.* /eudat/b2share/webui/app/vendors/


#
# Install B2Share webui module and dependencies
# NO NEED TO BUILD UI AT THIS STAGE, BUILDED AT GITLAB CI PREVIOUS JOB
#

WORKDIR /eudat
ADD ./webui/package.json b2share/webui/package.json
ADD ./webui/copy_files.sh b2share/webui/copy_files.sh

# WORKDIR /eudat/b2share/webui
# RUN npm install --unsafe-perm

#
# UWSGI Config
#

WORKDIR /eudat
ADD dockerize/uwsgi.ini b2share/uwsgi/uwsgi.ini

#
# Install python module and dependencies
#

WORKDIR /eudat/b2share
ADD setup.py setup.py
ADD b2share/version.py b2share/version.py
ADD requirements.txt requirements.txt
COPY shim/get-agent-values.py /usr/local/bin/
COPY wheels wheels

RUN pip3 install --no-index --find-links=./wheels -r requirements.txt && \
    pip3 install -e .

RUN rm /root/.pip/pip.conf

#nWORKDIR /eudat/b2share/demo
# ADD demo/setup.py setup.py
# RUN pip3 install -e .

COPY dockerize/b2share.sh /eudat/
COPY dockerize/supervisord.conf /etc/

#
# Copy the rest of B2Share files
#

WORKDIR /eudat
ADD . b2share

WORKDIR /eudat/b2share
COPY webui webui

#
# BUILD UI, NO NEED!!!
#

# WORKDIR /eudat/b2share/webui
# RUN npm install --unsafe-perm
# RUN node_modules/webpack/bin/webpack.js -p

WORKDIR /eudat/b2share

CMD ["/eudat/b2share.sh"]
