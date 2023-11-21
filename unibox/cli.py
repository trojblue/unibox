import os
import click

import unibox
from .processing import image_resizer
from .processing import file_mover


@click.group()
def cli():
    pass


@cli.command()
@click.argument('src_dir')
@click.option('--min_side', '-m', default=None, type=int, help='Minimum side length of the image.')
@click.option('--dst_dir', '-d', default=None, help='Destination directory for the images.')
@click.option('--format', '-f', default=None, help='Format of the image.')
@click.option('--quality', '-q', default=None, type=int, help='Quality of the image.')
@click.option('--exist_ok', '-e', default=None, type=bool, help='Keep existing images')
def resize_legacy(src_dir, min_side, dst_dir, format, quality, exist_ok):
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


from unibox import UniResizer


@cli.command()
@click.option("--img_root_dir", "-d", default=None, type=str, help="Root directory of the images.")
@click.option("--to_dir", "-t", default=None, type=str, help="Target directory for the images.")
@click.option("--min_side", "-m", default=None, type=int, help="Minimum side length of the image.")
@click.option("--max_side", "-M", default=None, type=int, help="Maximum side length of the image.")
@click.option("--target_pixels", "-p", default=None, type=int,
              help="Target number of pixels of the image.")
@click.option("--keep_hierarchy", "-k", default=True, type=bool, help="Keep directory hierarchy.")
@click.option("--exist_ok", "-e", default=True, type=bool, help="Keep existing images.")
def resize(img_root_dir, to_dir, min_side, max_side, target_pixels, keep_hierarchy, exist_ok):
    if not img_root_dir:
        img_root_dir = click.prompt('- Image root directory', type=str)

    if not target_pixels:
        target_pixels = click.prompt('- Target number of pixels (-1 to unset)', type=int,
                                     default=int(1024 * 1024 * 1.25))
        if target_pixels == -1:
            target_pixels = None

    dir_str = ""
    if min_side:
        dir_str += f"_min{min_side}"
    if max_side:
        dir_str += f"_max{max_side}"
    if target_pixels:
        dir_str += f"_target{target_pixels}"

    if not to_dir:
        src_dir_name = os.path.basename(os.path.abspath(img_root_dir))
        to_dir = click.prompt('- Destination', default=f"{src_dir_name}_resized{dir_str}_webp")

    if not keep_hierarchy:
        keep_hierarchy = click.prompt('- Keep directory hierarchy', type=bool, default=True)

    if not exist_ok:
        exist_ok = click.prompt('- Keep existing images', type=bool, default=True)

    resizer = UniResizer(img_root_dir, to_dir,
                         min_dim=min_side, max_dim=max_side, target_pixels=target_pixels,
                         keep_hierarchy=keep_hierarchy, exist_ok=exist_ok)

    resizer.execute_resize_jobs(resizer.get_resize_jobs())


def extensions_option(value: str):
    if value:
        extensions = value.strip().split()
        return [f".{ext.strip()}" if not ext.startswith('.') else ext.strip() for ext in extensions]
    return None


@cli.command()
@click.argument('src_dir')
@click.argument('dst_dir')
@click.option('--keep_structure', '-k', is_flag=True, help='Keep directory structure.')
@click.option('--include', '-i', default=None, type=extensions_option,
              help='File extensions to include (e.g., ".txt .jpg .webp").')
@click.option('--exclude', '-e', default=None, type=extensions_option,
              help='File extensions to exclude (e.g., ".txt .jpg .webp").')
def move(src_dir, dst_dir, keep_structure, include, exclude):
    mover = file_mover.DirMoverCopier(src_dir, dst_dir, keep_structure, include, exclude, 'move')
    mover.process_files()
    print(f'Moved files from {src_dir} to {dst_dir}')


@cli.command()
@click.argument('src_dir')
@click.argument('dst_dir')
@click.option('--keep_structure', '-k', is_flag=True, help='Keep directory structure.')
@click.option('--include', '-i', default=None, type=extensions_option,
              help='File extensions to include (e.g., ".txt .jpg .webp").')
@click.option('--exclude', '-e', default=None, type=extensions_option,
              help='File extensions to exclude (e.g., ".txt .jpg .webp").')
def copy(src_dir, dst_dir, keep_structure, include, exclude):
    copier = file_mover.DirMoverCopier(src_dir, dst_dir, keep_structure, include, exclude, 'copy')
    copier.process_files()
    print(f'Copied files from {src_dir} to {dst_dir}')


if __name__ == '__main__':
    cli()
