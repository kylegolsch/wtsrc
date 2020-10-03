import click
import os
import pexpect
from wtsrc.WtsrcModel import WtsrcModel
from wtsrc.WtsrcUtils import find_tsrc_root

output_bytes = []

def read(fd):
    data = os.read(fd, 1024)
    output_bytes.append(data)
    return data


@click.group()
def run():
    pass


def run_command(command):
    '''Executes a command on the command line and shows the results'''
    child = pexpect.spawn(command)
    child.interact()


@run.command()
@click.argument('alias', type=str)
@click.option('--branch', type=str, default=None, help="which branch to clone")
@click.option('--group', type=str, default=None, help="which group to clone")
@click.option('-s', default=False, is_flag=True, help="set this flag if you want a shallow copy")
def init(alias:str, branch:str, group:str, s):

    model = WtsrcModel.load()
    url = model.get_alias_url(alias)

    if(url == None):
        print("The alias '{}' is not known".format(alias))
    else:
        cmd = "tsrc init {r}{b}{u}{s}".format(r=url,
                                           b=" --branch {}".format(branch) if branch else "",
                                           u=" --group {}".format(group) if group else "",
                                           s=" -s" if s else "")
        run_command(cmd)


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
def show():
    '''Prints the saved model'''
    model = WtsrcModel.load()
    print(str(model))


@run.command()
def summary():
    cmd = 'tsrc status'
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
def status(repo_path):
    root = find_tsrc_root()
    if not root:
        print("You must call from within a tsrc directory")
    else:
        if repo_path == 'all':
            cmd = 'tsrc foreach git status'
            run_command(cmd)
        else:
            os.chdir(os.path.join(root, repo_path))
            cmd = "git status"
            run_command(cmd)
