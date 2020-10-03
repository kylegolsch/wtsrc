import os

TSRC_DIRECTORY = ".tsrc"

def find_tsrc_directory():
    '''Tries to walk up the directory tree until .tsrc directory is found'''

    tsrc_dir = None # assume we can't find the directory
    cur_dir = os.getcwd()

    while os.path.ismount(cur_dir) is False:
        test_path = os.path.join(cur_dir, TSRC_DIRECTORY)
        if os.path.exists(test_path):
            tsrc_dir = test_path
            break # we have found the directory - stop the loop
        else:
            head, tail = os.path.split(cur_dir)
            cur_dir = head

    return tsrc_dir


def find_tsrc_root():
    '''Tries to walk up the director until the root of the tsrc workspace is found'''

    tsrc_dir = find_tsrc_directory()
    if(tsrc_dir):
        head, tail = os.path.split(tsrc_dir)
        return head
    else:
        return None