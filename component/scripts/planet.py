"""this file will be used as a singleton object in the explorer tile."""

import re
from datetime import datetime

import requests
from geopandas import GeoDataFrame
from sepal_ui import sepalwidgets as sw
from sepal_ui.aoi import AoiModel
from sepal_ui.planetapi import PlanetModel
from sepal_ui.scripts import utils as su

from component import model as cmod
from component import parameter as cp
from component.message import cm

# create the regex to match the different know planet datasets
VISUAL = re.compile("^planet_medres_visual_")  # will be removed from the selection
ANALYTIC = re.compile("^planet_medres_normalized_analytic_")
ANALYTIC_MONTHLY = re.compile(
    "^planet_medres_normalized_analytic_\\d{4}-\\d{2}_mosaic$"
)  # NICFI monthly
ANALYTIC_BIANUAL = re.compile(
    "^planet_medres_normalized_analytic_\\d{4}-\\d{2}_\\d{4}-\\d{2}_mosaic$"
)  # NICFI bianual


def mosaic_name(mosaic: str) -> tuple[str, str]:
    """Give back the shorten name of the mosaic so that it can be displayed on the thumbnails.

    Args:
        mosaic (str): the mosaic full name
    Return:
        (str, str): the type and the shorten name of the mosaic.
    """
    if ANALYTIC_MONTHLY.match(mosaic):
        year = mosaic[34:38]
        start = datetime.strptime(mosaic[39:41], "%m").strftime("%b")
        res = f"{start} {year}"
        type_ = "ANALYTIC_MONTHLY"
    elif ANALYTIC_BIANUAL.match(mosaic):
        year = mosaic[34:38]
        start = datetime.strptime(mosaic[39:41], "%m").strftime("%b")
        end = datetime.strptime(mosaic[47:49], "%m").strftime("%b")
        res = f"{start}-{end} {year}"
        type_ = "ANALYTIC_BIANUAL"
    elif VISUAL.match(mosaic):
        res = None  # ignored in this module
        type_ = "VISUAL"
    else:
        res = mosaic[:15]  # not optimal but that's the max
        type_ = "OTHER"

    return type_, res


def order_basemaps(mosaics: dict) -> list[dict[str, str]]:
    """create a list of items for the dynamic selector"""

    # get the basemap names
    mosaics_names = [m["name"] for m in mosaics]

    # filter the mosaics in 3 groups
    bianual, monthly, other, res = [], [], [], []
    for m in mosaics_names:
        type_, short = mosaic_name(m)

        if type_ == "ANALYTIC_MONTHLY":
            monthly.append({"text": short, "value": m})
        elif type_ == "ANALYTIC_BIANUAL":
            bianual.append({"text": short, "value": m})
        elif type_ == "OTHER":
            monthly.append({"text": short, "value": m})

    # fill the results with the found mosaics
    if len(bianual):
        res += [{"header": "NICFI bianual"}] + bianual
    if len(monthly):
        res += [{"header": "NICFI monthly"}] + monthly
    if len(other):
        res += [{"header": "other"}] + other

    return res


def get_url(planet_model: PlanetModel, order_model: cmod.OrderModel) -> str:
    """retreive a fully defined mosaic url"""

    color = f"&proc={order_model.color}"

    mosaics = planet_model.get_mosaics()
    url = next(m["_links"]["tiles"] for m in mosaics if m["name"] == order_model.mosaic)

    return url + color


def download_quads(
    aoi_model: AoiModel,
    planet_model: PlanetModel,
    order_model: cmod.OrderModel,
    grid: GeoDataFrame,
    alert: sw.Alert,
) -> None:
    """Export each quad to the appropriate folder."""

    alert.add_msg(cm.planet.down.start)

    # get the mosaic from the mosaic name
    mosaics = planet_model.get_mosaics()
    mosaic = next(m for m in mosaics if m["name"] == order_model.mosaic)

    # construct the quad list
    quads = []
    for i, row in grid.iterrows():
        quads.append(f"{int(row.x):04d}-{int(row.y):04d}")

    # download the quads
    # create lists to display information to the user at the end
    skip = down = fail = 0
    total = len(quads)
    alert.update_progress(0, cm.planet.down.progress, total=total)
    for i, quad_id in enumerate(quads):

        # update the progress in advance
        alert.update_progress(i, total=total)

        # check file existence
        mosaic_str = su.normalize_str(mosaic_name(order_model.mosaic)[1])
        res_dir = cp.get_mosaic_dir(aoi_model.name, mosaic_str)
        file = res_dir / f"{quad_id}.tif"

        if file.is_file():
            skip += 1
            continue

        # catch error relative of quad existence
        try:
            quad = planet_model.get_quad(mosaic, quad_id)
        except Exception:
            fail += 1
            continue

        # download to file
        r = requests.get(quad["_links"]["download"])
        file.write_bytes(r.content)

        down += 1

    # adapt the color to the number of image effectively downloaded
    color = "success"
    if fail > 0.8 * len(quads):  # we missed nearly everything
        color = "error"
    elif fail > 0.5 * len(quads):  # we missed more than 50%
        color = "warning"

    alert.add_msg(cm.planet.down.end.format(len(quads), down, skip, fail), color)

    return
