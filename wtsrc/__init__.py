import click
import os
import pexpect
import subprocess
import wtsrc.WtsrcLogger as log
from termcolor import colored
from wtsrc.version import __version__
from wtsrc.WtsrcGlobalModel import WtsrcGlobalModel
from wtsrc.WtsrcProjectModel import WtsrcProjectModel
from wtsrc.WtsrcUtils import chdir_to_manifest_dir, chdir_to_repo, find_tsrc_root, obj_dump


# some commands cannot have a pre/post action
# for instance the init cannot have a pre action because the manifest isn't cloned yet
# and the alias related commands cannot have any actions because they be called from anywhere (the model might not exist)
pre_action_not_allowed = ['init', 'add-alias', 'remove-alias']
post_action_not_allowed = ['add-alias', 'remove-alias']


def run_command(command):
    '''Executes a command on the command line and shows the results and returns the exit code'''

    log.print("Running Command: ", nl=False)
    log.print(command, 'green')

    process = pexpect.spawn(command)
    process.interact()
    process.close()
    return process.exitstatus


def perhaps_run_action(action, heading):
    '''Manages running an action and exiting if the process fails'''

    restore_cwd = os.getcwd()
    chdir_to_manifest_dir()
    if action:
        log.print("{h} {a}".format(h=heading, a=action))
        result = run_command(action)
        if result != 0:
            log.fatal("{a} exited unsuccessfully ({e})".format(a=action, e=result))
    os.chdir(restore_cwd)


@click.group()
@click.option('-v', default=False, is_flag=True, help="if you want everything printed")
@click.pass_context
def run(ctx, v):
    '''Entry point - not real command - executes before all commands'''

    if(ctx.invoked_subcommand in pre_action_not_allowed):
        return

    for cmd_name in ctx.command.commands:
        WtsrcProjectModel.register_known_command(cmd_name)
    
    for cmd in pre_action_not_allowed:
        WtsrcProjectModel.register_pre_action_not_possible_cmd(cmd)
    
    for cmd in post_action_not_allowed:
        WtsrcProjectModel.register_post_action_not_possible_cmd(cmd)

    model = WtsrcProjectModel.load()
    pre_action = model.get_command_pre_action(ctx.invoked_subcommand)
    perhaps_run_action(pre_action, 'Running pre-action:')


@run.resultcallback()
@click.pass_context
def post_command(ctx, result, **kwargs):
    '''Called after each command to run the post action'''

    if(ctx.invoked_subcommand in post_action_not_allowed):
        return

    model = WtsrcProjectModel.load()
    post_action = model.get_command_post_action(ctx.invoked_subcommand)
    perhaps_run_action(post_action, 'Running post-action:')
    log.success()


@run.command()
@click.option('--alias', type=str, default=None, required=False, help="the name of the alias to the manifest repo url")
@click.option('--url', type=str, default=None, required=False, help="the url of the tsrc manifest repo")
@click.option('--branch', type=str, default=None, help="which branch to clone (without is master)")
@click.option('--group', type=str, default=None, help="which group to clone (without is all repos)")
@click.option('-s', default=False, is_flag=True, help="set this flag if you want a shallow copy")
def init(alias:str, url:str, branch:str, group:str, s):
    '''Clone the manifest and all repos'''

    manifest_url = None
    if alias and url:
        log.fatal("You cannot pass both an alias and a url, choose one option or the other")
    elif alias:
        model = WtsrcGlobalModel.load()
        manifest_url = model.get_alias_url(alias)
        if(manifest_url == None):
            log.fatal("The alias '{}' is not known".format(alias))
    else:
        manifest_url = url

    cmd = "tsrc init {r}{b}{u}{s}".format(r=manifest_url,
                                          b=" --branch {}".format(branch) if branch else "",
                                          u=" --group {}".format(group) if group else "",
                                          s=" -s" if s else "")
    run_command(cmd)


