import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from utilities.paths import paths


def set_style(file_name="masterthesisstyle", right_ticks=True, top_ticks=True):
    if file_name[-4:] != ".yml":
        name = file_name + ".yml"
    else:
        name = file_name
    plt.style.use(paths.styles_path / name)
    plt.rcParams["ytick.right"] = right_ticks
    plt.rcParams["xtick.top"] = top_ticks


def format_time_axis(axis, time_series, mjrfmt="%Y", mnrfmt="", month_interval=1):
    """
    """
    # ## Plotting
    # year formatting
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator(interval=month_interval)  # every month
    mjrFmt = mdates.DateFormatter(mjrfmt)
    mnrFmt = mdates.DateFormatter(mnrfmt)

    # format the ticks
    axis.xaxis.set_major_locator(years)
    axis.xaxis.set_major_formatter(mjrFmt)
    axis.xaxis.set_minor_locator(months)
    axis.xaxis.set_minor_formatter(mnrFmt)

    datemin = time_series.min()
    datemax = time_series.max()
    # axis.set_xlim(datemin, datemax)

#%%
