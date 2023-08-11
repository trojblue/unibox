import json
import pandas as pd
from PIL import Image
from pathlib import Path
from typing import Union

from .uni_logger import UniLogger


class uniSaver:
    """A simple utility class for saving various data types to appropriate file formats.
    """

    def __init__(self, logger=None):
        if not logger:
            self.logger = UniLogger(file_suffix="uniSaver")
        else:
            self.logger = logger

    def save(self, data, file_path: Union[Path, str]):
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
        }

        if data_type not in extension_mapping:
            self.logger.log("ERROR", f'Unsupported data type "{data_type}"')
            return

        expected_extension = extension_mapping[data_type]

        # Verify or append the correct extension
        if file_path.suffix != expected_extension:
            if file_path.suffix:
                raise ValueError(
                    f'Invalid file extension for {data_type}. Expected "{expected_extension}" but got "{file_path.suffix}"')
            else:
                file_path = file_path.with_suffix(expected_extension)

        try:
            if data_type == 'dict':
                self._save_json(data, file_path)
            elif data_type == 'list':
                self._save_list(data, file_path, expected_extension)
            elif data_type == 'DataFrame':
                self._save_parquet(data, file_path)
            elif data_type == 'Image':
                self._save_image(data, file_path)

            self.logger.log("INFO", f'{data_type} SAVED SUCCESSFULLY to "{file_path}"')
        except Exception as e:
            self.logger.log("ERROR", f'{data_type} SAVE ERROR at "{file_path}": {e}')

    def _list_extension(self, data: list):
        if all(isinstance(item, dict) for item in data):
            return '.jsonl'
        elif all(isinstance(item, str) for item in data):
            return '.txt'
        else:
            raise TypeError("List content must be either all dictionaries or all strings.")

    def _save_json(self, data: dict, file_path: Path):
        with open(file_path, "w") as f:
            json.dump(data, f)

    def _save_list(self, data: list, file_path: Path, extension: str):
        if extension == '.jsonl':
            self._save_jsonl(data, file_path)
        elif extension == '.txt':
            self._save_txt(data, file_path)
        else:
            raise ValueError("Invalid extension for list data.")

    def _save_jsonl(self, data: list, file_path: Path):
        with open(file_path, "w") as f:
            for item in data:
                json.dump(item, f)
                f.write('\n')

    def _save_txt(self, data: list, file_path: Path):
        with open(file_path, "w") as f:
            for item in data:
                f.write(f'{item}\n')

    def _save_parquet(self, data: pd.DataFrame, file_path: Path):
        data.to_parquet(file_path)

    def _save_image(self, data: Image.Image, file_path: Path):
        data.save(file_path)


if __name__ == "__main__":
    # Usage example
    logger = UniLogger("logs", file_suffix="data_saver")
    data_saver = uniSaver(logger)
    json_data = {'key': 'value'}
    data_saver.save(json_data, "example")  # Automatically adds .json
    jsonl_data = [{'key1': 'value1'}, {'key2': 'value2'}]
    data_saver.save(jsonl_data, "example.jsonl")
    txt_data = ['line1', 'line2']
    data_saver.save(txt_data, "example.txt")
    image_data = Image.new('RGB', (60, 30), color='red')
    data_saver.save(image_data, "example.png")
    df_data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    data_saver.save(df_data, "example.parquet")