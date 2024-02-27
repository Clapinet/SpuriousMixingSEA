from typing import Optional, List

import yaml
from pathlib import Path
from copy import deepcopy
from functools import singledispatch

from data.getters import DataGetter

from utilities.paths import paths

default_information_location = paths.config_path / "data_sources"


def check_validity(information: dict, values_to_check) -> bool:
    """
    Check that a dictionary actually contains a set of given values as keys.
    """

    missing = [k for k in values_to_check if k not in information]
    if missing:  # => if missing is not empty
        raise ValueError(
            f"Missing data in information file. Please provide : {missing}"
        )
    return True


def preprocess_value(info_key: str, info_data: object) -> object:
    """
    Given a value and a name for it, modify the value depending on name.
    (e.g. change str as Path if name contains "path")
    """

    # transform str paths as actual paths
    if "path" in info_key:
        if isinstance(info_data, str) or isinstance(info_data, Path):
            return Path(info_data)
        else:
            raise TypeError(
                f"Data {info_data} at Key {info_key} "
                f"interpreted as path but not a string."
            )
    else:
        return info_data


def load_yaml_file(info_file: str, info_location: Path) -> dict:
    """
    Open yaml file at given location and return corresponding dict.
    """
    if info_file[-4:] == ".yml":
        file_name = info_file
    else:
        file_name = info_file + ".yml"

    with open(info_location / file_name) as f:
        info = yaml.safe_load(f)
    return info


def open_multiple_yaml_files(location: Path) -> dict:
    # TODO : make it being called only once
    """
    Open and merge into one dict all .yml files at given location.

    Parameters
    ----------
    location:   Path
                Path to files.
    Returns
    -------

    Dict of merged files.
    """
    # Get files to process
    list_of_files = [f for f in location.iterdir() if f.suffix == ".yml"]

    # Merge dicts
    dic = {}
    for file_name in list_of_files:
        with open(file_name, "r") as f:
            tmp_dic = yaml.safe_load(f)

            if tmp_dic is None:  # empty file
                tmp_dic = {}
            dic.update(tmp_dic)

    return dic


# %%
class DataSource:
    def __init__(
            self,
            info_file_name: str = "",
            filtering_pattern: Optional[str] = None,
            info_location: Path = default_information_location,
    ):
        """

        Parameters
        ----------
        info_file_name:     str
                            Name of file to load.

        filtering_pattern:  str, optional.
                            If provided, directly call get_data method with given filtering_pattern.

        info_location:      Path
                            Path to directory where .yml information files are stored.

        """

        # Instantiate important attributes, for clarity
        self.name = None
        self.file_type = None
        self.file_path = None
        self.data_type = None
        need_to_be = vars(self)

        # Optional attributes
        self.processing_level = 0  # number of processing applied on data
        self.cleaning = None
        self.loading_kwargs = {}
        self.cleaning_kwargs = {}

        # Load info
        info = open_multiple_yaml_files(info_location)[info_file_name]
        # check_validity(info, need_to_be)  # check that no data_sources is missing
        # => Not working as I intended : not all attributes are necessary but var(.)
        # => load them all.

        # Load data in attributes
        for entry in info:
            value = preprocess_value(entry, info[entry])
            setattr(self, entry, value)

        self.d = None  # actual data

        if filtering_pattern is not None:
            self.get_data(filtering_pattern)

    def get_data(self, filtering_pattern=""):
        """ Actually load data in attribute .d using given path."""
        print("Loading", self.name, end=" ")
        d = DataGetter(
            self.file_type, self.cleaning, self.loading_kwargs, self.cleaning_kwargs
        ).get(self.file_path, filtering_pattern=filtering_pattern)
        print("=> done.")
        self.d = d
        return d

    # Manipulation
    # ------------

    def duplicate(self, update_d=None):
        """
            Create and return new DataSource object with same attributes,
        except for .d, that might be changed by specifying update_d != None.
        """
        cp = deepcopy(self)
        if update_d is not None:
            cp.d = update_d
        return cp

    def apply_f(self, func, *fargs, inplace=False, **fkwargs):
        """
            Apply a given function to data contained in object.
        Return either a new object or modify inplace.
        """
        if inplace:
            self.d = func(self.d, *fargs, **fkwargs)
        else:
            return self.duplicate(func(self.d), *fargs, **fkwargs)

    def apply_m(self, method, *margs, inplace=False, **mkwargs):
        """
        Apply a method to data.

        Parameters
        ----------
        method:     str
                    Name of the methode to apply to the data

        inplace:    bool, default=True
                    Whether to modify data inplace or output new object.
        margs:
        mkwargs

        Returns
        -------
        """
        if inplace:
            self.d = getattr(self.d, method)(*margs, **mkwargs)
        else:
            return self.duplicate(getattr(self.d, method)(*margs, **mkwargs))

    def apply(self, to_apply, *args, inplace=False, **kwargs):
        if isinstance(to_apply, str):
            return self.apply_m(to_apply, *args, inplace=inplace, **kwargs)
        else:
            return self.apply_f(to_apply, *args, inplace=inplace, **kwargs)

    def __add__(self, other):
        if isinstance(other, DataSource):
            return self.duplicate(self.d + other.d)
        else:
            return self.duplicate(self.d + other)

    def __sub__(self, other):
        if isinstance(other, DataSource):
            return self.duplicate(self.d - other.d)
        else:
            return self.duplicate(self.d - other)

# %%


def get_dataset(name: str, filtering_pattern: str):
    return DataSource(name, filtering_pattern).d


def create_sources(*names, info_location=default_information_location, gridded=False):
    out = []
    for nm in names:
        if not gridded:
            dts = DataSource(nm, info_location=info_location)
        else:
            dts = GriddedSource(nm, info_location=info_location)
        out.append(dts)

    if len(out) == 1:
        out = out[0]

    return out


def load_source(sources: DataSource, filtering_pattern: str = ""):
    sources.get_data(filtering_pattern=filtering_pattern)


def load_sources(sources: List[DataSource], filtering_pattern: str = ""):
    for sr in sources:
        sr.get_data(filtering_pattern=filtering_pattern)


# %%


class GriddedSource(DataSource):

    lon_t = None
    lat_t = None

    def _get_space_coord(self, coord, index_name, var_type="t"):

        if self.d is None:
            self.get_data()

        if self.data_type == "satellite":
            return getattr(self.d, coord)

        elif self.data_type == "model" or self.data_type == "grid":
            if self.model == "SYMPHONIE" or self.model == "NEMO":
                return getattr(self.d, coord + f"_{var_type}")  # TODO : allows for u, v, w
            else:
                try:
                    return getattr(self.d, coord)
                except AttributeError:
                    raise TypeError(
                        f"Getting space coordinate not handled for model type {self.model}."
                    )

        else:
            raise TypeError(
                f"Getting space coordinate not handled for data_type {self.data_type}."
            )

    def get_lon(self, var_type="t"):
        attr_name = f"lon_{var_type}"
        if getattr(self, attr_name) is None:
            setattr(
                self,
                attr_name,
                self._get_space_coord("lon", "j", var_type=var_type)
            )

        return getattr(self, attr_name)

    def get_lat(self, var_type="t"):
        attr_name = f"lat_{var_type}"
        if getattr(self, attr_name) is None:
            setattr(
                self,
                attr_name,
                self._get_space_coord("lat", "j", var_type=var_type)
            )

        return getattr(self, attr_name)
