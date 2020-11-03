import geopandas as gpd
from shapely import geometry as sg
import requests
import os
from requests.auth import HTTPBasicAuth
import time

def paginate(session, url):
    page_url = url
    page = session.get(page_url).json()
    
    return page

def get_scenes_per_quad(quad, session):
    url = quad["_links"]["items"]
    result = session.get(url)
    scenes = result.json()

    return scenes["items"]

def get_quads(url, payload, session):
    
    result = session.get(url, params=payload)
    page = result.json()

    if result.status_code < 299:
        quads = page["items"]
        while "_next" in page["_links"]:
            page = paginate(session, page["_links"].get("_next"))
            quads += page["items"]
    else:
        quads = result

    return quads

def download_quads(quads, mosaic, session):
    
    mosaic_path = os.getcwd() + '/' + mosaic
    if not os.path.exists(mosaic_path):
        os.mkdir(mosaic_path)

    for quad in quads:
        location = quad["_links"]["download"]
        quad_id = quad["id"]
        quad_file = mosaic_path + '/' + quad_id + ".tif"

        if not os.path.isfile(quad_file):
            worked = False
            while not worked:
                try:
                    download = session.get(location)
                    worked = True

                    f = open(quad_file, "wb")
                    output.add_msg(f'Downloading mosaic quad {quad_file}')
                    for chunk in download.iter_content(chunk_size=512 * 1024):
                        # filter out keep-alive new chunks
                        if chunk:
                            f.write(chunk)
                    f.close()
                    output.add_msg(f'{mosaic} quad ID {quad_id} saved.')
                except:
                    output.add_msg('Connection refused by the server..', 'warning')
                    time.sleep(5)
                    output.add_msg('Was a nice sleep, now let me continue...', 'warning')
                    continue
        else:
            output.add_msg(f'{mosaic} quad ID {quad_id} exists.')


def get_error(code, **kwargs):

    error_codes = {
        "e1": "There seem to be an error with your API access, please check your API key.",
        "e2": "Error finding your mosaics, try checking that you used the correct mosaic name.",
        "e3": "There was an error with your geometry, please check the GeoJSON file.",
        "e4": f"Error {kwargs["quads"].status_code}: {kwargs["quads"].reason}, {kwargs["quads"].text.split("<p>")[1][:-5]} \nProcess terminated"
    }

    return error_codes[code]

def run_download(planet_api_key, basemaps_url, aoi_io, output):
    
    #authenticate to planet
    command = [
        'curl', '-L', '-H',
        f"Authorization: api-key {planet_api_key}",
        basemaps_url
    ]
    os.system(' '.join(command))
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(planet_api_key, '')
    response = session.get(basemaps_url, params={'_page_size': 1000})

    output.add_msg(str(response))
    
    # Getting mosaics metadata
    orders = response.json()["mosaics"]
    if len(orders) == 0:
        output.add_msg(get_error("e1"), 'error')
        return
        
    
    output.reset()
    for order in range(len(orders)):
        output.append_msg(orders[order]["name"])
    
    #maybe insert number as a variable in the interface    
    mosaic_name = orders[0]["name"]
    
    mosaics_df = json_normalize(orders)

    if mosaic_name in mosaics_df.name.values:
        mosaic_id = mosaics_df.loc[mosaics_df["name"] == mosaic_name]["id"].values
        mosaic_url = basemaps_url + mosaic_id[0]

        # Parsing bounding box
        try:
            geom = getbbox(geojson_geometry)
        except Exception as e:
            output.add_msg(get_error("e3"), 'error')
            return

        # Getting the quads
        quads_url = mosaic_url + '/quads'
        payload = {"_page_size": 1000, 'bbox': ', '.join(po_aoi_io.get_bounds())}

        quads = get_quads(quads_url, payload, session)

        if isinstance(quads, list):
            output.add_msg(f"***Preparing the download of {len(quads)} quads for mosaic {mosaic_name}***")
            download_quads(quads, mosaic_name, session)
        else
            output.add_msg(get_error("e4", quads=quads), 'error')
            
    return
            
            
def get_sum_up(po_aoi_io):
    
    bb = po_aoi_io.get_bounds()
    sg_bb = sg.box(bb)
    
    gdf = gdp.GeoDataframe(crs="EPSG:4326", geometry = [sg_bb]).to_crs('ESRI:54009')
    surface = gdf.area
    
    msg = f"You're about to launch a downloading on a surface of {surface} Km\u00B2"
    
    return msg

# This is some crap that might be useful at some point...

# API request object
#search_request = {
#  #"interval": "day",
#  #"id": [mosaic_id],
#  #"item_types": ["PSScene4Band"],
#  "bbox":[ -51.416015625, -8.390865416667355, -50.987548828125, -7.966757602932168 ],
#  "coordinate_system": "EPSG:3857",
#  "first_acquired": "2018-12-01T00:00:00.000Z",
#  "last_acquired": "2019-06-01T00:00:00.000Z",
#  "name": "basemap_test",
#  "product_type": "basemap"
# #"filter": combined_filter
#}

# fire off the POST request
#search_result = \
#  requests.post(
#    'https://api.planet.com/basemaps/v1/mosaics',
#    auth=HTTPBasicAuth(PLANET_API_KEY, ''),
#    json=search_request)
#
#print(json.dumps(search_result.json(), indent=1))