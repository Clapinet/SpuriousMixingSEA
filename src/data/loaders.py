import xarray as xr
import pandas as pd

from pathlib import Path
import re

from utilities.func import check_matching


def get_loader(file_type):
    # Using a fun instead of a dic might be les elegant / more cumbersome
    # but allows for more flexibility on filtering.
    all_loaders = {
        "zarr": ZARRLoader,
        "mfd": MFDLoader,
        "netcdf": NCLoader,
        "csv": CSVLoader,
    }

    # process loader_name : could be more fancy but ftm we keep it simple
    loader_name = file_type.lower()

    # perform check just to print available options if not correctly given
    check_matching(loader_name, all_loaders, "loader")
    return all_loaders[loader_name]


#%%
class Loader:
    def load(self, path, **kwargs):
        pass


#%%
class MFDLoader(Loader):
    def __init__(self):
        self.file_endings = [".nc", ".gz"]

    def load(self, path, filtering_pattern="", **kwargs):
        return self._load_mfd(path, filtering_pattern=filtering_pattern, **kwargs)

    def _filter(self, name: str, pattern: str = ""):
        return (name[-3:] in self.file_endings) and (
            re.search(pattern, name) is not None
        )

    def _load_mfd(self, path, filtering_pattern="", **kwargs):

        files = [
            f
            for f in Path(path).iterdir()
            if self._filter(f.name, pattern=filtering_pattern)
        ]

        if not files:
            raise FileNotFoundError(f"Location {path} is empty.")
        files.sort()
        ds = xr.open_mfdataset(files, **kwargs)
        return ds.chunk(kwargs["chunks"])


class CSVLoader(Loader):
    def load(self, path, **kwargs):
        kwargs.pop("filtering_pattern")
        return pd.read_csv(path, **kwargs)


class ZARRLoader(Loader):
    def load(self, path, **kwargs):
        kwargs.pop("filtering_pattern")
        return xr.open_zarr(path, **kwargs)


class NCLoader(Loader):
    def load(self, path, **kwargs):
        kwargs.pop("filtering_pattern")
        return xr.open_dataset(path, **kwargs)
