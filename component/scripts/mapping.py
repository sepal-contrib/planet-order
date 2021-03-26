import json 

import ee
from shapely import geometry as sg
from shapely.ops import unary_union
import geopandas as gpd
import ipyvuetify as v
import geemap
import numpy as np

from component import parameter as cp
from component.message import cm

ee.Initialize()

from component.message import cm

def display_on_map(m, aoi_io, out):
    """display the aoi on the map"""
    
    out.add_msg(cm.map.aoi)
    
    aoi = aoi_io.get_aoi_ee()
    empty = ee.Image().byte()
    outline = empty.paint(**{'featureCollection': aoi, 'color': 1, 'width': 3})
    m.addLayer(outline, {'palette': v.theme.themes.dark.secondary}, 'AOI borders')
    m.zoom_ee_object(aoi.geometry())
    
    return 

def set_grid(aoi_io, m, out):
    """create a grid adapted to the aoi and to the planet initial grid"""
    
    out.add_msg(cm.map.grid)
    
    # chec the grid filename 
    aoi_name = aoi_io.get_aoi_name()
    grid_file = cp.get_aoi_dir(aoi_name).joinpath(f'{aoi_name}_grid.geojson')
    
    # read the grid if possible
    if grid_file.is_file():
        grid_gdf = gpd.read_file(grid_file)
    
    # generate the grid
    else:
    
        # get the shape of the aoi in EPSG:4326 proj 
        aoi_json = geemap.ee_to_geojson(aoi_io.get_aoi_ee())
        aoi_shp = unary_union([sg.shape(feat['geometry']) for feat in aoi_json['features']])
        aoi_gdf = gpd.GeoDataFrame({'geometry': [aoi_shp]}, crs="EPSG:4326")
    
        # retreive the bb 
        aoi_bb = sg.box(*aoi_gdf.total_bounds)
    
        # create a dataframe that only use the grid cells that are intersecting the bb of the aoi_gdf
        with cp.planet_grid.open() as f:
    
            features = []
        
            # jump over the first line
            next(f)
        
            # read each line of the file
            for line in f:
        
                # split the line 
                tmp = line.strip().split(sep=', ')
        
                # create a box object
                bb = sg.box(*json.loads(tmp[3]))
        
                # build a feature if it intersects the aoi
                if bb.intersects(aoi_bb):
                    feat = {
                        'type': 'Feature', 
                        'properties': {
                            'name': tmp[0], 
                            'x': tmp[1], 
                            'y': tmp[2]
                        }, 
                        'geometry': bb.__geo_interface__
                    }
            
                    features.append(feat)

        grid_gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')

        # filter by cliping 
        grid_gdf.geometry = grid_gdf.intersection(aoi_shp)
    
        # filter empty geometries
        grid_gdf = grid_gdf[np.invert(grid_gdf.is_empty)]
    
        # save the grid
        grid_gdf.to_file(grid_file, driver='GeoJSON')
    
    # convert the grid to ee for display
    json_df = json.loads(grid_gdf.to_json())
    grid_ee = geemap.geojson_to_ee(json_df)
    
    # display the grid on the map
    empty = ee.Image().byte()
    outline = empty.paint(featureCollection = grid_ee, color = 1, width = 3)
    m.addLayer(outline, {'palette': v.theme.themes.dark.accent}, 'AOI Planet© Grid')
    
    return grid_gdf
    
    
    
    
    