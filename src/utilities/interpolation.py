import numpy as np
import xarray as xr

from wrf import interplevel

import tqdm


def interp_variable(var: xr.DataArray, depth3d: xr.DataArray, depth1d: np.ndarray, h_sign=1, depth_name="depth_t", **kwargs):

    if len(depth3d.shape) == 1:
        print("Base depth field provided is 1d, should be 3d. Returning base data.")
        return var

    sign3d = np.sign(depth3d.mean()) * h_sign
    sign1d = np.sign(depth1d.mean()) * h_sign

    data = interplevel(var, sign3d * depth3d, sign1d * depth1d, **kwargs)

    data = data.rename(level=depth_name)

    return data


@xr.register_dataset_accessor("interpolation")
class InterpAccessor:

    def __init__(self, dataset):
        self._obj = dataset

    def _interp(self, var, depth1d, h_sign=1, depth_name="depth"):

        var_type = self._obj[var].dims[-1][-1]

        depth3d = self._obj[f"depth_{var_type}"]

        das = []
        for t in tqdm.tqdm(self._obj["time"]):
            da = interp_variable(
                self._obj[var].sel(time=t),
                depth3d,
                depth1d,
                h_sign=h_sign,
                depth_name=depth_name
            ).assign_coords(time=t)
            das.append(da)

        return xr.concat(das, dim="time")