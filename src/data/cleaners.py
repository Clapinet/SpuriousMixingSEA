from typing import Protocol, TypeVar

from utilities.paths import paths
from utilities.grids import get_grid
from utilities.func import check_matching

import xarray as xr
import numpy as np
import pandas as pd

from itertools import product


def get_processor(cleaning_name: str):
    all_cleanings = {
        "sea312": SEA312Cleaner,
        "sea312surface": SEA312SurfaceCleaner,
        "ostia": OSTIACleaner,
        "glorys": GLORYSCleaner,
        "sym_grd": SYMPHONIEGridCleaner,
    }

    if cleaning_name is not None:
        # process the name
        name = cleaning_name.lower()
    else:
        return IdentityCleaner  # base class does not modify data at all

    check_matching(name, all_cleanings, "processing")
    return all_cleanings[name]


#%%
T = TypeVar("T")


class Cleaner(Protocol[T]):
    def clean(self, data: T, **kwargs) -> T:
        pass


#%%


class IdentityCleaner:
    def clean(self, data: T, **kwargs) -> T:
        return data


class SEA312Cleaner(Cleaner):

    renaming = {
        "ni_t": "lon_t",
        "nj_t": "lat_t",
        "ni_u": "lon_u",
        "nj_u": "lat_u",
        "ni_v": "lon_v",
        "nj_v": "lat_v",
        "ni_w": "lon_w",
        "nj_w": "lat_w"
    }

    to_drop = [
        "cumulativetime",
        "longitude_t",
        "latitude_t",
        "longitude_u",
        "longitude_v",
        "latitude_u",
        "latitude_v",
        "longitude_w",
        "latitude_w",
    ]

    var_types = ["t", "u", "v"]
    depths = ["depth_t", "depth_u", "depth_v", "depth_w"]

    def _get_values_from_grid(self, grid):
        """
        Extract explicit coordinates values from given SYMPHONY grid.
        """

        lon, lat = {}, {}
        for var_type in self.var_types:
            masked_lon, masked_lat = (
                grid.variables[f"longitude_{var_type}"][:],
                grid.variables[f"latitude_{var_type}"][:],
            )
            lon[var_type] = masked_lon.mean(axis=0)
            lat[var_type] = masked_lat.mean(axis=1)
        values = {f"ni_{v}": lon[v] for v in self.var_types}
        values.update({f"nj_{v}": lat[v] for v in self.var_types})

        # set "lon_w" to "lon_t"
        values.update({"ni_w": lon["t"].values})
        values.update({"nj_w": lat["t"].values})
        values.update({d: getattr(grid, d) for d in self.depths})

        return values

    def _change_coordinate_values(self, dataset, values_dict):
        """
        Change and rename a given set of dimensions with given new values
        and new names. Also
        """

        ds_rename = dataset.copy()

        for d in values_dict:
            # we first add depth arrays in order to avoid conflicts with dimensions
            if d[:5] == "depth":
                ds_rename[d] = values_dict[d]

        for d in values_dict:
            if d[:5] != "depth":
                ds_rename[d] = values_dict[d]
        ds_rename = ds_rename.rename(self.renaming)

        # Remove useless fields
        try:
            ds_rename = ds_rename.drop(self.to_drop, errors="ignore")
        except ValueError:
            print(self.to_drop)
            print()
            print([k for k in ds_rename])

        return ds_rename

    def clean(self, data: xr.Dataset, **kwargs) -> xr.Dataset:
        """
        Change integers coordinates in longitude, latitude for explicit selection, and
        drop useless variables.

        Parameters
        ----------
        data:   xr.Dataset
                SYMPHONIE Dataset output to clean.

        kwargs: dict
                Keywords arguments for get_grid : configuration, coordinates.

        Returns
        -------
        xr.Dataset

        """
        grid = get_grid(**kwargs)
        vls = self._get_values_from_grid(grid)
        return self._change_coordinate_values(data, vls)


