#!/bin/bash

# Get the current commit hash
COMMIT=$(git rev-parse  HEAD)

# add 'DIRTY' if there are local changes which have not been committed
if ! [[ -z "`git status -s`" ]]; then COMMIT="DIRTY-${COMMIT}"; fi

# Get the current git branch
BRANCH=$(git symbolic-ref --short HEAD)

# get the name of the git repo
REPO=$(basename `git rev-parse --show-toplevel`)
# NOTE: `git rev-parse --show-toplevel` will get the name of the local folder that contains `.git/`.
#       If you created it with `git clone` and did not supply a different working directory
#       then this will be same as the name of the git repo, but if you are in a different local
#       folder then you might want to replace above with the correct repo name


gcloud builds submit --config cloudbuild.yaml --substitutions \
  COMMIT_SHA=${COMMIT},BRANCH_NAME=${BRANCH},REPO_NAME=${REPO}
