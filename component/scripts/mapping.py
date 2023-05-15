"""Methods to interact with the map."""

from itertools import product

import geopandas as gpd
import numpy as np
from pyproj import CRS, Transformer
from sepal_ui import aoi
from shapely import geometry as sg

from component import parameter as cp


def set_grid(aoi_model: aoi.AoiModel) -> gpd.GeoDataFrame:
    """Create a grid adapted to the aoi and to the planet initial grid."""

    # check the grid filename
    aoi_name = aoi_model.name
    grid_file = cp.get_aoi_dir(aoi_name) / f"{aoi_name}_grid.geojson"

    # read the grid if possible
    if grid_file.is_file():
        return gpd.read_file(grid_file)

    # get the shape of the aoi in EPSG:3857 proj
    aoi_gdf = aoi_model.gdf.to_crs("EPSG:3857")

    # retreive the bb
    sg.box(*aoi_gdf.total_bounds)

    # compute the longitude and latitude in the apropriate CRS
    CRS.from_epsg(4326)
    crs_3857 = CRS.from_epsg(3857)
    crs_bounds = crs_3857.area_of_use.bounds

    proj = Transformer.from_crs(4326, 3857, always_xy=True)
    bl = proj.transform(crs_bounds[0], crs_bounds[1])
    tr = proj.transform(crs_bounds[2], crs_bounds[3])

    # the planet grid is constructing a 2048x2048 grid of SQUARES.
    # The latitude extends is bigger (20048966.10m VS 20026376.39) so to ensure the "squariness"
    # Planet lab have based the numerotation and extends of it square grid on the longitude only.
    # the extreme -90 and +90 band it thus exlucded but there are no forest there so we don't care
    longitudes = np.linspace(bl[0], tr[0], 2048 + 1)

    # the planet grid size cut the world in 248 squares vertically and horizontally
    box_size = (tr[0] - bl[0]) / 2048

    # filter with the geometry bounds
    bb = aoi_gdf.total_bounds

    # filter lon and lat
    lon_filter = longitudes[
        (longitudes > (bb[0] - box_size)) & (longitudes < bb[2] + box_size)
    ]
    lat_filter = longitudes[
        (longitudes > (bb[1] - box_size)) & (longitudes < bb[3] + box_size)
    ]

    # get the index offset
    x_offset = np.nonzero(longitudes == lon_filter[0])[0][0]
    y_offset = np.nonzero(longitudes == lat_filter[0])[0][0]

    # create the grid
    x, y, names, squares = [], [], [], []
    for coords in product(range(len(lon_filter) - 1), range(len(lat_filter) - 1)):

        # get the x and y index
        ix, iy = coords[0], coords[1]

        # fill the grid values
        x.append(ix + x_offset)
        y.append(iy + y_offset)
        names.append(f"L15-{x[-1]:4d}E-{y[-1]:4d}N.tif")
        squares.append(
            sg.box(
                lon_filter[ix],
                lat_filter[iy],
                lon_filter[ix + 1],
                lat_filter[iy + 1],
            )
        )

        # create a buffer grid in lat-long
        grid = gpd.GeoDataFrame(
            {"x": x, "y": y, "names": names, "geometry": squares}, crs="EPSG:3857"
        )

        # cut the grid to the aoi extends
        # the geometry is thus dissolve into 1 single geometry
        mask = grid.intersects(aoi_gdf.dissolve()["geometry"][0])
        grid = grid.loc[mask]

        # project back to 4326
        grid_gdf = grid.to_crs("EPSG:4326")

        # save the grid
        grid_gdf.to_file(grid_file, driver="GeoJSON")

    return grid_gdf
