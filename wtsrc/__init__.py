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


def do_init(manifest_url:str, branch:str, group:str, s):
    cmd = "tsrc init {r}{b}{u}{s}".format(r=manifest_url,
                                          b=" --branch {}".format(branch) if branch else "",
                                          u=" --group {}".format(group) if group else "",
                                          s=" -s" if s else "")
    run_command(cmd)


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
    WtsrcProjectModel.register_pre_action_not_possible_cmd('init-alias')

    if WtsrcProjectModel.pre_action_allowed_for_cmd(ctx.invoked_subcommand):
        model = WtsrcProjectModel.load()
        pre_action = model.get_command_pre_action(ctx.invoked_subcommand)
        perhaps_run_action(pre_action, 'Running pre-action:')
    else:
        log.print("Info: pre-actions are enabled because the manifest repo hasn't been cloned yet")


@run.resultcallback()
@click.pass_context
def post_command(ctx, result, **kwargs):
    model = WtsrcProjectModel.load()

    post_action = model.get_command_post_action(ctx.invoked_subcommand)
    perhaps_run_action(post_action, 'Running post-action:')
    log.success()


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
    model = WtsrcGlobalModel.load()
    url = model.get_alias_url(alias)

    if(url == None):
        log.fatal("The alias '{}' is not known".format(alias))

    do_init(url, branch, group, s)


@run.command()
@click.argument('alias', type=str)
@click.argument('url', type=str)
def add_alias(alias:str, url:str):
    '''Will try to add an alias and save the model'''

    if(alias is None or alias.isidentifier() == False):
        log.fatal("'{}' is not a valid alias".format(alias))

    if(url is None):
        log.fatal("You must specify the url with --url")

    model = WtsrcGlobalModel.load()
    model.add_alias(alias, url)
    model.save()


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
