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
@click.argument('src_dir')
@click.option('--min_side', '-m', default=None, type=int, help='Minimum side length of the image.')
@click.option('--dst_dir', '-d', default=None, help='Destination directory for the images.')
@click.option('--format', '-f', default=None, help='Format of the image.')
@click.option('--quality', '-q', default=None, type=int, help='Quality of the image.')
def resize(src_dir, min_side, dst_dir, format, quality):
    # resize implementation
    print(f'Resizing directory: {src_dir}')

    if not min_side:
        min_side = click.prompt('- Minimum side length', type=int, default=768)
    if not format:
        format = click.prompt('- File format', default="webp")
    if not dst_dir:
        dst_dir = click.prompt('- Destination', default=f"{src_dir}_{min_side}_{format}")
    if not quality:
        quality = click.prompt('- Image quality', type=int, default=95)

    resizer = image_resizer.ImageResizer(src_dir, dst_dir, min_side, format=format, quality=quality)
    resizer.resize_images()

cli.add_command(setup)

if __name__ == '__main__':
    cli()
