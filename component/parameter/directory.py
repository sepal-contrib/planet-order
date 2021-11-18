from pathlib import Path

# module directory
module_dir = Path("~", "module_results").expanduser()
module_dir.mkdir(exist_ok=True)

# result_dir
result_dir = module_dir.joinpath("planet-order")
result_dir.mkdir(exist_ok=True)


def get_aoi_dir(aoi_name):
    """get the result dir associated with the aoi name"""

    aoi_dir = result_dir.joinpath(aoi_name)
    aoi_dir.mkdir(exist_ok=True)

    return aoi_dir


def get_mosaic_dir(aoi_name, mosaic_name):
    """get the result dir associated with the mosaic name"""

    aoi_dir = get_aoi_dir(aoi_name)
    mosaic_dir = aoi_dir.joinpath(mosaic_name)
    mosaic_dir.mkdir(exist_ok=True)

    return mosaic_dir
