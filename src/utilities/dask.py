from utilities.paths import paths

from dask import distributed
from dask.distributed import Client, LocalCluster

try:
    import dask_jobqueue
except ModuleNotFoundError:
    pass


def _slurm_cluster(
    cluster_name="my_cluster",
    client_name="my_client",
    walltime="00:30:00",
    n_scale=1,
    **kwargs
):
    # Cluster with default jobqueue parameters
    cluster = dask_jobqueue.SLURMCluster(
        name=cluster_name,
        walltime=walltime,
        local_directory=paths.logs_path,
        **kwargs
    )
    cluster.scale(n=n_scale)

    # Client
    client = distributed.Client(cluster, name=client_name)
    return cluster, client


def _local_cluster(
    n_workers=3,
    threads_per_worker=2,
    cluster_name="my_cluster",
    client_name="my_client",
    **kwargs
):
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        local_directory=paths.logs_path,
        name=cluster_name,
        **kwargs
    )
    client = Client(cluster, name=client_name)
    return cluster, client


def init_dask_cluster(
        cluster_type: str = "SLURM",
        n_workers: int = 3,
        threads_per_worker: int = 2,
        display_link: bool = True,
        cluster_name: str = "my_cluster",
        client_name: str = "my_client",
        walltime: str = "00:30:00",
        n_scale: int = 1,
        **kwargs
):
    """

    Parameters
    ----------
    threads_per_worker: int
    n_workers:      int
    cluster_name:   str
                    Cluster name.
    cluster_type:   str
                    Type of cluster to instantiate. "SLURM" or "Local" for now.
    client_name:    str
                    Client name.
    display_link:   bool, default: True
                    Whether to display link to dashboard client or not.
    walltime:       str
                    Lifetime of cluster.
    n_scale:        int
                    Number of time to scale cluster.
    kwargs:         dict
                    Kwargs to pass to cluster.
    Returns
    -------
    cluster

    client

    """
    if cluster_type.lower() == "slurm":
        cluster, client = _slurm_cluster(
            cluster_name=cluster_name,
            client_name=client_name,
            walltime=walltime,
            n_scale=n_scale,
            **kwargs
        )
    elif cluster_type.lower() == "local":
        cluster, client = _local_cluster(
            n_workers=n_workers,
            threads_per_worker=threads_per_worker,
            cluster_name=cluster_name,
            client_name=client_name,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown cluster type : {cluster_type}.")

    if display_link:
        print("=> Client dashboard :", client.dashboard_link)

    return cluster, client
