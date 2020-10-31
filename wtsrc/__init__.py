import click
import os
import pexpect
import subprocess
import sys
import wtsrc.WtsrcLogger as log
from termcolor import colored
from wtsrc.version import __version__
from wtsrc.ManifestModel import ManifestModel
from wtsrc.TsrcConfigModel import TsrcConfigModel
from wtsrc.WtsrcGlobalModel import WtsrcGlobalModel
from wtsrc.WtsrcProjectModel import WtsrcProjectModel
from wtsrc.WtsrcUtils import chdir_to_manifest_dir, chdir_to_repo, chdir_to_proj_root, nuke_root, obj_dump


# some commands cannot have a pre/post action
# for instance the init cannot have a pre action because the manifest isn't cloned yet
# and the alias related commands cannot have any actions because they be called from anywhere (the model might not exist)
pre_action_not_allowed = ['add-alias','init', 'ls-manifest', 'nuke', 'remove-alias', 'show']
post_action_not_allowed = ['add-alias', 'ls-manifest', 'nuke', 'remove-alias', 'show']


def choose_alias_or_url(alias, url):
    """use for commands that can choose an alias or url option"""
    if alias and url:
        log.fatal("You cannot pass both an alias and a url, choose one option or the other")
    elif alias:
        model = WtsrcGlobalModel.load()
        manifest_url = model.get_alias_url(alias)
        if(manifest_url == None):
            log.fatal("The alias '{}' is not known".format(alias))
    else:
        manifest_url = url
    
    return manifest_url


def run_commands(commands, preview=False, as_sub_process=False):

    for command in commands:
        if preview:
            log.print("This action will run the following commands:", color="green")
            log.print(command)
        else:
            run_command(command, as_sub_process=as_sub_process)


