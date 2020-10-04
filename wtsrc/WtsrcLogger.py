import click
from termcolor import colored

verbose = False

indents = []

def fatal(message):
    click.echo(click.style("Fatal Error: " + message, bg='red'))
    exit()


def warning(message):
    click.echo(click.style("Warning: " + message, bg='yellow', fg='red'))


def print(message, color='reset', nl=True, indent=True):
    if indent:
        message = "".join(indents) + message
    click.echo(click.style(message, bg='reset', fg=color), nl=nl)


def perhaps_print(message, color='reset', nl=True):
    if verbose:
        print(message, color=color, nl=nl)


def success():
    if verbose:
        click.echo(click.style("WTSRC OK", bg='reset', fg='green'))


def increase_indent(indent="    "):
    indents.append(indent)


def decrease_indent():
    if len(indents) > 0:
        indents.pop()
    else:
        warning("decrease_indent called but no indent is active")
