import click
import os
import pexpect
from termcolor import colored
from wtsrc.WtsrcModel import WtsrcModel
from wtsrc.WtsrcUtils import find_tsrc_root


def log_fatal(message):
    print(colored(message, 'red'))
    exit()


def chdir_to_repo(repo_path):
    '''Tries to change to the repo directory'''
    root = find_tsrc_root()
    if not root:
        log_fatal("You must call from within a tsrc directory")
        exit()

    dir = os.path.join(root, repo_path)
    if(not os.path.exists(dir)):
        log_fatal("The repo path '{}' was not found".format(repo_path))
        exit()

    os.chdir(dir)


@click.group()
def run():
    pass


def run_command(command):
    '''Executes a command on the command line and shows the results'''
    print("Running Command: " + colored(command, 'green'))
    child = pexpect.spawn(command)
    child.interact()


def do_init(manifest_url:str, branch:str, group:str, s):
    cmd = "tsrc init {r}{b}{u}{s}".format(r=manifest_url,
                                          b=" --branch {}".format(branch) if branch else "",
                                          u=" --group {}".format(group) if group else "",
                                          s=" -s" if s else "")
    run_command(cmd)

@run.command()
@click.argument('repo-url', type=str)
@click.option('--branch', type=str, default=None, help="which branch to clone (without is master)")
@click.option('--group', type=str, default=None, help="which group to clone (without is all repos)")
@click.option('-s', default=False, is_flag=True, help="set this flag if you want a shallow copy")
def init(manifest_url:str, branch:str, group:str, s):
    '''Clone the manifest and all repos'''
    do_init(manifest_url, branch, group, s)


@run.command()
@click.argument('alias', type=str)
@click.option('--branch', type=str, default=None, help="which branch to clone (without is master)")
@click.option('--group', type=str, default=None, help="which group to clone (without is all repos)")
@click.option('-s', default=False, is_flag=True, help="set this flag if you want a shallow copy")
def init_alias(alias:str, branch:str, group:str, s):
    '''Clone the manifest and all repos by its alias'''
    model = WtsrcModel.load()
    url = model.get_alias_url(alias)

    if(url == None):
        print("The alias '{}' is not known".format(alias))
    else:
        do_init(url, branch, group, s)


@run.command()
@click.argument('alias', type=str)
@click.option('--url', type=str, help="the url for the repository")
def add_alias(alias:str, url:str):
    '''Will try to add an alias and save the model'''

    if(alias is None or alias.isidentifier() == False):
        print("'{}' is not a valid alias".format(alias))
    elif(url is None):
        print("You must specify the url for the alias with the -u flag")
    else:
        model = WtsrcModel.load()
        model.add_alias(alias, url)
        model.save()


@run.command()
@click.argument('alias', type=str)
def remove_alias(alias: str):
    '''Will try to remove an alias and save the model'''
    model = WtsrcModel.load()
    model.remove_alias(alias)
    model.save()


@run.command()
def diff():
    '''Shows which files have been modified'''
    cmd = "tsrc foreach git diff-index HEAD"
    run_command(cmd)


@run.command()
def clean():
    '''deletes all local files that are not under version control'''
    cmd = "tsrc foreach -- git clean -df"
    run_command(cmd)


@run.command()
def reset():
    '''Discards/resets all uncommitted changes'''
    cmd = "tsrc foreach -- git reset --hard HEAD"
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
@click.argument('branch', type=str)
def merge(repo_path, branch):
    '''Merges a branch into a repo'''
    chdir_to_repo(repo_path)
    cmd = "git merge {}".format(branch)
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
def mergetool(repo_path):
    '''Shows the merge tool for a repo'''
    chdir_to_repo(repo_path)
    cmd = "git mergetool"
    run_command(cmd)


@run.command()
def show():
    '''Prints the saved model'''
    model = WtsrcModel.load()
    print(str(model))


@run.command()
@click.argument('repo-path', type=str, default=None, required=False)
def status(repo_path:str):
    """Shows the status of a repo at the specified path or 'all'"""
    if repo_path == None:
        cmd = 'tsrc status'
        run_command(cmd)
    elif repo_path == 'all':
        cmd = 'tsrc foreach git status'
        run_command(cmd)
    else:
        chdir_to_repo(repo_path)
        cmd = "git status"
        run_command(cmd)
