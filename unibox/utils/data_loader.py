import csv
import json
from PIL import Image
import tomli
from omegaconf import OmegaConf
from pathlib import Path
from .logger import UniLogger


class UniLoader:
    """简单的loader utils, 用于原样加载json, txt, csv, image等数据;
    数据cleaning写在具体使用的class里
    """

    def __init__(self, logger=None):
        if not logger:
            self.logger = UniLogger(file_suffix="UniLoader")
        else:
            self.logger = logger

    def _load_data(self, file_path: Path, load_func, encoding="utf-8"):
        """
        使用<Load_func>读取<file_path>的内容, 并返回
        """
        file_type = file_path.suffix.lstrip(".")
        if not file_path.exists():
            self.logger.log("ERROR", f'{file_type} DOES NOT EXIST at "{file_path}"')
            return None

        try:
            with open(file_path, "r", encoding=encoding) as f:
                data = load_func(f)

            if not data:
                self.logger.log("WARNING", f'EMPTY {file_type} file at "{file_path}"')
                return None

            return data
        except Exception as e:
            self.logger.log("ERROR", f'{file_type} LOAD ERROR at "{file_path}": {e}')
            return None

    def load_json(self, json_path: Path, encoding="utf-8"):
        # *.json
        return self._load_data(json_path, json.load, encoding)

    def load_txt(self, txt_path: Path, encoding="utf-8"):
        # *.txt
        return self._load_data(txt_path, lambda f: f.read(), encoding)

    def load_csv(self, csv_path: Path, delimiter=",", encoding="utf-8"):
        # *.csv
        return self._load_data(
            csv_path, lambda f: list(csv.reader(f, delimiter=delimiter)), encoding
        )

    def load_image(self, image_path: Path):
        try:
            return Image.open(image_path)
        except Exception as e:
            self.logger.log("ERROR", f"image load error at {image_path}: {e}")
            return None

    def load_toml(self, toml_path: Path, encoding="utf-8"):
        return self._load_data(toml_path, tomli.load, encoding)

    def load_yaml(self, yaml_path: Path, encoding="utf-8"):
        return self._load_data(yaml_path, lambda f: OmegaConf.load(f), encoding)



# todo: implement unibox.loads() function

if __name__ == "__main__":
    # Usage example
    logger = UniLogger("logs", file_suffix="data_loader")
    data_loader = UniLoader(logger)
    json_data = data_loader.load_json(Path("example.json"))
    txt_data = data_loader.load_txt(Path("example.txt"))
    csv_data = data_loader.load_csv(Path("example.csv"))
    image_data = data_loader.load_image(Path("example.png"))
    toml_data = data_loader.load_toml(Path("example.toml"))
    yaml_data = data_loader.load_yaml(Path("example.yaml"))
