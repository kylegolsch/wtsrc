# wtsrc

Wrapper around tsrc

It will save a file .wtsrcdata in your home directory to store aliases to repos.

# Installation

```sh
# 1. download this repo
# 2. change directory to the download
# 3. install the pre-requisities
pip[3] install -r requirements.txt

# 4. run the installer
python[3] setup.py install
```

# Usage


## Aliases

The url of a repo can be given an alias so that the full url doesn't need to be entered each time.

```sh
#generic
wtsrc add-alias ALIAS_NAME MANIFEST_REPO_URL

#example
wtsrc add-alias foo https://github.com/foo.git

# removing
wtsrc remove-alias ALIAS_NAME

```


## Initialization

Same format as tsrc except for an alias is entered instead of the url

```sh
# by alias
wtsrc init --alias ALIAS [--branch BRANCH_NAME] [--group GROUP_NAME]

# by repo url
wtsrc init --url MANIFEST_REPO_URL [--branch BRANCH_NAME] [--group GROUP_NAME]
```


## Checking for status:

You should not clone any repos into a directory called 'manifest'

```sh
# print high level summary (branch name, and is dirty)
# directly wraps tsrc status
wtsrc status

#print git status for each repository
# wraps tsrc foreach -- git status
wtsrc status all

#print the git status for one repo
wtsrc status path/in/workspace/repo

#print all the differences
wtsrc diff

#open the mergetool
wrtsrc mergetool path/in/workspace/repo
```


## Running commands on repos

You can run a command on just one repo - or all repos (all repos excludes manifest)

```sh
# for all repos - excluding manifest
wtsrc foreach -c "command to run from root of repo on command line"
# example - list the directoroy contents of all repos
wtsrc foreach -c "ls"


# for all repos - excluding manifest
wtsrc forsingle REPO_PATH -c "command to run from root of repo on command line"
# example - list the directoroy contents of repo 'target1/repo1'
wtsrc forsingle target1/repo1 -c "ls"
```


## Manifest

You can make edits to the manifest repo by accessing the hidden directory .tsrc/manifest
To access the manifest repo, you can simply specify 'manifest' as the REPO_PATH - .tsrc/manifest will be substituted

```sh
# print the status the manifest repo located in .tsrc/manifest
wtsrc status manifest

# if you want to add, commit and push changes to the manifest repo
wtsrc forsingle manifest -c "git add wtsrc.yml"

# commiting the change
wtsrc forsingle manifest -c "git commit -m 'update wtsrc.yml'"

# push the changes
wtsrc forsingle manifest -c "git push"
```


## Pre/post Actions

Look into the example folder for some examples of pre/post actions


# Credits

Author: Kyle Golsch (kyle@sagelab.com)

https://www.sagelab.com
