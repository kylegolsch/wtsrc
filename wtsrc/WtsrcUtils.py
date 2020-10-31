import os
import shutil
from wtsrc.WtsrcSettings import MANIFEST_DIRECTORY, TSRC_DIRECTORY
import wtsrc.WtsrcLogger as log


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


def find_project_root():
    '''Tries to walk up the director until the root of the tsrc workspace is found'''

    tsrc_dir = find_tsrc_directory()
    if tsrc_dir:
        head, tail = os.path.split(tsrc_dir)
        return head
    else:
        return None


def find_directory_in_project(proj_dir):
    '''Tries the path in the project or returns None'''
    path = None
    root = find_project_root()
    if root:
        file_path = os.path.join(root, proj_dir)
        if os.path.exists(file_path):
            path = file_path
    return path


def find_file_in_project(proj_dir, file_name):
    '''Tries to find the path to a file in a directory relative to the project root'''
    path = None
    proj_dir_path = find_directory_in_project(proj_dir)
    if proj_dir_path:
        file_path = os.path.join(proj_dir_path, file_name)
        if os.path.exists(file_path):
            path = file_path
    return path


def obj_dump(obj, name='obj'):
  for attr in dir(obj):
    print("%s.%s = %r" % (name, attr, getattr(obj, attr)))


def chdir_to_proj_root():
    # find the workspace root and change directories to that
    root = find_project_root()
    if not root:
        log.fatal("Cannot change to project root: you must call from within a tsrc directory")
    os.chdir(root)


def chdir_to_repo(repo_path, overide_manifest=True):
    '''Tries to change to the repo directory'''

    special_paths={}
    if(overide_manifest):
        special_paths['manifest'] = MANIFEST_DIRECTORY

    # find the workspace root and change directories to that
    root = find_project_root()
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


def chdir_to_proj_dir(proj_dir):
    '''Tries to change directories to specified path'''

    proj_dir_path = find_directory_in_project(proj_dir)
    if not proj_dir_path:
        log.fatal("Could not find the specified path {p}".format(p=proj_dir))

    os.chdir(proj_dir_path)


def find_manifest_directory():
    return find_directory_in_project(MANIFEST_DIRECTORY)


def find_file_in_manifest_dir(file_name):
    return find_file_in_project(MANIFEST_DIRECTORY, file_name)


def find_file_in_tsrc_dir(file_name):
    return find_file_in_project(TSRC_DIRECTORY, file_name)


def chdir_to_manifest_dir():
    chdir_to_proj_dir(MANIFEST_DIRECTORY)


def nuke_dir(dir_to_nuke):

    if not os.path.exists(TSRC_DIRECTORY):
        log.fatal("You must call from the root of the project for safety.  The .tsrc directory was not found in the cwd")

    files = [f for f in os.listdir(dir_to_nuke) if os.path.isfile(os.path.join(dir_to_nuke, f))]
    dirs = [d for d in os.listdir(dir_to_nuke) if os.path.isdir(os.path.join(dir_to_nuke, d))]
    for file in files:
        os.unlink(file)
    for cur_dir in dirs:
        shutil.rmtree(cur_dir)


def nuke_root():
    root = find_project_root()
    if not root:
        log.fatal("Could not find the project root")
    nuke_dir(root)
