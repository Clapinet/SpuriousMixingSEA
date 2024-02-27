from typing import Iterable, List

import yaml

from utilities.paths import paths


def get_real_names(full_names: Iterable[str]) -> List[str]:
    """
    """
    with open(paths.config_path / "data_sources" / "simulation_full_names.yml", 'r') as f:
        dic = yaml.safe_load(f)

    return [dic[name] for name in full_names]


zone_names = {
    "SCS": "South China Sea",
    "SULU": "Sulu Sea",
    "MAK": "Makassar Strait",
    "CEL": "Celebes Sea",
    "NORDMOL": "Molucca Sea",
    "SUDMOL": "Banda Sea",
    "WESTIND": "Eastern Indian",
}

zone_names_with_break = {
    "SCS": "South China\nSea",
    "SULU": "Sulu\nSea",
    "MAK": "Makassar\nStrait",
    "CEL": "Celebes\nSea",
    "NORDMOL": "Molucca\nSea",
    "SUDMOL": "Banda\nSea",
    "WESTIND": "Eastern\nIndian",
}

sim_names = {
    "GLORYS": "GLORYS",
    "argo": "ARGO",
    "ARGO": "ARGO",
    "NTNW": "NT1",
    "COP": "GLORYS",
    "rat0_NT": "NT0",
    "ndrat0.0": "T0",
    "ndh1v1_vqsfile_quikest2": "T1",
}


def get_simple_names(names_list):
    return [sim_names[name] for name in names_list]

#%%
