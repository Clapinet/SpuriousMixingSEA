import matplotlib.patches as mpatches

import numpy as np
import xarray as xr

from data.sources import DataSource

from utilities.paths import paths
from utilities.names import sim_names, zone_names, get_simple_names, zone_names_with_break
from utilities.argo import get_weights_from_std
from utilities.metrics import my_metrics
import utilities.units as units
from preprocessings.load_profiles import load_sims

from plotting.display import set_style

import matplotlib.pyplot as plt

from plotting.misc import material


# %% Define parameters
if __name__ == "__main__":

    PARAMS = dict(
        ZONES=[
            # "NORDPAC",
            # "SUDPAC",
            "CEL",
            "SCS",
            "SULU",
            "MAK",
            "NORDMOL",
            "SUDMOL",
            "WESTIND",
        ],

        SIMS=[
            "ARGO",
            "NT0",
            "NT1",
            "T0",
            # "T0.5",
            # "T0.9",
            "T1",
            # "T1.05",
            # "T1.1",
            # "T1.15",
            # "T1.2",
            # "T1.3"
        ],

        VAR="sal",
        REF_SIM="ARGO",
        WEIGHTS="uniform",  # uniform or std
        METRIC="diff_std",
        FIG_LOC="papers/new_scheme",
        MIN_DEPTH=-50,
        MAX_DEPTH=-500,
    )


# %% Load data

    argo = load_sims(PARAMS["SIMS"])

#%%

    argo_mean = argo.mean(["cycle"])
    argo_std = argo.std(["cycle"])
# %% Reduce data

    # argo = argo[PARAMS['VAR']]
    argo_mean = argo_mean[PARAMS['VAR']].sel(depth=slice(PARAMS["MAX_DEPTH"], PARAMS["MIN_DEPTH"]))
    argo_std = argo_std[PARAMS['VAR']].sel(depth=slice(PARAMS["MAX_DEPTH"], PARAMS["MIN_DEPTH"]))


# %% Compute weights

    if PARAMS["WEIGHTS"] == "std":
        weights = get_weights_from_std(argo_std.sel(sim=PARAMS["REF_SIM"]), dim="depth")
    elif PARAMS["WEIGHTS"] == "uniform":
        weights = xr.ones_like(argo_std.sel(sim=PARAMS["REF_SIM"]))
    else:
        raise ValueError(f"Weights option <{PARAMS ['WEIGHTS']}> unknown.")

# %% Compute values
    data_to_plot = []

    for zone in PARAMS["ZONES"]:

        metrics = []
        for sim in PARAMS["SIMS"][1:]:

            # Compute metric
            d1 = argo_mean.sel(zone=zone, sim=sim)
            d2 = argo_mean.sel(zone=zone, sim=PARAMS["REF_SIM"])
            w = weights.sel(zone=zone)

            metric = my_metrics[PARAMS['METRIC']](d1, d2, w, dim="depth").values
            # Save metric
            metrics.append(metric)

        # Save metrics
        data_to_plot.append(metrics)

    data_to_plot = np.array(data_to_plot)


# %% Plot
    set_style("paper")

    N_ZONES = len(PARAMS["ZONES"])
    N_SIMS = len(PARAMS["SIMS"])
    N_LINES = N_ZONES // 3

    fig, ax = plt.subplots(figsize=(N_ZONES * 2, 4))  # frameon = False -> remove borders


    def color_choice(i):
        if N_SIMS > 5:
            return i
        else:
            return 2 * i + 1


    def bars(data, origin, colors, label, ax=ax, **label_kw):
        """
        Main plotting function, to plot group of bars with x-label.

        Taken from : https://github.com/rougier/scientific-visualization-book/tree/master

        Parameters
        ----------
        data: y-values to plot
        origin: where to start plotting group of bars on x axis
        color: name of color group to use
        label: name of the group, to plot below
        color_palette: dict matching color names and shades

        """
        n = len(data)

        # Define locations where to plot y values
        x = origin + np.arange(n)

        # Plot data
        bar = ax.bar(
            x,
            data,
            width=1.0,
            align="edge",
            color=colors,
            edgecolor="black",
            linewidth=0.3
        )
        line_offset = 0.5
        ax.plot([origin - line_offset, origin + n + line_offset], [0, 0], color="black", lw=2.5)
        ax.text(origin + n / 2, -0.015, label, va="center", ha="center", fontsize='xx-large', **label_kw)


    COLORS = ['red', 'pink', 'purple', 'deep purple',
               'indigo',
               'blue',
               'light blue',
               'cyan',
               'teal',
               'green',
               'light green',
               'lime',
               'yellow',
               'amber',
               'orange',
               'deep orange',
               'brown',
               'grey',
               'blue grey'
    ]

    OFFSET = 0.0
    color_tide = "blue grey"
    color_no_tide = "deep orange"
    for i, z in enumerate(PARAMS['ZONES']):
        bars(data_to_plot[i], i * (N_SIMS + OFFSET),
             # COLORS[i],
             # "blue",
             [material[color_no_tide][1], material[color_no_tide][5], material[color_tide][1], material[color_tide][5]],
             zone_names_with_break[z],
             )

    # Add mean
    ## Color half plane
    ax.axvline(N_ZONES * (N_SIMS + OFFSET) - 0.5, ls="--", lw=0.5, c="k")
    Y_MAX = 0.12
    half_plane = [N_ZONES * (N_SIMS + OFFSET) - 0.5, (N_ZONES + 1) * (N_SIMS + OFFSET) - 0.5]
    ax.fill_between(half_plane, Y_MAX, color='grey', alpha=0.1)

    ## Add data
    bars(data_to_plot.mean(axis=0), (len(PARAMS["ZONES"])) * (N_SIMS + OFFSET),
         # COLORS[i],
         # "blue",
         [material[color_no_tide][1], material[color_no_tide][5], material[color_tide][1], material[color_tide][5]],
         "Average",
         fontweight="semibold",
         )

    ax.bar_label(
        ax.containers[0], labels=PARAMS["SIMS"][1:],
        fontsize="xx-large",
        rotation=90,
        label_type="edge",
        padding=10
    )

    ax.set_xlim(left=-0.5, right=(len(PARAMS["ZONES"]) + 1) * (N_SIMS + OFFSET) - 0.5)
    ax.set_xticks([])
    # ax.spines.right.set_visible(False)
    # ax.spines.top.set_visible(False)
    ax.spines.bottom.set_visible(False)

    # Y axis
    y_min = 0.0
    ax.set_yticks([0.0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12], size='x-small')
    ax.spines.left.set_bounds(0.0, Y_MAX)
    ax.set_ylim(0.0, Y_MAX)
    ax.yaxis.set_ticks_position("left")

    ax.tick_params(which="minor", axis='y', width=0)
    ax.tick_params(axis='y', which='major', length=3, direction="out")
    ax.set_ylabel(
        # f"{'w' if PARAMS['WEIGHTS'] == 'std' else ''}{PARAMS['METRIC'].upper()}  ",
        "wRMSE [psu]",
        fontsize="xx-large"
        # fontweight="semibold"
    )

    title = f"fig05_metric_all_zones.png"
    print("Saving", title)

#%%
    fig.savefig(
        paths.figures_path / title,
        dpi=300
    )

#%%

#%%
