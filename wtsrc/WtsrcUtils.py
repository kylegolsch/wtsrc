import os
import wtsrc.WtsrcLogger as log

TSRC_DIRECTORY = ".tsrc"
TSRC_MANIFEST_DIR = "manifest"

def find_tsrc_directory():
    '''Tries to walk up the directory tree until the folder containing .tsrc directory is found'''

    tsrc_dir = None # assume we can't find the directory
    try:
        cur_dir = os.getcwd()
    except FileNotFoundError:
        log.fatal("Cannot be called from a deleted directory")

    while os.path.ismount(cur_dir) is False:
        test_path = os.path.join(cur_dir, TSRC_DIRECTORY)
        if os.path.exists(test_path):
            tsrc_dir = test_path
            break # we have found the directory - stop the loop
        else:
            head, tail = os.path.split(cur_dir)
            cur_dir = head

    return tsrc_dir


def find_manifest_directory():
    '''Tries to find the manifest directory or returns None'''

    tsrc_dir = find_tsrc_directory()
    if tsrc_dir:
        file_path = os.path.join(tsrc_dir, TSRC_MANIFEST_DIR)
        if os.path.exists(file_path):
            return file_path
    return None


def find_tsrc_root():
    '''Tries to walk up the director until the root of the tsrc workspace is found'''

    tsrc_dir = find_tsrc_directory()
    if tsrc_dir:
        head, tail = os.path.split(tsrc_dir)
        return head
    else:
        return None


def find_file_in_manifest_dir(file_name):
    '''Tries to find the path to the specified file in the manifest directory'''

    manifest_dir = find_manifest_directory()
    if manifest_dir:
        file_path = os.path.join(manifest_dir, file_name)
        if os.path.exists(file_path):
            return file_path
    return None


def obj_dump(obj, name='obj'):
  for attr in dir(obj):
    print("%s.%s = %r" % (name, attr, getattr(obj, attr)))


def chdir_to_proj_root():
    # find the workspace root and change directories to that
    root = find_tsrc_root()
    if not root:
        log.fatal("Cannot change to project root: you must call from within a tsrc directory")
    os.chdir(root)


def chdir_to_repo(repo_path, overide_manifest=True):
    '''Tries to change to the repo directory'''

    special_paths={}
    if(overide_manifest):
        special_paths['manifest'] = os.path.join(TSRC_DIRECTORY, TSRC_MANIFEST_DIR)

    # find the workspace root and change directories to that
    root = find_tsrc_root()
    if not root:
        log.fatal("Cannot change to repo: you must call from within a tsrc directory")
    os.chdir(root)

    # override the path if needed
    if(repo_path in special_paths):
        new_path = special_paths[repo_path]
        if(os.path.exists(repo_path)):
            log.warning("'{0}' path was overriden to '{1}'".format(repo_path, new_path))
        repo_path = new_path

    if(not os.path.exists(repo_path)):
        log.fatal("The repo path '{}' was not found".format(repo_path))

    os.chdir(repo_path)


def chdir_to_manifest_dir():
    '''Tries to change directories to where the manifest file is located'''

    manifest_dir = find_manifest_directory()
    if not manifest_dir:
        log.fatal("Cannot change to manifest: you must call from within a tsrc directory")

    os.chdir(manifest_dir)
