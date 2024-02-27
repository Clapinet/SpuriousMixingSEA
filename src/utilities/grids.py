import xarray as xr

from utilities.paths import paths

PATH = paths.grids_path


def get_grid(configuration="SEA_312", coordinates=None):
    if coordinates is not None and coordinates is not "":
        suffix = f"_{coordinates}"
    else:
        suffix = ""
    grid_name = f"grid_{configuration}{suffix}.nc"
    return xr.open_dataset(PATH / grid_name)