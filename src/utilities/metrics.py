import xarray as xr
import numpy as np

# from dataclasses import dataclass
#
# @dataclass
# class Metric:


def rmse(d1: xr.Dataset, d2: xr.Dataset, weights=None, **mean_kwargs) -> xr.Dataset:
    """
    Root mean square error.
    """
    if weights is None:
        return np.sqrt(((d1 - d2)**2).mean(**mean_kwargs))

    else:
        return np.sqrt(((d1 - d2)**2).weighted(weights).mean(**mean_kwargs))


def diff_std(d1: xr.Dataset, d2: xr.Dataset, weights=None, **std_kwargs) -> xr.Dataset:
    """
    Std of difference.
    """
    if weights is None:
        return (d1 - d2).std(**std_kwargs)

    else:
        return (d1 - d2).weighted(weights).std(**std_kwargs)


def mae(d1: xr.Dataset, d2: xr.Dataset, weights=None, **mean_kwargs) -> xr.Dataset:
    """
    Mean absolute error.
    """

    if weights is None:
        return np.abs(d1 - d2).mean(**mean_kwargs)

    else:
        return np.abs(d1 - d2).weighted(weights).mean(**mean_kwargs)


def bias(d1: xr.Dataset, d2: xr.Dataset, weights=None, **mean_kwargs) -> xr.Dataset:
    """
    Bias.
    """

    if weights is None:
        return (d1 - d2).mean(**mean_kwargs)

    else:
        return (d1 - d2).weighted(weights).mean(**mean_kwargs)


def mare(d1: xr.Dataset, d_ref: xr.Dataset, weights=None, **mean_kwargs) -> xr.Dataset:
    """
    Mean absolute error.
    """

    if weights is None:
        return np.abs((d1 - d_ref) / d_ref).mean(**mean_kwargs)

    else:
        return np.abs((d1 - d_ref) / d_ref).weighted(weights).mean(**mean_kwargs)


my_metrics = dict(
    rmse=rmse,
    mae=mae,
    mare=mare,
    bias=bias,
    diff_std=diff_std,
)