@run.command()
@click.argument('alias', type=str)
@click.argument('url', type=str)
def add_alias(alias:str, url:str):
    '''Will try to add an alias and save the model'''

    if(alias is None or alias.isidentifier() == False):
        log.fatal("'{}' is not a valid alias".format(alias))

    model = WtsrcGlobalModel.load()
    model.add_alias(alias, url)
    model.save()


@run.command()
@click.argument('alias', type=str)
def remove_alias(alias: str):
    '''Will try to remove an alias and save the model'''
    model = WtsrcGlobalModel.load()
    model.remove_alias(alias)
    model.save()


@run.command()
def diff():
    '''Shows which files have been modified'''
    cmd = "tsrc foreach git diff-index HEAD"
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
@click.argument('branch', type=str)
def merge(repo_path, branch):
    '''Merges a branch into a repo'''
    chdir_to_repo(repo_path, overide_manifest=True)
    cmd = "git merge {}".format(branch)
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
def mergetool(repo_path):
    '''Shows the merge tool for a repo'''
    chdir_to_repo(repo_path, overide_manifest=True)
    cmd = "git mergetool"
    run_command(cmd)


@run.command()
@click.argument("action", type=str)
def run_action(action):
    '''Tries to run an action defined in project yml file'''
    model = WtsrcProjectModel.load()

    action_name = action
    action = model.get_action_action(action_name)
    if not action:
        log.fatal("The action '{}' was not found".format(action_name))

    perhaps_run_action(action, "Action: ")


@run.command()
@click.option('-c', type=str, help="The text of the command to run including options")
def foreach(c:str):
    """wraps tsrc foreach - runs -c 'CMD_TEXT' for each repo"""
    cmd = "tsrc foreach -c '{c}'".format(c=c)
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str)
@click.option('-c', type=str)
@click.option('-sp', default=False, is_flag=True, help="Flag if the command is tig or vim or similar, runs as sub-process")
def forsingle(repo_path:str, c:str, sp):
    """Will run -c 'CMD_TEXT' for the specified repo"""
    chdir_to_repo(repo_path, overide_manifest=True)
    if not sp:
        run_command(c)
    else:
        subprocess.run(c.split(" "))


@run.command()
def show():
    '''Prints the saved model'''
    gmodel = WtsrcGlobalModel.load()
    log.print(str(gmodel))

    pmodel = WtsrcProjectModel.load()
    pmodel.log()


@run.command()
@click.argument('repo-path', type=str, default=None, required=False)
def status(repo_path:str):
    """Shows the status of a repo at the specified path or 'all'"""
    if repo_path == None:
        cmd = 'tsrc status'
        run_command(cmd)
    elif repo_path == 'all':
        chdir_to_manifest_dir()
        log.print("Status of manifest", color='green')
        cmd = 'git status'
        run_command(cmd)
        cmd = 'tsrc foreach git status'
        run_command(cmd)
    else:
        chdir_to_repo(repo_path, overide_manifest=True)
        cmd = "git status"
        run_command(cmd)


@run.command()
@click.argument('repo-path', type=str, default=None)
def tig(repo_path:str):
    '''Runs tig for the specified repo'''
    chdir_to_repo(repo_path, overide_manifest=True)
    # don't use run_command - tig doesn't dismount cleanly
    subprocess.run(["tig"])


@run.command()
def clean():
    '''deletes all local files that are not under version control'''
    cmd = "tsrc foreach -- git clean -df"
    run_command(cmd)


@run.command()
@click.argument('repo-path', type=str, default=None)
def reset(repo_path:str):
    """Discards/resets all uncommitted changes  - 'all'"""
    cmd = "tsrc foreach -- git reset --hard HEAD"
    run_command(cmd)


@run.command()
def version():
    '''prints both tsrc's and wtsrc's version'''
    run_command("tsrc version")
    log.print("wtsrc version: {}".format(__version__))
