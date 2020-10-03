import click
import shlex
import subprocess
from wtsrc.WtsrcModel import WtsrcModel


@click.group()
def run():
    pass



def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True)
    while process.poll() is None:
        line = process.stdout.readline()    # This blocks until it receives a newline.
        if(isinstance(line, bytes)):
            print(line.decode())
        else:
            print(line)

'''
def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc
'''

@run.command()
@click.argument('alias', type=str)
@click.option('--branch', type=str, default=None, help="which branch to clone")
@click.option('--group', type=str, default=None, help="which group to clone")
def init(alias:str, branch:str, group:str):

    model = WtsrcModel.load()
    url = model.get_alias_url(alias)

    if(url == None):
        print("The alias '{}' is not known".format(alias))
    else:
        cmd = "tsrc init {r}{b}{u}".format(r=url,
                                           b=" --branch {}".format(branch) if branch else "",
                                           u=" --group {}".format(group) if group else "")
        run_command(cmd)


@run.command()
@click.argument('alias', type=str)
@click.option('--url', type=str, help="the url for the repository")
#@click.option('-e', '--evaluate', type=click.STRING, help='Execute specified commands string and exit')
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
def show():
    '''Prints the saved model'''
    model = WtsrcModel.load()
    print(str(model))
