import click

from .processing import image_resizer

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
def resize(src_dir):
    # resize implementation
    print(f'Resizing directory: {src_dir}')
    min_side = 768
    dst_dir = f"{src_dir}_{min_side}webp"
    resizer = image_resizer.ImageResizer(src_dir, dst_dir, min_side, format="webp", quality=95)
    resizer.resize_images()

cli.add_command(setup)

if __name__ == '__main__':
    cli()
