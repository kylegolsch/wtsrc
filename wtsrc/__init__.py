import click
import os
import pexpect
import wtsrc.WtsrcLogger as log
from termcolor import colored
from wtsrc.WtsrcGlobalModel import WtsrcGlobalModel
from wtsrc.WtsrcProjectModel import WtsrcProjectModel
from wtsrc.WtsrcUtils import chdir_to_manifest_dir, chdir_to_repo, find_tsrc_root, obj_dump


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
    log.verbose = v

    # tell model about the valid commands for validation
    for cmd_name in ctx.command.commands:
        WtsrcProjectModel.register_known_command(cmd_name)

    # tell the model which commands can't have pre-actions because the manifest isn't cloned before the command
    WtsrcProjectModel.register_pre_action_not_possible_cmd('init')

    if WtsrcProjectModel.pre_action_allowed_for_cmd(ctx.invoked_subcommand):
        model = WtsrcProjectModel.load()
        pre_action = model.get_command_pre_action(ctx.invoked_subcommand)
        perhaps_run_action(pre_action, 'Running pre-action:')
    else:
        log.print("Info: pre-actions are disabled because the manifest repo hasn't been cloned yet")


@run.resultcallback()
@click.pass_context
def post_command(ctx, result, **kwargs):
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


@run.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('command', type=str)
@click.argument('args', type=str, required=False, nargs=-1)
def manifest(command, args):
    if(command=="git"):
        chdir_to_manifest_dir()
        cmd = "git " + " ".join(args)
        run_command(cmd)
    else:
        log.fatal("Unknown sub command '{}'".format(command))


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
        cmd = 'tsrc foreach git status'
        run_command(cmd)
    else:
        chdir_to_repo(repo_path)
        cmd = "git status"
        run_command(cmd)
