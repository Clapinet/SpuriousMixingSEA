from dataclasses import dataclass

from pathlib import Path


# PROJECT
# =======
# path of the project

@dataclass
class MyPaths:
    project_path: Path = Path(__file__).parent.parent.parent

    # where to find source code
    source_path: Path = project_path / "src"

    # where to save figures
    figures_path: Path = project_path / "figures"

    # where to put logs
    logs_path: Path = project_path / "logs"

    #
    config_path: Path = project_path / "conf"

    # Directory with data to work with
    work_data_path: Path = Path("/home/garinet/data")

    # Data paths by level of processing
    raw_data_path: Path = work_data_path / "01_raw"
    intermediate_data_path: Path = work_data_path / "02_intermediate"
    primary_data_path: Path = work_data_path / "03_primary"

    # Misc
    # ----
    styles_path: Path = source_path / "plotting" / "styles"

    grids_path: Path = raw_data_path / "GRIDS"

    def __getattr__(self, item):
        # getattr is : "__getattr__ is an extra hook to access
        # attributes that don't exist, and would otherwise raise AttributeError"
        # => Therefore, no need to write standard case
        return super().__getattribute__(item + "_path")


# Simplify use
paths = MyPaths()
# super_paths = MyPaths
