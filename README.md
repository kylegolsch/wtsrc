# wtsrc
Wrapper around tsrc

It will save a file .wtsrcdata in your home directory to store aliases to repos.

# Installation

```sh
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

## Manifest

You can make edits to the manifest repo by accessing the hidden directory .tsrc/manifest

```sh
# print the status the manifest repo located in .tsrc/manifest
wtsrc manifest -- status

# if you want to add, commit and push changes to the manifest repo
wtsrc manifest git add wtsrc.yml

# commiting the change (needs improvement on syntax)
wtsrc manifest git commit -m "updating\ to\ be\ compatible\ with\ wtsrc\ 1.4"

# push the changes
wtsrc manifest git push


```

## Pre/post Actions

Look into the example folder for some examples of pre/post actions


# Credits
Author: Kyle Golsch (kyle@sagelab.com)

https://www.sagelab.com