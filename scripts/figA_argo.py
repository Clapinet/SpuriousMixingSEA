import numpy as np

from data.sources import GriddedSource, DataSource

from plotting.display import set_style

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import seaborn as sns

import cmcrameri.cm as cmc

from utilities.paths import paths

#%%
if __name__ == '__main__':

    zones = [
        "SCS",
        # "SORTIENA",
        "SULU",
        "CEL",
        "MAK",
        "SUDMOL",
        "NORDMOL",
        "WESTIND",
    ]

    interior_color = "lightgrey"
    colors = {
        "SCS": interior_color,
        "SULU": interior_color,
        "CEL": interior_color,
        "MAK": interior_color,
        "SUDMOL": interior_color,
        "NORDMOL": interior_color,
        "WESTIND": interior_color,
    }

    # Get grid information
    grid = GriddedSource("grid_VQSF", "")
    bathy = grid.d.hm_w  # max depth

    # Get information on ARGO profiles
    argo = DataSource("ARGO_features", "").d
    # Filter data
    argo = argo[
        (
                # (argo["year"] == 2017) |
                (argo["year"] == 2018)
        ) & (argo["zone"] != "SORTIENA")
    ]
    #%%
    grid_lon = grid.get_lon()
    grid_lat = grid.get_lat()
    lon_min, lon_max = grid_lon.min(), grid_lon.max()
    # lat_min, lat_max = lat.min(), lat.max()
    lat_min, lat_max = -16, 24

    lon, lat = (
        np.linspace(lon_min, lon_max, 50),
        np.linspace(lat_min, lat_max, 50),
    )

    loc = MultipleLocator(10)

    #%%
    set_style("paper")

    fig, ax = plt.subplots(
        figsize=(5, 5),
        subplot_kw={"projection": ccrs.Mercator()}
    )

    # Display bathy
    ax.pcolormesh(
        grid_lon, grid_lat, bathy,
        transform=ccrs.PlateCarree(),
        cmap=cmc.oslo_r,
        alpha=0.35
    )
    ctr = ax.contour(grid_lon, grid_lat, bathy, [100, 1000], colors="grey", transform=ccrs.PlateCarree(), linewidths=0.2)

    # Customize
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])

    # Add land
    land_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m')
    ax.add_feature(land_10m,
                   # facecolor="#f7f1aa",
                   # facecolor="#bfbfbf",
                   facecolor="#e9e7d9",  # light yellow
                   edgecolor="k",
                   lw=0.6,
                   alpha=0.6
                   )
    # ax.add_feature(cfeature.BORDERS, lw=0.2)
    #%%
    col_pal = sns.color_palette("hls", len(zones))
    for i, z in enumerate(zones):
        print(z)
        df = argo[argo["zone"] == z]

        mean_lon = df["lon"].mean()
        mean_lat = df["lat"].mean()
        n_prf = len(df)

        ax.scatter(
            mean_lon,
            mean_lat,
            marker="o",
            s=int(np.sqrt(n_prf / len(argo)) * 3000),
            transform=ccrs.PlateCarree(),

            # Marker
            edgecolors="k",
            linewidths=1,
            # c=col_pal[i],
            c=colors[z],
            zorder=10 + i,
            alpha=0.65
        )
        ax.text(
            mean_lon,
            mean_lat,
            str(n_prf),
            ha="center",
            va="center",
            zorder=10 + i,

            transform=ccrs.PlateCarree(),
        )
    # ax.legend(loc="upper left")
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

    col_pal = sns.color_palette("hls", len(zones))
    for i, z in enumerate(zones):
        print(z)
        df = argo[argo["zone"] == z]
        ax.plot(
            df["lon"],
            df["lat"],
            ls="",
            marker="o",
            transform=ccrs.PlateCarree(),

            # Marker
            mec="k",
            mew=0.3,
            mfc=col_pal[i],
            ms=1.5,
            alpha=0.3
            # label=z
        )
#%%
    # ticks
    fig.savefig(
        paths.figures_path / "figA_argo_on_map.png",
        dpi=400,
        transparent=False
    )
    print("done")
 # %%

#%%
