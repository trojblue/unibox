import click

@click.group()
def cli():
    pass

@click.group()
def setup():
    pass

@setup.command()
def awscli():
    # install_awscli()
    print('Setting up awscli')

@cli.command()
@click.argument('dir_name')
def resize(dir_name):
    # resize implementation
    print(f'Resizing directory: {dir_name}')

cli.add_command(setup)

if __name__ == '__main__':
    cli()
