import pandas as pd
from collections import Counter
from typing import Any, Union
import json  # Import the json module


class CompactJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder for specific formatting of dictionaries and lists."""
    def iterencode(self, o, _one_shot=False):
        """Overridden method for custom JSON formatting."""
        if isinstance(o, (list, dict)):
            items = []
            if isinstance(o, dict):
                for key, value in o.items():
                    formatted_value = json.dumps(value, separators=(',', ': ')).replace('"', "'")
                    items.append(f"'{key}': {formatted_value}")
            else:  # For lists
                items = [json.dumps(item, separators=(',', ': ')).replace('"', "'") for item in o]
            yield from self._encode_line(items, isinstance(o, dict))
        else:
            yield from super().iterencode(o, _one_shot)

    def _encode_line(self, items, is_dict):
        """Helper method to yield formatted lines."""
        yield '{\n' if is_dict else '[\n'
        for i, item in enumerate(items):
            separator = ',' if i < len(items) - 1 else ''
            yield f'    {item}{separator}\n'
        yield '}\n' if is_dict else ']\n'

class UniPeeker:
    """Utility class for peeking into data with efficient methods."""

    def __init__(self, n: int = 3, console_print: bool = False):
        self.n = n
        self.console_print = console_print

    def peeks(self, data: Any, n: int = None, console_print: bool = None) -> dict:
        """Peek into the data and return metadata and a preview of the data, with efficient handling for large data."""
        peek_n = n if n else self.n
        _print = console_print if console_print is not None else self.console_print

        data_type = type(data).__name__
        meta_dict = {}
        preview = None

        if data_type == 'dict':
            meta_dict, preview = self._peek_dict(data, peek_n)
        elif data_type == 'DataFrame':
            meta_dict, preview = self._peek_dataframe(data, peek_n)
        elif data_type == 'list':
            meta_dict, preview = self._peek_list(data, peek_n)
        # Handling for other data types...

        if _print:
            self._print_info(data_type, meta_dict, preview)

        return {'metadata': meta_dict, 'preview': preview}

    def _peek_dict(self, data: dict, n: int) -> tuple:
        """Peek into a dictionary efficiently."""
        first_n = [(k, data[k]) for k in list(data)[:n]]
        value_types = Counter([type(v).__name__ for v in data.values()])
        is_nested = any(isinstance(v, dict) for v in data.values())

        meta_dict = {
            'len': len(data),
            'value_types': dict(value_types),
            'is_nested': is_nested
        }
        return meta_dict, first_n

    def _peek_dataframe(self, data: pd.DataFrame, n: int) -> tuple:
        """Peek into a DataFrame."""
        meta_dict = {
            'len': len(data),
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict(),
            'shape': data.shape
        }
        preview = data.head(n)
        return meta_dict, preview

    def _peek_list(self, data: list, n: int) -> tuple:
        """Peek into a list."""
        first_n = data[:n]
        meta_dict = {
            'len': len(data),
            'item_type': type(data[0]).__name__ if data else 'None'
        }
        return meta_dict, first_n

    def _print_info(self, data_type: str, meta_dict: dict, preview: Any) -> None:
        """Print information about the data using custom pretty print for the metadata."""
        data_len = meta_dict['len']

        # Convert dtypes to string if the data is a DataFrame
        if data_type == 'DataFrame':
            meta_dict['dtypes'] = {k: str(v) for k, v in meta_dict['dtypes'].items()}

        pretty_meta_dict = json.dumps(meta_dict, cls=CompactJSONEncoder, indent=4, sort_keys=True)
        print(f"[{data_type}] of size [{data_len}]:\n{pretty_meta_dict}\n")
        print(f"[Preview]\n{preview}")


if __name__ == '__main__':
    # Example usage:
    # some_dict_or_dataframe = {"name": "John", "age": 30}

    # df
    some_dict_or_dataframe = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

    unipeeker = UniPeeker()
    result = unipeeker.peeks(some_dict_or_dataframe)

    print("D")
