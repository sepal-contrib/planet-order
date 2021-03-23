from pathlib import Path
import json
from zipfile import ZipFile
import requests
from requests.auth import HTTPBasicAuth
import os
import time

import geopandas as gpd
from shapely import geometry as sg
import pandas as pd
import geemap
import ipyvuetify as v
import numpy as np
import ee 

ee.Initialize()

from component import parameter as cp

def paginate(session, url):
    return session.get(url).json()

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

def download_quads(quads, mosaic, session, aoi_name, output):
    
    mosaic_path = cp.get_result_dir(aoi_name).joinpath(mosaic)
    mosaic_path.mkdir(exist_ok=True)

    for quad in quads:
        location = quad["_links"]["download"]
        quad_id = quad["id"]
        quad_file = mosaic_path.joinpath(f'{quad_id}.tif')

        if not quad_file.is_file():
            worked = False
            while not worked:
                try:
                    download = session.get(location)
                    with quad_file.open('wb') as f:
                        output.add_msg(f'Downloading mosaic quad {quad_file}')
                        for chunk in download.iter_content(chunk_size=512 * 1024):
                            # filter out keep-alive new chunks
                            if chunk:
                                f.write(chunk)
                    output.add_msg(f'{mosaic} quad ID {quad_id} saved.')
                    
                    worked = True
                except:
                    output.add_msg('Connection refused by the server..', 'warning')
                    time.sleep(5)
                    output.add_msg('Was a nice sleep, now let me continue...', 'warning')
                    continue
        else:
            output.add_msg(f'{mosaic} quad ID {quad_id} exists.')
    
    output.add_msg(f"The result are now available in the following folder : {mosaic_path}/", "success")
    
    return mosaic_path

def get_error(code, **kwargs):

    error_codes = {
        "e1": "There seem to be an error with your API access, please check your API key.",
        "e2": "Error finding your mosaics, try checking that you used the correct mosaic name.",
        "e3": "There was an error with your geometry, please check the GeoJSON file.",
        "e4": f"Error {kwargs['quads'].status_code}: {kwargs['quads'].reason}, {kwargs['quads'].text.split('<p>')[1][:-5]} \nProcess terminated"
    }

    return error_codes[code]

def get_orders(planet_api_key, basemaps_url, output):
    
    # authenticate to planet
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
        raise Excception(get_error("e1"))
        
    return orders, session

def get_grid(quads, aoi_io, m, output):
    
    df = pd.json_normalize(quads)
    geometry = [sg.box(*row.bbox) for i, row in df.iterrows()]
    gdf = gpd.GeoDataFrame(df.filter(['id']), geometry=geometry, crs="EPSG:4326")
    
    grid_path = cp.get_result_dir(aoi_io.get_aoi_name()).joinpath(f'{aoi_io.get_aoi_name()}_planet_grid.shp')
    gdf.to_file(grid_path)
    
    # display on map 
    json_df = json.loads(gdf.to_json())
    ee_df = geemap.geojson_to_ee(json_df)
    
    m.addLayer(ee_df, {'color': v.theme.themes.dark.accent}, 'grid')
    m.zoom_ee_object(ee_df.geometry())
    
    output.add_live_msg(f'The grid have been created and is available at {grid_path}', 'success')
    
    return grid_path
    
def run_download(planet_api_key, basemaps_url, aoi_io, order_io, m, output):
    
    # get the orders 
    orders = order_io.orders
    session = order_io.session
    
    # maybe insert number as a variable in the interface    
    mosaic_name = orders[order_io.order_index]["name"]
    
    mosaics_df = pd.json_normalize(orders)

    if mosaic_name in mosaics_df.name.values:
        mosaic_id = mosaics_df.loc[mosaics_df["name"] == mosaic_name]["id"].values
        mosaic_url = basemaps_url + mosaic_id[0]

        # Getting the quads
        quads_url = mosaic_url + '/quads'
        payload = {"_page_size": 1000, 'bbox': ', '.join(str(x) for x in aoi_io.get_bounds(aoi_io.get_aoi_ee()))}

        quads = get_quads(quads_url, payload, session)

        if isinstance(quads, list):
            
            grid_path = get_grid(quads, aoi_io, m, output)
            
            output.add_msg(f"Preparing the download of {len(quads)} quads for mosaic {mosaic_name}")
            mosaic_path = download_quads(quads, mosaic_name, session, aoi_io.get_aoi_name(), output)
            
        else:
            raise Exception(get_error("e4", quads=quads))
    
    return (mosaic_path, grid_path)
    
def get_sum_up(aoi_io):
    
    min_lon, min_lat, max_lon, max_lat = aoi_io.get_bounds(aoi_io.get_aoi_ee())
    sg_bb = sg.box(min_lon, min_lat, max_lon, max_lat)
    
    gdf = gpd.GeoDataFrame(crs="EPSG:4326", geometry = [sg_bb]).to_crs('ESRI:54009')
    minx, miny, maxx, maxy = gdf.total_bounds
    surface = (maxx-minx)*(maxy-miny)/10e6 #in km2
    
    msg = f"You're about to launch a downloading on a surface of {surface:.2f} Km\u00B2"
    
    return msg

def get_theorical_grid(aoi_io, m, output):
    """get the theorical grid on the selected aoi"""
    
    # get the aoi as a shapefile 
    aoi_json = geemap.ee_to_geojson(aoi_io.get_aoi_ee())
    gdf = gpd.GeoDataFrame.from_features(aoi_json).set_crs('EPSG:4326').to_crs('EPSG:3857')
        
    min_lon_aoi, min_lat_aoi, max_lon_aoi, max_lat_aoi = gdf.total_bounds
    
    # bounds of the world in 3857
    min_lon = -20026376.39 
    max_lon = 20026376.39
    min_lat = -20048966.10
    max_lat = 20048966.10

    # size of each cell for zoom 15
    size = 4.77 * 4096

    # compute latitude and longitude 
    longitudes = np.arange(min_lon, max_lon, size)
    latitudes = np.arange(min_lat, max_lat, size)

    # create the grid geometry data  
    data = {'id':[],'geometry':[]}
    for i, x in enumerate(longitudes):
        for j, y in enumerate(latitudes):
        
            # identify if the point is inside the total bounds 
            inside_lon = (x + size > min_lon_aoi) and (x < max_lon_aoi)
            inside_lat = (y + size > min_lat_aoi) and (y < max_lat_aoi)
            
            # add the geometry
            if inside_lon and inside_lat:
                data['id'].append(f'{i}-{j}')
                data['geometry'].append(sg.box(x, y, x + size, y + size))
                        
    
    # create and clip the grid over the country geometry
    grid = gpd.GeoDataFrame(data, crs='EPSG:3857')  
    grid = gpd.clip(grid, gdf)
    grid = grid.to_crs('EPSG:4326')
            
    # save the file
    grid_path = cp.get_result_dir(aoi_io.get_aoi_name()).joinpath(f'{aoi_io.get_aoi_name()}_grid.shp')
    grid.to_file(grid_path)
            
    # display on map 
    json_df = json.loads(grid.to_json())
    ee_df = geemap.geojson_to_ee(json_df)
    
    m.addLayer(ee_df, {'color': v.theme.themes.dark.warning}, 'theorical grid')
    m.zoom_ee_object(ee_df.geometry())
    
    output.add_live_msg(f'The grid have been created and is available at {grid_path}', 'success')
            
    return grid_path
            