class SEA312SurfaceCleaner(Cleaner):

    renaming = {
        "ni_t": "lon_t",
        "nj_t": "lat_t",
        "ni_u": "lon_u",
        "nj_u": "lat_u",
        "ni_v": "lon_v",
        "nj_v": "lat_v",
        "ni_w": "lon_w",
        "nj_w": "lat_w"
    }

    to_drop = [
        "cumulativetime",
        "longitude_t",
        "latitude_t",
        "longitude_u",
        "longitude_v",
        "latitude_u",
        "latitude_v",
        "latitude_w",
        "longitude_w",
    ]

    var_types = ["t", "u", "v", "w"]

    def _get_values_from_grid(self, grid):
        """
        Extract explicit coordinates values from given SYMPHONY grid.
        """

        lon, lat = {}, {}
        excluded = []
        for var_type in self.var_types:
            try:
                masked_lon, masked_lat = (
                    grid.variables[f"longitude_{var_type}"][:],
                    grid.variables[f"latitude_{var_type}"][:],
                )
                lon[var_type] = masked_lon.mean(axis=0)
                lat[var_type] = masked_lat.mean(axis=1)
            except KeyError:
                excluded.append(var_type)
        values = {f"ni_{v}": lon[v] for v in self.var_types if v not in excluded}
        values.update({f"nj_{v}": lat[v] for v in self.var_types if v not in excluded})

        return values

    def _change_coordinate_values(self, dataset, values_dict):
        """
        Change and rename a given set of dimensions with given new values
        and new names. Also
        """

        ds_rename = dataset.copy()

        for d in values_dict:
            # we first add depth arrays in order to avoid conflicts with dimensions
            if d[:5] == "depth":
                ds_rename[d] = values_dict[d]

        for d in values_dict:
            if d[:5] != "depth":
                ds_rename[d] = values_dict[d]

        for k, it in self.renaming.items():
            try:
                ds_rename = ds_rename.rename({k: it})
            except (ValueError, KeyError) as e:
                print(e)
                pass

        # Remove useless fields
        try:
            ds_rename = ds_rename.drop(self.to_drop, errors="ignore")
        except ValueError:
            print(self.to_drop)
            print()
            print([k for k in ds_rename])

        return ds_rename

    def clean(self, data: xr.Dataset, **kwargs) -> xr.Dataset:
        grid = get_grid(**kwargs)
        vls = self._get_values_from_grid(grid)
        out = self._change_coordinate_values(data, vls)
        try:
            return out.squeeze()
        except KeyError:
            print("KeyError while cleaning data : returning raw.")
            return data


class SYMPHONIEGridCleaner(Cleaner):

    def clean(self, data: T, **kwargs) -> T:
        var_s = ["longitude", "latitude"]
        type_s = ["t", "u", "v", "f"]
        renaming_dict = {f"{s}_{t}": f"{s[:3]}_{t}" for s, t in product(var_s, type_s)}
        return data.rename(renaming_dict)


#%% Satellites
class OSTIACleaner(Cleaner):
    def clean(self, data: xr.Dataset, **kwargs) -> xr.Dataset:
        renaming_dict = {"analysed_sst": "tem"}
        data["analysed_sst"] = data.analysed_sst - 273.15  # K -> °C
        return data.rename(renaming_dict)


class GLORYSCleaner(Cleaner):
    def clean(self, data: xr.Dataset, **kwargs) -> xr.Dataset:
        renaming_dict = {
            "latitude": "lat_t",
            "longitude": "lon_t",
            "depth": "depth_t",
            "thetao": "tem",
            "so": "sal",
        }

        return data.rename(renaming_dict)


def get_renaming_dict(nemo_config: str, var: str="t"):
    if nemo_config == "SEAsia":
        renaming_dict = {
            "y": "lat_t",
            "x": "lon_t",
            # "nav_lon": "lon_t",
            # "nav_lat": "lat_t",
            "deptht": "depth_t",
            "time_counter": "time",
            "toce_e3t": "tem_w",
            "soce_e3t": "sal_w"
        }
    else:
        renaming_dict = {
            "y": f"lat_{var}",
            "x": f"lon_{var}",
            # "nav_lon": "lon_t",
            # "nav_lat": "lat_t",
            f"depth{var}": f"depth_{var}",
            "time_counter": "time",
        }
        if var == "t":
            renaming_dict.update({
                "thetao": "tem",
                "so": "sal"
            })

    return renaming_dict