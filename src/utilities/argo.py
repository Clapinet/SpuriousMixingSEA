import xarray as xr


def get_weights_from_std(d_std: xr.Dataset, **sum_kwargs) -> xr.Dataset:
    """ Stuff. """
    return (1 / d_std) / ((1 / d_std).sum(**sum_kwargs))