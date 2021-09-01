#!/bin/sh
set -u

IMAGE=${ARTIFACTORY_DOCKER_REPO}/${IMAGE_BASE}:${TAG}

# https://docs.docker.com/develop/develop-images/build_enhancements/#new-docker-build-secret-information
# DOCKER_BUILDKIT=1

JF_BUILD_NAME=fmi-${CI_PROJECT_NAME}-local
JF_BUILD_NUMBER=${CI_JOB_ID}

# Build the image 
# docker build \
#   --rm \
#   --no-cache \
#   --build-arg DOCKER_REGISTRY=${ARTIFACTORY_DOCKER_REPO} \
#   --build-arg ARTIFACTORY_USER=${ARTIFACTORY_USER} \
#   --build-arg ARTIFACTORY_PASS=${ARTIFACTORY_PASSWORD} \
#   --build-arg NPM_REGISTRY=${ARTIFACTORY_NPM_REPO} \
#   --build-arg PIP_REGISTRY=${ARTIFACTORY_PIP_REPO} \
#   -t ${IMAGE} \
#   -t ${IMAGE_BASE} \
#   -f ./dockerfiles/Dockerfile.bk .

docker build \
  --rm --no-cache \
  -t ${IMAGE} \
  -t ${IMAGE_BASE} \
  -f ./dockerize/Dockerfile .

####  Needs troubleshooting!               ####
####  Most likely artifactory side problem ####
# # Use JFrog CLI
# # docker-push
# jfrog rt dp ${IMAGE} inar-docker --build-name=${JF_BUILD_NAME} --build-number=${JF_BUILD_NUMBER}
# # build-publish
# jfrog rt bp ${JF_BUILD_NAME} ${JF_BUILD_NUMBER}

# Not using jfrog
docker push ${IMAGE}

# SHA Digest available only after pushing to the repository
echo "$(docker images --digests | grep ${ARTIFACTORY_DOCKER_REPO}/${IMAGE_BASE} | grep ${TAG} | awk '{print $3}')" > build_var
cat build_var