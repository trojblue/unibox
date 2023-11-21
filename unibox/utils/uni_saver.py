import json
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union

from .uni_logger import UniLogger


class UniSaver:
    """A simple utility class for saving various data types to appropriate file formats.
    """

    def __init__(self, logger=None, debug_print=True):
        if not logger:
            self.logger = UniLogger(file_suffix="UniSaver")
        else:
            self.logger = logger

        self.debug_print = debug_print

    def saves(self, data, file_path: Union[Path, str]):
        """Save data to the given file path.

        The type of file saved depends on the data type.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        data_type = type(data).__name__

        # Determine the expected file extension
        extension_mapping = {
            'dict': '.json',
            'list': self._list_extension(data),
            'DataFrame': '.parquet',
            'Image': '.png',
            'str': '.txt',  # Added case for strings
        }

        if data_type not in extension_mapping:
            self.logger.error(f'Unsupported data type "{data_type}"')
            return

        expected_extension = extension_mapping[data_type]

        # Verify or append the correct extension
        if file_path.suffix.lower() != expected_extension:
            if file_path.suffix:
                self.logger.error(
                    f'Invalid file extension for {data_type}. Expected "{expected_extension}" but got "{file_path.suffix}"')
                self.logger.warning("file extension will be appended to the file name")

            file_path = Path(
                str(file_path) + expected_extension)  # something.txt -> something.txt.json, so no overwrite
            self.logger.warning(f"file without extension, saving to actual path: {file_path}")

        self.handle_save(data, data_type, file_path, expected_extension)

    def _save_data(self, data, data_type, file_path, expected_extension=None):
        if data_type == 'dict':
            self._save_json(data, file_path)
        elif data_type == 'list':
            self._save_list(data, file_path, expected_extension)
        elif data_type == 'set':
            self._save_list(list(data), file_path, expected_extension)
        elif data_type == 'DataFrame':
            self._save_parquet(data, file_path)
        elif data_type == 'Image':
            self._save_image(data, file_path)
        elif data_type == 'str':  # New case for saving strings
            self._save_txt([data], file_path)  # Wrapping data in a list

        if self.debug_print:
            self.logger.info(f'{data_type} saved successfully to "{file_path}"')

    def handle_save(self, data, data_type, file_path, expected_exteison=None):
        try:
            self._save_data(data, data_type, file_path, expected_exteison)
        except PermissionError:
            alternative_file_path = file_path.replace('.parquet', '_alternative.parquet')
            self.logger.warning(
                f'Permission denied for "{file_path}". Trying to saves to "{alternative_file_path}" instead.')
            self._save_data(data, data_type, alternative_file_path, expected_exteison)
        except Exception as e:
            self.logger.error(f'{data_type} saves ERROR at "{file_path}": {e}')

    def _list_extension(self, data: list):
        if all(isinstance(item, dict) for item in data):
            return '.jsonl'
        elif all(isinstance(item, str) for item in data):
            return '.txt'
        else:
            raise TypeError("List content must be either all dictionaries or all strings.")

    def _save_json(self, data: dict, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_list(self, data: list, file_path: Path, extension: str):
        if extension == '.jsonl':
            self._save_jsonl(data, file_path)
        elif extension == '.txt':
            self._save_txt(data, file_path)
        else:
            raise ValueError("Invalid extension for list data.")

    def _save_jsonl(self, data: list, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

    def _save_txt(self, data: list, file_path: Path):
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(f'{item}\n')

    def _save_parquet(self, data: pd.DataFrame, file_path: Path):
        data.to_parquet(file_path, index=False)

    def _save_image(self, data: Image.Image, file_path: Path):
        data.save(file_path)


if __name__ == "__main__":
    # Usage example
    logger = UniLogger("logs", file_suffix="saver")
    saver = UniSaver(logger)
    json_data = {'key': 'value'}
    saver.saves(json_data, "example")  # Automatically adds .json
    jsonl_data = [{'key1': 'value1'}, {'key2': 'value2'}]
    saver.saves(jsonl_data, "example.jsonl")
    txt_data = ['line1', 'line2']
    saver.saves(txt_data, "example.txt")
    image_data = Image.new('RGB', (60, 30), color='red')
    saver.saves(image_data, "example.png")
    df_data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    saver.saves(df_data, "example.parquet")
