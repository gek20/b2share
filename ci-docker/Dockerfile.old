FROM eudat-docker.artifactory.ci.csc.fi/b2share-github:2.1.7

LABEL maintainer Johannes Lares <johannes.lares@csc.fi>

EXPOSE 5000

WORKDIR /eudat/b2share

# Replace original files with client specific modifications
# ADD b2share/modules/oauthclient/cscaai.py b2share/modules/oauthclient/
ADD dockerize/uwsgi.ini uwsgi/
# This does not work.
# Volume mapping overrides this.
# ADD usr/var/b2share-instance /usr/var/b2share-instance/
COPY b2share/config.py b2share/

# Fix GUI elements (POC)
COPY webui ./webui/

# Add patched invenio-stats v1.0.0a8 which contains fix
# for events-stats-file-download mapping conflict problem
# ADD invenio-stats ./invenio-stats/
# RUN pip install ./invenio-stats/

# Fix to allow writing PID and other files
RUN mkdir -p /usr/var && \
  chown 1000:1000 /eudat/b2share /usr/var

CMD ["/eudat/b2share.sh"]
