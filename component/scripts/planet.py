# this file will be used as a singleton object in the explorer tile

import time
import requests
from types import SimpleNamespace
import re
from datetime import datetime

from planet import api
from ipyleaflet import TileLayer

from component.message import cm
from component import parameter as cp

planet = SimpleNamespace()

# parameters
planet.url = "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"
planet.basemaps = "https://tiles.planet.com/basemaps/v1/planet-tiles/{mosaic_name}/gmap/{{z}}/{{x}}/{{y}}.png?api_key={key}"
planet.attribution = "Imagery © Planet Labs Inc."

# attributes

planet.valid = False
planet.key = None
planet.client = None

# create the regex to match the different know planet datasets
VISUAL = re.compile("^planet_medres_visual_")  # will be removed from the selection
ANALYTIC = re.compile("^planet_medres_normalized_analytic_")
ANALYTIC_MONTHLY = re.compile(
    "^planet_medres_normalized_analytic_\d{4}-\d{2}_mosaic$"
)  # NICFI monthly
ANALYTIC_BIANUAL = re.compile(
    "^planet_medres_normalized_analytic_\d{4}-\d{2}_\d{4}-\d{2}_mosaic$"
)  # NICFI bianual


def mosaic_name(mosaic):
    """
    Give back the shorten name of the mosaic so that it can be displayed on the thumbnails
    Args:
        mosaic (str): the mosaic full name
    Return:
        (str, str): the type and the shorten name of the mosaic
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


def check_key():
    """raise an error if the key is not validataed"""

    if not planet.valid:
        raise Exception(cm.planet.key.invalid)

    return


def validate_key(key, out):
    """Validate the API key and save it the key variable"""

    out.add_msg(cm.planet.key.test)

    # get all the subscriptions
    resp = requests.get(planet.url, auth=(key, ""))
    subs = resp.json()

    # only continue if the resp was 200
    if resp.status_code != 200:
        raise Exception(subs["message"])

    # check the subscription validity
    # stop the execution if it's not the case
    planet.valid = any([True for sub in subs if sub["state"] == "active"])
    check_key()

    planet.key = key

    out.add_msg(cm.planet.key.valid, "success")

    return


def order_basemaps(key, out):
    """check the apy key and then order the basemap to update the select list"""

    # checking the key validity
    validate_key(key, out)

    out.add_msg(cm.planet.mosaic.load)

    # autheticate to planet
    planet.client = api.ClientV1(api_key=planet.key)

    # get the basemap names
    # to use when PLanet decide to update it's API, until then I manually retreive the mosaics
    # mosaics = planet.client.get_mosaics().get()['mosaics']
    url = planet.client._url("basemaps/v1/mosaics")
    mosaics = (
        planet.client._get(url, api.models.Mosaics, params={"_page_size": 1000})
        .get_body()
        .get()["mosaics"]
    )

    # filter the mosaics in 3 groups
    bianual, monthly, other, res = [], [], [], []
    for m in mosaics:
        name = m["name"]
        type_, short = mosaic_name(name)

        if type_ == "ANALYTIC_MONTHLY":
            monthly.append({"text": short, "value": name})
        elif type_ == "ANALYTIC_BIANUAL":
            bianual.append({"text": short, "value": name})
        elif type_ == "OTHER":
            monthly.append({"text": short, "value": name})

    # fill the results with the found mosaics
    if len(bianual):
        res += [{"header": "NICFI bianual"}] + bianual
    if len(monthly):
        res += [{"header": "NICFI monthly"}] + monthly
    if len(other):
        res += [{"header": "other"}] + other

    out.add_msg(cm.planet.mosaic.complete, "success")

    print(mosaics)

    return res


def display_basemap(mosaic_name, m, out, color):
    """display the planet mosaic basemap on the map"""

    out.add_msg(cm.map.tiles, loading=True)

    # set the color if necessary
    color_option = "" if color == "visual" else f"&proc={color}"

    # remove the existing layers with planet attribution
    for layer in m.layers:
        if layer.attribution == planet.attribution:
            m.remove_layer(layer)

    # use the visual basmap if available
    if ANALYTIC.match(mosaic_name) and not color_option:
        mosaic_name = mosaic_name.replace("normalized_analytic", "visual")

    # create a new Tile layer on the map
    layer = TileLayer(
        url=planet.basemaps.format(key=planet.key, mosaic_name=mosaic_name)
        + color_option,
        name="Planet© Mosaic",
        attribution=planet.attribution,
        show_loading=True,
    )

    # insert the mosaic bewteen CardoDB and the country border ie position 1
    # we have already removed the planet layers so I'm sure that nothing is in
    # The grid and the country are build before and if we are here I'm also sure that there are 3 layers in the map
    tmp_layers = list(m.layers)
    tmp_layers.insert(1, layer)
    m.layers = tuple(tmp_layers)

    return


def download_quads(aoi_name, mosaic_name, grid, out):
    """export each quad to the appropriate folder"""

    # a bool_variable to trigger a specifi error message when the mosaic cannot be downloaded
    view_only = False

    out.add_msg(cm.planet.down.start)

    # get the mosaic from the mosaic name
    mosaic = planet.client.get_mosaic_by_name(mosaic_name).get()["mosaics"][0]

    # construct the quad list
    quads = []
    for i, row in grid.iterrows():
        quads.append(f"{int(row.x):04d}-{int(row.y):04d}")

    # download the quads
    # create lists to display information to the user at the end
    skip = down = fail = 0
    for i, quad_id in enumerate(quads):

        # update the progress in advance
        out.update_progress(i / len(quads), cm.planet.down.progress)

        # check file existence
        res_dir = cp.get_mosaic_dir(aoi_name, mosaic_name)
        file = res_dir.joinpath(f"{quad_id}.tif")

        if file.is_file():
            out.append_msg(cm.planet.down.exist.format(quad_id))
            skip += 1
            time.sleep(0.3)
            continue

        # catch error relative of quad existence
        try:
            quad = planet.client.get_quad_by_id(mosaic, quad_id).get()
        except Exception as e:
            out.append_msg(cm.planet.down.not_found.format(quad_id))
            fail += 1
            time.sleep(0.3)
            continue

        out.append_msg(
            cm.planet.down.done.format(quad_id)
        )  # write first to make sure the message stays on screen

        # specific loop (yes it's ugly) to catch people that didn't use a key allowed to download the asked tiles
        try:
            planet.client.download_quad(quad).get_body().write(file)
        except Exception as e:
            out.append_msg(cm.planet.down.no_access)
            fail += 1
            view_only = True
            time.sleep(0.3)
            continue

        down += 1

    # adapt the color to the number of image effectively downloaded
    color = "success"
    if fail > 0.8 * len(quads):  # we missed nearly everything
        color = "error"
    elif fail > 0.5 * len(quads):  # we missed more than 50%
        color = "warning"

    out.add_msg(cm.planet.down.end.format(len(quads), down, skip, fail), color)
    if view_only:
        out.append_msg(cm.planet.down.view_only, type_=color)

    return
