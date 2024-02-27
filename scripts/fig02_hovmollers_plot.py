import xarray as xr
import numpy as np
import pandas as pd

from utilities.paths import paths
import utilities.names as names
from plotting.display import set_style, format_time_axis

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_toolkits.axes_grid1 as mpa
from mpl_toolkits.axes_grid1 import ImageGrid

import cmocean.cm as cmo
import cmcrameri.cm as cmc

from utilities.interpolation import interp_variable


from scipy.interpolate import interpn

#%%
PATH = paths.primary_data_path / "SYMPHONIE"

PARAMS = dict(
    sims=[
        "GLORYS",
        "SEA_312_T_H0V0_V_Q2",
        "SEA_312_NT_H0V0_V_Q2",
        "SEA_312_T_H1V1_V_Q2",
        "SEA_312_NT_H1V1_V_Q2",
    ],
    loc="mid_scs",
    var="sal",
    transparent=True,
    dpi=300
)

SIMS = PARAMS["sims"]

#%% Get data

data = {
    sim: xr.open_dataset(PATH / f"{sim}_tem_sal_profiles_{PARAMS['loc']}.nc") for sim in SIMS
}

#%% Compute mean profile
time_slice = slice("2017-01-03", "2018-12-30")
#%%

depth = np.linspace(0, 500, 100)
data_interp = {
    sim: interp_variable(data[sim][PARAMS["var"]], data[sim].depth_t, depth, h_sign=1)
    for sim in data
}
data_interp["GLORYS"] = data_interp["GLORYS"].interp(depth_t=depth)
print("Interpolated !")


#%%
data_mean = {
    sim: data_interp[sim].sel(time=time_slice).mean(dim=["lon_t", "lat_t"])
    for sim in data
}

#%%

# Salinity
if PARAMS['var'] == "sal":
    VMIN = 34
    VMAX = 34.7
    # VMAX = 35.5
    # VMIN = 34.5
    delta = 0.2
    contours = np.arange(VMIN, VMAX + 2 * delta, delta)
    cmap = cmo.haline
    # cmap = "jet"
    label = "[psu]"

elif PARAMS['var'] == "tem":
    VMIN = 5
    VMAX = 30
    delta = 5
    contours = np.arange(VMIN, VMAX + 2 * delta, delta)
    cmap = cmo.thermal
    label = "[°C]"

#%%
set_style("paper")

N_SIMS = len(SIMS)
FIG_LEN = 8
FIG_WID_PER_PLOT = 1

LON_MEAN = data[SIMS[0]].lon_t.mean().values
LAT_MEAN = data[SIMS[0]].lat_t.mean().values

#%%

fig, ax_s = plt.subplots(
    N_SIMS, 1,
    figsize=(FIG_LEN, FIG_WID_PER_PLOT * (N_SIMS)),
    constrained_layout=True
)
if N_SIMS == 1:
    ax_s = [ax_s]

for i, (ax, sim) in enumerate(zip(ax_s, data_mean)):
    print(sim)
    d = data_mean[sim]
    contours_kw = dict(
        linewidths=0.5,
        colors="k",
        zorder=10,
        alpha=0.5,
        # linestyles='--'
    )
    pcm_kw = dict(
        vmin=VMIN,
        vmax=VMAX,
        cmap=cmap,
        # cmap=cmc.devon
    )

    # Plot data
    if sim != "GLORYS" and sim != "INDESO":
        mesh = ax.pcolormesh(
            d.time.values,
            depth,
            d.values.T,
            **pcm_kw
        )
        ctr = ax.contour(
            d.time.values,
            depth,
            d.values.T,
            contours,
            **contours_kw
        )

    else:
        mesh = ax.pcolormesh(
            d.time.values,
            depth,
            d.values.T,
            **pcm_kw
        )
        ctr = ax.contour(
            d.time.values,
            depth,
            d.values.T,
            contours,
            **contours_kw
        )

    plt.clabel(ctr,
               np.array([34.60000000000001, 35.000000000000014]),

               fontsize="xx-small",
               inline_spacing=1,
               rightside_up=True
               )

    # Format y-axis
    # ax.set_ylim(-1500, 0)
    ax.set_ylim(350, 30)
    # y_ticks = np.array([500, 250, 0])
    # ax.set_yticks(y_ticks)
    # ax.set_yticklabels(y_ticks)
    if i == N_SIMS // 2:
        ax.set_ylabel("Depth [m]")
    # ax.invert_yaxis()
    try:
        ax.set_title(names.sim_names[names.get_real_names([sim])[0][8:]], loc='left')
    except KeyError:  # case : GLORYS or ECCO
        ax.set_title(names.sim_names[sim], loc='left')

    # Format x-axis
    skip_months = 6
    if i == N_SIMS - 1:
        format_time_axis(ax, d.time.values, mnrfmt="%b %Y", mjrfmt="%b %Y", month_interval=skip_months)
        # ax.text(pd.Timestamp("2016-12-30"), -510, "2017", ha="left", va="center")
        # ax.text(pd.Timestamp("2018-12-30"), -635, "o", ha="left", va="center")
    else:
        format_time_axis(ax, d.time.values, mnrfmt="", mjrfmt="", month_interval=skip_months)

    # Plot colorbar
    div = mpa.make_axes_locatable(ax)
    cax = div.append_axes("right", size="3%", pad=0.1)
    label = "" if i != N_SIMS // 2 else "[psu]"
    cbar = plt.colorbar(
        mesh, cax=cax, orientation="vertical", label=label
    )

fig_name = f"fig02_hovmoller.png"
print("Saving " + fig_name)
fig.savefig(
    paths.figures_path / fig_name,
    dpi=PARAMS["dpi"],
    transparent=PARAMS["transparent"],
)

#%%
