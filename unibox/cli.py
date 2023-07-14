import os
import click

from .processing import image_resizer
from .processing import file_mover


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
@click.option('--exist_ok', '-e', default=None, type=bool, help='Keep existing images')
def resize(src_dir, min_side, dst_dir, format, quality, exist_ok):

    # resize implementation
    print(f'Resizing directory: {src_dir}')

    if not min_side:
        min_side = click.prompt('- Minimum side length', type=int, default=768)
    if not format:
        format = click.prompt('- File format', default="webp")
    if not dst_dir:
        src_dir_name = os.path.basename(os.path.abspath(src_dir))
        dst_dir = click.prompt('- Destination', default=f"{src_dir_name}_{min_side}_{format}")
    if not quality:
        quality = click.prompt('- Image quality', type=int, default=95)
    if not exist_ok:
        exist_ok = click.prompt('- Keep existing images', type=bool, default=True)

    # Printing the command
    print("\nRunning Command:\n")
    print(f"unibox resize {src_dir} --min_side {min_side} --dst_dir {dst_dir} "
          f"--format {format} --quality {quality} --exist_ok {exist_ok}\n")

    resizer = image_resizer.ImageResizer(src_dir, dst_dir, min_side, format=format, quality=quality, exist_ok=exist_ok)
    resizer.resize_images()



@cli.command()
@click.argument('src_dir')
@click.argument('dst_dir')
@click.option('--keep_structure', '-k', default=False, type=bool, help='Keep directory structure.')
@click.option('--include', '-i', default=None, multiple=True, help='File extensions to include.')
@click.option('--exclude', '-e', default=None, multiple=True, help='File extensions to exclude.')
def move(src_dir, dst_dir, keep_structure, include, exclude):
    mover = file_mover.DirMoverCopier(src_dir, dst_dir, keep_structure, include, exclude, 'move')
    mover.process_files()
    print(f'Moved files from {src_dir} to {dst_dir}')

@cli.command()
@click.argument('src_dir')
@click.argument('dst_dir')
@click.option('--keep_structure', '-k', default=False, type=bool, help='Keep directory structure.')
@click.option('--include', '-i', default=None, multiple=True, help='File extensions to include.')
@click.option('--exclude', '-e', default=None, multiple=True, help='File extensions to exclude.')
def copy(src_dir, dst_dir, keep_structure, include, exclude):
    copier = file_mover.DirMoverCopier(src_dir, dst_dir, keep_structure, include, exclude, 'copy')
    copier.process_files()
    print(f'Copied files from {src_dir} to {dst_dir}')


cli.add_command(setup)

if __name__ == '__main__':
    cli()
