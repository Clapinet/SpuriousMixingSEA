"""
Compute, plot and save mean T and S profiles (along depth) for each model
for each zone in a given set.
"""

from data.sources import DataSource

from utilities.paths import paths
from utilities.names import zone_names, get_simple_names
import utilities.units as units

from preprocessings.load_profiles import load_sims

from plotting.display import set_style
from plotting.misc import get_color_from_simulation_name

import matplotlib.pyplot as plt

# %% Define plotting parameters
PARAMS = dict(
    ZONE=(
        # "CEL"
        # "MAK"
        # "SCS"
        # "SULU"
        "NORDMOL"
        # "SUDMOL"
        # "WESTIND"
    ),
    SIMS=[
        "ARGO",
        "NT0",
        "NT1",
        "T0",
        "T1",
    ],
    REF_SIM="ARGO",
    FIG_LOC="papers/new_scheme"
)

# %% Load data

argo = load_sims(PARAMS["SIMS"])

#%%

argo_mean = argo.mean(["cycle"])
argo_std = argo.std(["cycle"])

# %% Plotting

set_style("paper")

# Define colors
prop_cycle = plt.rcParams["axes.prop_cycle"]
# colors = prop_cycle.by_key()["color"]  # TODO : do something better
colors = {
    "ARGO": "k",
    "NT0": "#ffab91",  # deep orange (2)
    # "NT0": "#ffccbc",  # deep orange (1)
    # "NT1": "#ff5722",
    "NT1": "#e64a19",  # deep orange (7)
    # "T0": "#cfd8dc",  # blue grey (1)
    "T0": "#90a4ae",
    "T1": "#607d8b",
}

# Get simplified names of simulations
# names = get_simple_names(PARAMS["SIMS"])

# x_lims
s_delta = 1.2
s_min = 33.75
s_max = s_delta + s_min
t_min = 7
t_max = 30

COL_WIDTH = 4
ROW_WIDTH = 4
MARKEVERY = 4
LW_SIM = 2.5
LW_REF = 3
COLOR_CYCLE_OFFSET = 2
LEGEND = True

# %%
N_ZONES = 1
N_SIMS = len(PARAMS["SIMS"])
N_ROWS = 1
N_COLS = 2
z_id = PARAMS["ZONE"]

fig, ax_s = plt.subplots(N_ROWS, N_COLS, figsize=(N_COLS * COL_WIDTH, N_ROWS * ROW_WIDTH))

ax_tem = ax_s[0]
ax_sal = ax_s[1]
# Get depth
dpt = argo_mean.depth.data
h_max = int(dpt.max())

for i, sim_id in enumerate(PARAMS['SIMS']):
    print(sim_id)
    # c = colors[(i + COLOR_CYCLE_OFFSET - 1) % len(colors)]
    c = colors[sim_id]

    marker = None
    # Set specific marker for simulation with tides
    if sim_id[0] == "N":
        marker = "^"
    elif sim_id[1] == "C":
        marker = "+"

    sub_ds = argo_mean.sel(zone=z_id, sim=sim_id)
    sal, tem = sub_ds.sal.data, sub_ds.tem.data

    if sim_id == PARAMS['REF_SIM']:
        # also plot number of floats kept
        ax_tem.plot(tem, - dpt, c="k", lw=LW_REF, label=f"{PARAMS['REF_SIM']}", marker=marker, markevery=MARKEVERY)
    else:
        ax_tem.plot(tem, - dpt, c=c, label=sim_id, lw=LW_SIM, marker=marker, markevery=MARKEVERY)

    if sim_id == PARAMS['REF_SIM']:
        # also plot number of floats kept
        ax_sal.plot(
            sal, - dpt, "-", c="k", lw=LW_REF, marker=marker, markevery=MARKEVERY
        )
    else:
        ax_sal.plot(sal, - dpt, "-", c=c, lw=LW_SIM, marker=marker, markevery=MARKEVERY)


# Format axes
ax_tem.set_xlabel(units.tem)
ax_tem.set_ylabel(units.dpt)
if LEGEND:
    ax_tem.legend(loc="center right", fontsize="large", )
ax_tem.yaxis.set_tick_params(which="both", right=False)
ax_tem.set_title("(a)", fontsize="x-large", fontweight="bold", loc="left")

ax_sal.set_xlabel(units.sal)
# ax_sal.set_yticks(ax_tem.get_yticks(), [])
ax_sal.yaxis.set_tick_params(which="both", left=False, right=True)
ax_sal.set_yticklabels([])
ax_sal.set_title("(b)", fontsize="x-large", fontweight="bold", loc="left")

ax_sal.set_xlim(s_min, s_max)
ax_tem.set_xlim(t_min, t_max)

for ax in ax_s:
    ax.set_ylim(0, 500)
    ax.invert_yaxis()
    ax.xaxis.set_tick_params(which="both", top=True)


# ax.grid()
# TITLE
# fig.suptitle(zone_names[z_id], fontsize="large", fontweight="black")
ax_tem.text(9, 60, zone_names[z_id], fontsize="large")  # fontweight="black")
plt.tight_layout()


#%%
fig.savefig(
    paths.figures_path / f"fig03_mean_profiles_molucca.png",
    dpi=300,
    transparent=False
)

# %%

#%%
