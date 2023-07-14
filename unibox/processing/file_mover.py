import os
import shutil
from tqdm.auto import tqdm


class DirMoverCopier:
    def __init__(self, src_dir, dst_dir, keep_structure, include, exclude, action):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.keep_structure = keep_structure
        self.include = include
        self.exclude = exclude
        self.action = action

        self._print_debug_string()

    def _print_debug_string(self):
        debug_string = f"Processing with action={self.action}: " \
                       f"src_dir={self.src_dir}, dst_dir={self.dst_dir}, " \
                       f"keep_structure={self.keep_structure}, include={self.include}, exclude={self.exclude}"
        print(debug_string)

    def should_include_file(self, file_name):
        extension = os.path.splitext(file_name)[1]
        if self.include and extension not in self.include:
            return False
        if self.exclude and extension in self.exclude:
            return False
        return True

    def process_files(self):
        processed_files = 0
        for dir_path, _, filenames in os.walk(self.src_dir):
            for filename in tqdm(filenames, desc="Processing files"):
                if self.should_include_file(filename):
                    src_file_path = os.path.join(dir_path, filename)
                    if self.keep_structure:
                        relative_path = os.path.relpath(dir_path, self.src_dir)
                        dst_file_dir = os.path.join(self.dst_dir, relative_path)
                    else:
                        dst_file_dir = self.dst_dir
                    os.makedirs(dst_file_dir, exist_ok=True)
                    dst_file_path = os.path.join(dst_file_dir, filename)
                    if self.action == 'move':
                        shutil.move(src_file_path, dst_file_path)
                        processed_files += 1
                    elif self.action == 'copy':
                        shutil.copy2(src_file_path, dst_file_path)
                        processed_files += 1

        print(f"Processed {processed_files} files")

