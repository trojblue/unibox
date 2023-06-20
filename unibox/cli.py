import click
from .setup import setup_swap, setup_linux, setup_awscli


@click.group()
def cli():
    pass

@click.group()
def setup():
    pass

@setup.command()
@click.argument('size', type=str, default='2G', required=False)
def swap(size):
    # setup_swap(size)
    print(f'Setting up swap with size: {size}')
    setup_swap(size)

@setup.command()
def awscli():
    # install_awscli()
    print('Setting up awscli')

@setup.command()
def linux():
    setup_linux()


@cli.command()
@click.argument('dir_name')
def resize(dir_name):
    # resize implementation
    print(f'Resizing directory: {dir_name}')

cli.add_command(setup)

if __name__ == '__main__':
    cli()
