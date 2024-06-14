import os
import json
import pandas as pd
from PIL import Image, JpegImagePlugin, PngImagePlugin
from typing import Union

from unibox.utils.uni_logger import UniLogger
from unibox.utils.s3_client import S3Client  # Assuming S3Client is in a module named s3_client


class UniSaver:
    """A simple utility class for saving various data types to appropriate file formats."""
    
    def __init__(self, logger=None, debug_print=True, s3_client=None):
        self.logger = logger or UniLogger(file_suffix="UniSaver")
        self.debug_print = debug_print
        self.s3_client = s3_client or S3Client()

    def saves(self, data, file_path: str):
        """Save data to the given file path."""
        data_type = type(data).__name__
        expected_extension = self._get_expected_extension(data_type, data)
        file_path = self._validate_and_append_extension(file_path, expected_extension)

        is_s3 = file_path.startswith("s3://")
        local_file_path = self._get_local_file_path(file_path, is_s3)

        try:
            self._save_data(data, data_type, local_file_path, expected_extension)
            if is_s3:
                self._upload_to_s3(local_file_path, file_path)
            if self.debug_print:
                self.logger.info(f'{data_type} saved successfully to "{file_path}"')
        
        except PermissionError:
            self._handle_permission_error(data, data_type, local_file_path, expected_extension)
            if self.debug_print:
                self.logger.info(f'{data_type} saved successfully to "{file_path}"')
        
        except Exception as e:
            self.logger.error(f'{data_type} save ERROR at "{local_file_path}": {e}')

    def _get_expected_extension(self, data_type, data):
        if data_type == 'list':
            extension = self._list_extension(data)
        else:
            extension_mapping = {
                'dict': '.json',
                'DataFrame': '.parquet',
                'str': '.txt'
            }

            # Generalize for Image types
            if isinstance(data, Image.Image):
                extension = '.png'
            elif data_type not in extension_mapping:
                self.logger.error(f'Unsupported data type "{data_type}"')
                raise ValueError(f'Unsupported data type "{data_type}"')
            else:
                extension = extension_mapping[data_type]
        
        return extension

    def _validate_and_append_extension(self, file_path: str, expected_extension: str) -> str:
        if not file_path.endswith(expected_extension):
            if '.' in file_path:
                self.logger.error(f'Invalid file extension for expected "{expected_extension}" but got "{file_path.split(".")[-1]}"')
                self.logger.warning("File extension will be appended to the file name")

            file_path += expected_extension
            self.logger.warning(f"File without extension, saving to actual path: {file_path}")
        
        return file_path

    def _get_local_file_path(self, file_path: str, is_s3: bool) -> str:
        if is_s3:
            return os.path.basename(file_path)  # Use only the basename for the local file path
        return file_path

    def _save_data(self, data, data_type, file_path, expected_extension=None):
        
        if isinstance(data, Image.Image): # Handle image data separately
            self._save_image(data, file_path)
            return
        
        save_function_mapping = {
            'dict': self._save_json,
            'list': lambda d, p: self._save_list(d, p, expected_extension),
            'set': lambda d, p: self._save_list(list(d), p, expected_extension),
            'DataFrame': self._save_parquet,
            'str': lambda d, p: self._save_txt([d], p)
        }

        if data_type not in save_function_mapping:
            self.logger.error(f'No save function available for data type "{data_type}"')
            raise ValueError(f'No save function available for data type "{data_type}"')

        save_function_mapping[data_type](data, file_path)

    def _upload_to_s3(self, local_file_path: str, s3_file_path: str):
        s3_dir = os.path.dirname(s3_file_path)
        self.s3_client.upload(local_file_path, s3_dir)
        os.remove(local_file_path)

    def _handle_permission_error(self, data, data_type, local_file_path, expected_extension):
        alternative_file_path = local_file_path.replace('.parquet', '_alternative.parquet')
        self.logger.warning(f'Permission denied for "{local_file_path}". Trying to save to "{alternative_file_path}" instead.')
        self._save_data(data, data_type, alternative_file_path, expected_extension)

    def _list_extension(self, data: list) -> str:
        if all(isinstance(item, dict) for item in data):
            return '.jsonl'
        elif all(isinstance(item, str) for item in data):
            return '.txt'
        else:
            raise TypeError("List content must be either all dictionaries or all strings.")

    def _save_json(self, data: dict, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_list(self, data: list, file_path: str, extension: str):
        if extension == '.jsonl':
            self._save_jsonl(data, file_path)
        elif extension == '.txt':
            self._save_txt(data, file_path)
        else:
            raise ValueError("Invalid extension for list data.")

    def _save_jsonl(self, data: list, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')

    def _save_txt(self, data: list, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(f'{item}\n')

    def _save_parquet(self, data: pd.DataFrame, file_path: str):
        data.to_parquet(file_path, index=False)

    def _save_image(self, data: Image.Image, file_path: str):
        if not isinstance(data, (JpegImagePlugin.JpegImageFile, PngImagePlugin.PngImageFile)):
            data = data.convert("RGB")  # Convert to standard Image object if not already one
        data.save(file_path)


def sample_usage():
    # Usage example
    logger = UniLogger("logs", file_suffix="saver")
    saver = UniSaver(logger=logger, s3_client=s3_client)
    
    # Save to local
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
    
    # Save to S3
    saver.saves(json_data, "s3://my-bucket/example.json")
    saver.saves(image_data, "s3://my-bucket/example.png")
    saver.saves(df_data, "s3://my-bucket/example.parquet")


def debug_saver():
    # import pandas as pd
    # sample_df = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    # saver = UniSaver()
    # saver.saves(sample_df, "s3://unidataset-danbooru/sample_df.parquet")

    from PIL import Image
    from unibox.utils.uni_loader import UniLoader

    loader = UniLoader()
    jpeg_file = loader.loads("https://cdn.donmai.us/180x180/8e/ea/8eea944690c0c0b27e303420cb1e65bd.jpg")

    
    saver = UniSaver()
    saver.saves(jpeg_file, "s3://unidataset-danbooru/sample_image.jpg")