def run_command(command, as_sub_process=False):
    '''Executes a command on the command line and shows the results and returns the exit code'''

    log.print("Running Command: ", nl=False)
    log.print(command, 'green')

    if sys.platform.lower().startswith('win') or as_sub_process:
        p = subprocess.Popen(command.split(' '), env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            print(p.stdout.readline().decode("utf-8"), end="")
            if(p.poll() is not None):
                break
        return p.returncode
    else:
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
@click.option('--alias', '-a', type=str, default=None, required=False, help="the name of the alias to the manifest repo url")
@click.option('--url', '-u', type=str, default=None, required=False, help="the url of the tsrc manifest repo")
@click.option('--branch', '-b', type=str, default=None, help="which branch to clone (without is master)")
@click.option('--group', '-g', type=str, default=None, help="which group to clone (without is all repos)")
@click.option('--shallow', '-s', type=bool, default=False, is_flag=True, help="set this flag if you want a shallow copy")
def init(alias:str, url:str, branch:str, group:str, shallow:bool):
    '''Clone the manifest and all repos'''

    manifest_url = choose_alias_or_url(alias, url)
    cmd = "tsrc init {r}{b}{u}{s}".format(r=manifest_url,
                                          b=" --branch {}".format(branch) if branch else "",
                                          u=" --group {}".format(group) if group else "",
                                          s=" -s" if shallow else "")
    run_command(cmd)


@run.command()
@click.option('--alias', '-a', type=str, help="A convenient alias to give to the manifest repo url")
@click.option('--url', '-u', type=str, help="The url to the manifest repo")
def add_alias(alias:str, url:str):
    '''Will try to add an alias and save the model'''

    if(alias is None or alias.isidentifier() == False):
        log.fatal("'{}' is not a valid alias".format(alias))

    model = WtsrcGlobalModel.load()
    model.add_alias(alias, url)
    model.save()
    log.print("Added alias: {a} => {u}".format(a=alias, u=url), color='green')


@run.command()
@click.option('--alias', '-a', type=str, help="The name of the alias you want to delete")
def remove_alias(alias: str):
    '''Will try to remove an alias and save the model'''
    model = WtsrcGlobalModel.load()
    model.remove_alias(alias)
    model.save()


@run.command()
def sync():
    '''Pulls all repos - wraps tsrc sync'''
    cmd = "tsrc sync"
    run_command(cmd)


@run.command()
@click.option('--repo', '-r', type=str, default=None, required=False)
def status(repo:str):
    '''Shows the status of a repo at the specified path or "all"'''
    if repo == None or repo == 'all':
        chdir_to_manifest_dir()
        log.print("Status of manifest", color='green')
        cmd = 'git status'
        run_command(cmd)
        if repo == None:
            cmd = 'tsrc status'
        else:
            cmd = 'tsrc foreach git status'
        run_command(cmd)
    else:
        log.print("Changing to repo {0}".format(repo))
        chdir_to_repo(repo, overide_manifest=True)
        cmd = "git status"
        run_command(cmd)


@run.command()
def show():
    '''Shows the model'''
    gmodel = WtsrcGlobalModel.load()
    log.print("Global Model:", color="green")
    log.print(str(gmodel))

    pmodel = WtsrcProjectModel.load()
    log.print("Project Model:", color="green")
    pmodel.log()


@run.command()
@click.option('--command', '-c', type=str, help="The text of the command to run including options")
def foreach(command:str):
    '''wraps tsrc foreach, runs the "command text" for all repos'''
    cmd = "tsrc foreach -c '{c}'".format(c=command)
    run_command(cmd)


@run.command()
@click.option('--repo', '-r', type=str, help="The repo path")
@click.option('--command', '-c', type=str, help="The text of the command to run including options")
def forsingle(repo:str, command:str):
    '''Will run "command text" for the specified repo'''
    log.print("Changing to repo {0}".format(repo))
    chdir_to_repo(repo, overide_manifest=True)
    run_command(command)


@run.command()
@click.argument("action", type=str)
def run_action(action):
    '''Tries to run an action defined in wtsrc.yml'''
    model = WtsrcProjectModel.load()

    action_name = action
    action = model.get_action_action(action_name)
    if not action:
        log.fatal("The action '{}' was not found".format(action_name))

    perhaps_run_action(action, "Action: ")


@run.command()
@click.option('--alias', '-a', type=str, default=None, required=False, help="the name of the alias to the manifest repo url")
@click.option('--url', '-u', type=str, default=None, required=False, help="the url of the tsrc manifest repo")
def ls_manifest(alias, url):
    '''Lists all branches for the manifest repo'''
    manifest_url = choose_alias_or_url(alias, url)
    cmd = "git ls-remote {}".format(manifest_url)
    run_command(cmd)


@run.command()
@click.option('--repo', '-r', type=str, default=None, required=True, help="The path of the repo relative to the project root")
def ls_repo(repo):
    '''Shows all the available branches for a repo's remote'''
    log.print("Changing to repo {0}".format(repo))
    chdir_to_repo(repo, overide_manifest=True)
    run_command("git branch -a")


@run.command()
@click.option('--repo', '-r', type=str, default=None, required=True, help="the path of the repo relative to the project root")
@click.option('--branch', '-b', type=str, default=None, required=True, help="the name of the branch to checkout")
def checkout_for(repo, branch):
    '''Checks out an existing branch for a repo'''
    chdir_to_repo(repo, overide_manifest=True)
    run_command("git checkout {0}".format(branch))


@run.command()
@click.option('--repos', '-r', type=str, default=None, multiple=True, required=True, help="The set of repos to create the repo for")
@click.option('--branch', '-b', type=str, default=None, required=True, help="the name branch for the configuration")
def create_config(repos, branch):
    '''Creates a new configuration with the given name'''

    manifest = ManifestModel.load()
    config = TsrcConfigModel.load()

    # check that the repo is in the model
    for repo in repos:
        found = manifest.has_repo(repo)
        if not found:
            log.fatal("Could not find repo {r}".format(r=repo))
        chdir_to_repo(repo) # this will also error if the repo directory doesn't exist

    for repo in repos:
        log.print("Changing to repo directory: {r}".format(r=repo))
        chdir_to_repo(repo)
        run_command("git checkout -b {0}".format(branch))
        run_command("git push --set-upstream origin {0}".format(branch))
        manifest.update_branch(repo, branch)
        log.print("")

    log.print("")
    log.print("Changing to manifest directory")
    chdir_to_manifest_dir()
    run_command("git checkout -b {0}".format(branch))
    log.print("Saving updated tsrc manifest")
    manifest.save()
    run_command('git add manifest.yml')
    run_command('git commit -m "creating configuration {0}"'.format(branch))
    run_command("git push --set-upstream origin {0}".format(branch))

    log.print("")
    log.print("Saving updated tsrc configuration file")
    config.change_branch(branch)
    config.save()

"""
@run.command()
def destroy_config():
    '''Destroys the current configuration in the config.yml file'''

    manifest = ManifestModel.load()
    config = TsrcConfigModel.load()

    manifest_branch = config.get_manifest_branch()
    if not manifest_branch:
        log.fatal("The configuration name could not be determined from the config.yml file")

    log.warning("This command is usually run only by integrators after approving pull requests")
    log.warning("This command will delete branches in the cloud!!!")
    log.print("The configuration is: {0}".format(manifest_branch), color='cyan')
    if( click.confirm("Do you want to continue?") ):
        pass
    else:
        log.warning("You've canceled")
"""

@run.command()
def nuke():
    """Deletes everything, including the .tsrc director"""
    if click.confirm('This will attempt to delete all files in\n{0}\n...\nAre you sure you want to continue?'.format(os.getcwd())):
        nuke_root()
        log.print("Nuked", color="green")
    else:
        log.warning("You've canceled")


@run.command()
def version():
    '''prints both tsrc's and wtsrc's version'''
    run_command("tsrc version")
    log.print("wtsrc version: {}".format(__version__))
