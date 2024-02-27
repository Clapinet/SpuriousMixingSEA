#%%
if __name__ == '__main__':

    cluster, client = init_dask_cluster("local")  #, walltime="00:15:00")
    client

# %%

    PARAMS = dict(
        var="tem",
        sat_ref="ostia",
        sat_dataset="OSTIA_monthly",
        time_slice=slice("2017-01-02", "2018-12-30"),
        unit="[°C]"
    )
#%%
    # Satellite data
    sat_data = dict(
        ostia=GriddedSource(PARAMS["sat_dataset"], ""),
    )

#%%

    # SYMPHONIE data
    sym_data = {
        "T0": GriddedSource("SEA_312_T_H0V0_V_Q2_surface_monthly", ""),
        "NT0": GriddedSource("SEA_312_NT_H0V0_V_Q2_surface_monthly", ""),
        "T1": GriddedSource("SEA_312_T_H1V1_V+_Q2_surface_monthly", ""),
        "NT1": GriddedSource("SEA_312_NT_H1V1_V_Q2_surface_monthly", ""),
    }

#%%

    N_REF = 0
    REF_SIM = sym_data[list(sym_data.keys())[N_REF]]
    REF_LON, REF_LAT = REF_SIM.get_lon(), REF_SIM.get_lat()

#%%
    # Satellite data
    mean_sat = sat_data[PARAMS["sat_ref"]].d[PARAMS["var"]]
    mean_sat = mean_sat.interp(lon=REF_LON, lat=REF_LAT).mean("time")

#%%
    # Model data
    mean_sym = {
        sim: sym_data[sim].d[PARAMS['var']].sel(time=PARAMS['time_slice']).mean(dim='time').squeeze().compute()
        for sim in sym_data
    }
#%%
    # Compute diff
    diff = {
        sim: mean_sym[sim] - mean_sat
        for sim in mean_sym
    }
#%%
import numpy as np

from data.sources import GriddedSource, DataSource

from utilities.paths import paths
from utilities.dask import init_dask_cluster

from plotting.display import set_style

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.ticker import MultipleLocator

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes

from cmocean import cm as cmo
from cmcrameri import cm as cmc

from matplotlib import path as mpath
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
import pandas as pd


def get_mask_zone(zone,lons, lats, grid_name=""):
    pth_to_npy = paths.raw_data_path / "ZONES" / f"{zone}_{grid_name}.npy"

    if pth_to_npy.is_file():
        with open(pth_to_npy, "rb") as f:
            mask = np.load(f)
    else:
        coord = pd.read_csv(paths.raw_data_path / "ZONES" / f"{zone}.csv")
        zone = mpath.Path(coord[["longitude", "latitude"]].values)

        mask = np.zeros((lons.size, lats.size))
        for i, ln in enumerate(lons):
            print(f"{i} / {lons.size}", end="\r")
            for j, lt in enumerate(lats):
                mask[i, j] = zone.contains_point((ln, lt))

        # Save data
        with open(pth_to_npy, "rb") as f:
            np.save(f, mask)

    return mask

#%%
    # Mean diff
    diff_mean = np.zeros_like(diff[list(diff.keys())[0]])

#%%
    MASK_ZONE_NAME = "SEA"
    MASK_ZONE_GRID = "SEA312"
    MASK_ZONE = get_mask_zone(MASK_ZONE_NAME, REF_LON, REF_LAT, MASK_ZONE_GRID).astype(bool)

    # Get Path
    _coord = pd.read_csv(paths.raw_data_path / "ZONES" / f"{MASK_ZONE_NAME}.csv")
    ZONE_PATH = mpath.Path(_coord[["longitude", "latitude"]].values)

    grid = GriddedSource("grid_VQSF", "")
    grid_lon = grid.get_lon()
    grid_lat = grid.get_lat()

