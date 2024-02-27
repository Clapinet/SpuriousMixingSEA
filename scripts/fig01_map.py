# # Data
import numpy as np

from data.sources import GriddedSource, DataSource

# # Plotting
from plotting.display import set_style

# Cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

# Matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import mpl_toolkits.axes_grid1 as mpa
import matplotlib.patheffects as path_effects

# # Misc
import cmcrameri.cm as cmc
import cmocean.cm as cmo

from utilities.paths import paths



#%%

# yellow = #faf307"
texts = {
    "South\nChina\nSea":
        (12.51866013144652, 114.38246428664561, "x-large", "white"),
    "Pacific\nOcean": (15, 135, "x-large", "white"),
    "Indian\nOcean": (-12, 98, "x-large", "white"),
    "Celebes\nSea": (3.081193955530461, 122.19594660323291, "small", "white"),
    "Banda\nSea": (-5.902044112805921, 127.61145510124497, "small", "white"),
    "Molucca \nSea": (-0.5076, 125.3, "x-small", "k"),
    "Java Sea": (-5.0699, 112.03, "small", "k"),
    "Sulu \nSea": (8.22, 120.1, "x-small", "k"),
}

edge_sizes = {
    "small": 1.1,
    "x-large": 2,
    "x-small": 1
}

#%%
if __name__ == '__main__':

    # Get grid information
    grid = GriddedSource("grid_VQSF", "")
    bathy = grid.d.hm_w  # max depth

    # Get information on ARGO profiles
    argo = DataSource("ARGO_features", "").d
    # Filter data
    argo = argo[((argo["year"] == 2017) | (argo["year"] == 2018)) & (argo["zone"] != "SORTIENA")]

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
        figsize=(7, 5),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )

    # Display bathy
    pcm = ax.pcolormesh(
        grid_lon, grid_lat, bathy,
        transform=ccrs.PlateCarree(),
        cmap=cmc.oslo_r,
        # cmap=cmo.deep,
        alpha=1
    )
    ctr = ax.contour(
        grid_lon, grid_lat, bathy, [100, 1000], colors="grey", transform=ccrs.PlateCarree(), linewidths=0.2)

    # Locations
    for t in texts:
        txt = ax.text(
            texts[t][1], texts[t][0],
            t,
            ha="center",
            va="center",
            color=texts[t][3],
            # color="orange",
            size=texts[t][2],
            fontfamily="serif",
            fontstyle="italic",
            fontstretch="extra-expanded",
            transform=ccrs.PlateCarree(),
            zorder=1001
        )
        if texts[t][3] != "k":
            txt.set_path_effects(
                [
                    path_effects.Stroke(
                        linewidth=edge_sizes[texts[t][2]],
                        foreground="k"
                    ),
                    # path_effects.SimpleLineShadow(offset=(5, -5), shadow_color='red', alpha=1),
                    path_effects.Normal()
                ]
            )
        shadow_offset = 0.05  # Adjust this value to control the shadow offset
        ax.text(
            texts[t][1] + shadow_offset, texts[t][0] - shadow_offset,
            t,
            ha="center",
            va="center",
            size=texts[t][2],
            fontfamily="serif",
            fontstyle="italic",
            fontstretch="extra-expanded",
            transform=ccrs.PlateCarree(),
            # color='#f1f0d7',
            color="yellow",
            alpha=0.45,
            zorder=1000
        )

    # Add localisation of hovmollers
    x_locs, y_locs = [117.25,
                      # 134.75
                      ], [17.5,
                          # 10.5
                          ]
    points = {
        "P": (0, 1.3),
        # "B": (1.4, 0)
    }
    ax.scatter(
        x_locs,
        y_locs,
        color="red",
        edgecolors="k",
    )
    for i, pt in enumerate(points):
        txt = ax.text(
            x_locs[i] + points[pt][0],
            y_locs[i] + points[pt][1],
            pt,
            ha="center",
            va="center",
            color="tab:red",
            size="large",
            fontfamily="serif",
            fontstretch="extra-expanded",
            transform=ccrs.PlateCarree(),
        )
        txt.set_path_effects(
            [
                path_effects.Stroke(
                    linewidth=1,
                    foreground="k"
                ),
                path_effects.Normal()
            ]
        )


# Colorbar
#     caxx = fig.add_axes((
#         1.2,  # position gauche
#         0.0,  # position bas
#         0.05, # largeur
#         1 # hauteur
#
#     ))

    div = mpa.make_axes_locatable(ax)
    cax = div.append_axes("right", size="4%", pad=0.1, axes_class=plt.Axes)
    cbar = plt.colorbar(
        pcm, cax=cax, orientation="vertical",
    )

    cbar.ax.invert_yaxis()
    cbar.set_label(
        label="Depth [m]",
        # weight="bold",
        size="x-large"
    )

    # Customize
    ax.set_aspect("equal")
    ax.tick_params(top=True, right=True, bottom=True, left=True, which="major", grid_transform=ccrs.PlateCarree(), zorder=1000)
    # ax.set_yticks(crs=ccrs.PlateCarree())
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
    # ax.add_feature(cfeature.BORDERS, lw=0.2, alpha=0.6)

    # ax.legend(loc="upper left")
    gl = ax.gridlines(
        draw_labels=True,
        dms=True, x_inline=False, y_inline=False,
        xlocs=loc,
        ylocs=loc,
    )
    label_style = dict(color='gray', size="large")
    gl.xlines = False
    gl.ylines = False
    gl.right_labels = False  # because of colorbar
    gl.xlabel_style = label_style
    gl.ylabel_style = label_style

    # ax.set_xticks(ax.get_xticks(), [])
    # Add additional locations
    # Sulu, Savu, Lifamatola, Dewakang Sill
    x_locs, y_locs = (
        [121, 122.1, 126.9, 118.5, 118],
        [6, -10, -1.74, -5.7, -1.2]
    )
    points = {
        "Su": (1.6, 0.7),
        # "B": (1.4, 0),
        "Sa": (0.5, -1.9),
        "L": (1, 1.6),
        "D": (0, 1.3),
        "Ma": (-2.2, 0.5)

    }
    color = "tab:orange"
    ax.scatter(
        x_locs,
        y_locs,
        marker="^",
        color=color,
        edgecolors="k",
        zorder=1000
    )
    for i, pt in enumerate(points):
        txt = ax.text(
            x_locs[i] + points[pt][0],
            y_locs[i] + points[pt][1],
            pt,
            ha="center",
            va="center",
            color=color,
            size="large",
            fontfamily="serif",
            fontstretch="extra-expanded",
            transform=ccrs.PlateCarree(),
            )
        txt.set_path_effects(
            [
                path_effects.Stroke(
                    linewidth=1.4,
                    foreground="k"
                ),
                path_effects.Normal()
            ]
        )

#%%
    fig.savefig(
        paths.figures_path / "fig01_bathymetry_map.png",
        dpi=300,
        transparent=True
    )
    print("done")
# %%

#%%
