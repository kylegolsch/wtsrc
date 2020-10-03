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
wtsrc add-alias alias url

#example
wtsrc add-alias foo https://github.com/foo.git

# removing
wtsrc remove-alias foo
```

## Initialization

Same format as tsrc except for an alias is entered instead of the url

```sh
#generic
wtsrc init alias [--branch branch_name] [--group group_name]
```

## Checking for status:

```sh
# print high level summary (branch name, and is dirty)
# directly wraps tsrc status
wtsrc summary

#print git status for each repository
wtsrc status all

#print the git status for one repo
wtsrc status path/in/workspace

#print all the differences
wtsrc diff

```


# Credits
Author: Kyle Golsch (kyle@sagelab.com)

https://www.sagelab.com