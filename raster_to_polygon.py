# “C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\proenv.bat” 
# Used to create polygons from classified ALR data with geopandas, and
# add time-aware data

import glob
import os
import numpy as np
import geopandas as gpd 
import rasterio
from rasterio.features import shapes
import re
import pandas as pd

working_dir = r'U:/GIS_PROJECTS/CARTO/2019_CARTO_NightRadianceModel/Data/RasterData/ALR_outputs/May_Nov_ALR/' #add this in
os.chdir(working_dir)
files = glob.glob('ALRclass_*.tif')
re_date = '(?<=_)[0-9]{6}'

def gdf_from_raster(file):
    with rasterio.open(file) as src:
        image = src.read(1)
        transfrm = src.transform
        geoms = []
        for s, v in shapes(image, transform = transfrm):
            if v != 0: #ignore NoData areas
                result = {'properties': {'raster_val': v}, 'geometry': s}
                geoms.append(result)
    gdf = gpd.GeoDataFrame.from_features(geoms)
    return gdf

gdf_all = pd.DataFrame()
for file in files:
    gdf = gdf_from_raster(file)
    date_str = re.search(re_date, file)[0]
    gdf['MonthYear'] = date_str
    gdf_diss = gdf.dissolve(by = 'raster_val', as_index = False)
    gdf_all = gpd.GeoDataFrame(pd.concat([gdf_all, gdf_diss], ignore_index = True))

gdf_all.crs = {'init': 'epsg:4326'}
#Calculate area in km^2
gdf_all['geometry'].to_crs({'init':'epsg:3083'}).map(lambda p: p.area/10**6)

gdf_all.to_file(driver = 'ESRI Shapefile', filename = 'C:/Users/kabbott/Documents/May_Nov_ALR_2012-19.shp')


#gdf_all.to_file(driver = 'FileGDB', '../../../BIBE_CORE_NightRadiance.gdb', layer = 'test')


