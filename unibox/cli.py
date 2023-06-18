import click
from .setup import setup_swap, install_awscli

@click.group()
def cli():
    pass

@cli.command()
@click.argument('size')
def swap(size):
    setup_swap(size)

@cli.command()
def awscli():
    install_awscli()

if __name__ == '__main__':
    cli()
