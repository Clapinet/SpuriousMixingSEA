from typing import List

from utilities.paths import paths

from pathlib import Path

from data.loaders import *
from data.cleaners import *

DEFAULT_DIRS = [
    Path(""),
    paths.work_data_path,
    paths.raw_data_path,
    paths.intermediate_data_path,
    paths.primary_data_path,
]


def _check_all_paths(path: Path, paths_list: List[Path]) -> Path:
    for pth in paths_list:
        if (pth / path).exists():
            return pth / path
    raise FileNotFoundError(f"Cannot find data at {path}.")


def check_path_existence(
        path: Path,
        default_dirs: List[Path] = DEFAULT_DIRS) -> Path:
    """
    Check if given path exists :
    - absolutely
    - relatively to cwd
    - relatively to given default_dir

    Return existing path, if any. Raise error otherwise.
    """
    path = Path(path)  # in case not provided

    if not path.exists():
        path_to_data = _check_all_paths(path, default_dirs)
    else:
        path_to_data = Path(path)
    return path_to_data


class DataGetter:
    def __init__(
        self,
        file_type: str,
        cleaning: str = None,
        loading_kwargs={},
        processing_kwargs={},
    ):
        self._loader = get_loader(file_type)()
        self._cleaner = get_processor(cleaning)()

        # Kwargs
        self._loading_kwg = loading_kwargs
        self._cleaning_kwg = processing_kwargs

    def add_kwg(self, key, value, where="loading"):
        if where == "loading":
            self._loading_kwg[key] = value
        elif where == "processing":
            self._cleaning_kwg[key] = value
        else:
            raise KeyError(f"Unknown value {where} for where arg.")

    def get(self, path: Path, filtering_pattern=""):
        path_to_data = check_path_existence(path)
        data = self._loader.load(
            path_to_data, filtering_pattern=filtering_pattern, **self._loading_kwg
        )
        data = self._cleaner.clean(data, **self._cleaning_kwg)
        return data