#%%

    land_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m')

    # # Full map
    # lon_min, lon_max = REF_LON.min(), REF_LON.max()
    # lat_min, lat_max = -16, 24

    # Zoom on IS
    lon_min, lon_max = 106, 140
    lat_min, lat_max = -14, 14

    loc = MultipleLocator(10)

    set_style("paper")

    # PARAMETERS
    N_ROWS, N_COLS = 2, 2
    SIZE_PER_FIG = 6
    MINUS_DIFF_MEAN = False
    cmap = cmc.vik
    # cmap = "cmo.delta"
    vm = 2
    metric = "RMSE"
    ref_axis_for_colorbar = 0


    #%
    fig = plt.figure(figsize=(N_COLS * SIZE_PER_FIG, N_ROWS * SIZE_PER_FIG), layout="constrained")

    projection = ccrs.PlateCarree()
    axc = (GeoAxes,
           dict(map_projection=projection))

    ax_s = ImageGrid(
        fig,
        111,          # as in plt.subplot(111)
        nrows_ncols=(N_ROWS, N_COLS),
        axes_pad=0.15,
        cbar_location="bottom",
        cbar_mode="single",
        cbar_size="4%",
        cbar_pad=0.15,
        axes_class=axc,
        label_mode=""  # this line seems to be important : otherwise it doesnt work ...
    )


    sym_order = [
        "NT0",
        "NT1",
        "T0",
        "T1",
    ]

    for i, (ax, sim) in enumerate(zip(ax_s, sym_order)):
        # Plot data
        mesh = ax.pcolormesh(
            REF_LON, REF_LAT, diff[sim] - MINUS_DIFF_MEAN * diff_mean,
            cmap=cmap,
            vmin=-vm,
            vmax=vm,
            transform=ccrs.PlateCarree(),
            # levels=10
        )
        if i == 0 and MINUS_DIFF_MEAN:
            patch = mpatches.PathPatch(ZONE_PATH, facecolor=(0, 0, 0, 0), lw=1, ls="--")
            ax.add_patch(patch)

        if i == ref_axis_for_colorbar:
            ref_mesh = mesh
        data = diff[sim] - MINUS_DIFF_MEAN * diff_mean
        metrics = {
            "RMSE": np.sqrt((np.nanmean((data**2).values[MASK_ZONE.T]))),
            "bias": np.nanmean(data.values[MASK_ZONE.T])
        }

        # Details
        text_lat = 12.3
        ax.text(136, text_lat, sim, va="center", ha="center", fontsize="xx-large", transform=ccrs.PlateCarree())
        # ax.text(135, text_lat, f"{metrics[metric]:0.2f} {PARAMS['unit']}", va="center", ha="center")
        ax.set_extent([lon_min, lon_max, lat_min, lat_max])
        ax.add_feature(
            land_10m,
            # facecolor="#e9e9e9",
            facecolor="#c0c0c0",
            # facecolor="#bcbcbc",
            edgecolor="k",
            lw=0.4
        )

        ctr = ax.contour(
            grid_lon, grid_lat, grid.d.hm_w, [100, 500, 1000], colors="grey", transform=ccrs.PlateCarree(), linewidths=0.2
            # grid_lon, grid_lat, grid.d.hm_w, [200, 400, 600, 800, 1000], colors="grey", transform=ccrs.PlateCarree(), linewidths=0.2
        )

        gl = ax.gridlines(
            draw_labels=True,
            dms=True, x_inline=False, y_inline=False,
            xlocs=loc,
            ylocs=loc,
        )
        label_style = dict(color='gray', size="small")
        gl.xlines = False
        gl.ylines = False
        gl.xlabel_style = label_style
        gl.ylabel_style = label_style

        if i % N_COLS != 0:
            gl.left_labels = False
        if i % N_COLS != N_COLS - 1:
            gl.right_labels = False
        if i // N_COLS != 0:
            gl.top_labels = False
        if i // N_COLS != N_ROWS - 1:
            gl.bottom_labels = False

    ax.cax.colorbar(ref_mesh, label=f"$\\Delta$T {PARAMS['unit']}")
    ax.cax.toggle_label(True)
#%%
    transparent = True
    fig.savefig(
        paths.figures_path / f"fig04_bias_satellite.png",
        dpi=300,
        transparent=transparent
    )
    print("saved")
#%%

#%%
