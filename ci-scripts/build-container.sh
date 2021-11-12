#!/bin/sh
set -u

IMAGE=${ARTIFACTORY_REGISTRY}/${IMAGE_BASE}
IMAGE_TAGGED=${ARTIFACTORY_REGISTRY}/${IMAGE_BASE}:${TAG}

# https://docs.docker.com/develop/develop-images/build_enhancements/#new-docker-build-secret-information
# DOCKER_BUILDKIT=1

# JF_BUILD_NAME=fmi-${CI_PROJECT_NAME}-local  # "fmi-fmi-b2share-source-local" denied by artifactory
JF_BUILD_NAME="eudat-b2share-fmi-local"
JF_BUILD_NUMBER=${CI_JOB_ID}

# Check we have needed variables
[ ${ARTIFACTORY_URL} -a ${ARTIFACTORY_USER} -a ${ARTIFACTORY_PASS} ] && echo "We has secrets...." || (echo "No needed variables found" && exit 2)
# Connect to artifactory
jf config add af-server --artifactory-url=${ARTIFACTORY_URL} --user=${ARTIFACTORY_USER} --password=${ARTIFACTORY_PASS}
jf config show

# Build the image
# docker build \
#   --rm \
#   --no-cache \
#   --build-arg DOCKER_REGISTRY=${ARTIFACTORY_REGISTRY} \
#   --build-arg ARTIFACTORY_USER=${ARTIFACTORY_USER} \
#   --build-arg ARTIFACTORY_PASS=${ARTIFACTORY_PASSWORD} \
#   --build-arg NPM_REGISTRY=${ARTIFACTORY_NPM_REPO} \
#   --build-arg PIP_REGISTRY=${ARTIFACTORY_PIP_REPO} \
#   -t ${IMAGE} \
#   -t ${IMAGE_TAGGED} \
#   -f ./dockerfiles/Dockerfile.bk .
docker build \
  --rm \
  --cache-from ${IMAGE} \
  -t ${IMAGE} \
  -t ${IMAGE_TAGGED} \
  -f ./dockerize/Dockerfile .

# Use JFrog CLI for pushing the images to artifactory
jf rt dp ${IMAGE} eudat-docker --build-name=${JF_BUILD_NAME} --build-number=${JF_BUILD_NUMBER}
jf rt dp ${IMAGE_TAGGED} eudat-docker  --build-name=${JF_BUILD_NAME} --build-number=${JF_BUILD_NUMBER}
# Publish
jf rt bp ${JF_BUILD_NAME} ${JF_BUILD_NUMBER}

# SHA Digest available only after pushing to the repository
docker images --digests | grep ${ARTIFACTORY_REGISTRY}/${IMAGE_BASE} | grep -i "seconds ago" | grep ${TAG} | awk '{print $3}' > build_var
cat build_var

