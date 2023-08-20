import os
def to_relaive_unix_path(absolute_path:str, root_dir:str, convert_slash=True):
    relative_path = os.path.relpath(absolute_path, root_dir)
    if convert_slash:
        relative_path = relative_path.replace("\\", "/")
    return relative_path