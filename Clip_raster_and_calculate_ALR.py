# Written by Katy Abbott as part of the Geoscientists-in-the-Parks 
# program at Big Bend National Park

import numpy as np
import os
import sys
from matplotlib import pyplot as plt
import time
from astropy.modeling.models import Ellipse2D
import astropy.convolution as conv
import re
import tarfile
import gdal
import geopandas as gpd
from osgeo import ogr
import osr

s1 = time.time()

## USER INPUTS - change these depending on your set-up
working_dir = '../Data/RasterData/'
geodb = '../BIBE_CORE_NightRadiance.gdb' #where buffer feature layers are stored
roi = 'BIBE_Boundary' #region of interest, will ultimately clip output to this
name = 'BIBE' #ID for labeling outputs
out_proj = 3083 #EPSG greater TX equal-area Albers. #Change this to reflect your location's equal-area Albers projection code.
#Note that units should be meters for buffer calculation
image_tile = '75N180W' #image tile assigned by VIIRS/DNB
verbosity = True #print logging statements (such as time elapsed) as program runs

#Make new folder output if necessary
if not os.path.exists(working_dir + 'ALR_outputs'):
    os.mkdir(working_dir + 'ALR_outputs')
ALR_ras = 'ALR_outputs/ALR_{{}}_{}.tif'.format(name)

## SYSTEM INPUTS
try:
    fname = sys.argv[1] #i.e. location of 'SVDNB_npp_20181201-20181231_75N180W_vcmcfg_v10_c201902122100.tgz'
except IndexError:
    print("You must supply a file path for the location of the input radiance raster. \n In this case, it is a tarball downloaded from EOG.")
    exit()
os.chdir(working_dir)

## FUNCTIONS
#adapted from astroimtools
def circular_annulus_footprint(radius_inner, radius_outer, dtype=np.int):
    if radius_inner > radius_outer:
        raise ValueError('radius_outer must be >= radius_inner')
    size = (radius_outer * 2) + 1
    y, x = np.mgrid[0:size, 0:size]
    circle_outer = Ellipse2D(1, radius_outer, radius_outer, radius_outer,
                             radius_outer, theta=0)(x, y)
    circle_inner = Ellipse2D(1., radius_outer, radius_outer, radius_inner,
                             radius_inner, theta=0)(x, y)
    return np.asarray(circle_outer - circle_inner, dtype=dtype)

verboseprint = print if verbosity else lambda *args, **kwargs: None

## START WORKFLOW
verboseprint("Starting workflow")
N = 38 #number of rings for calculation. Can be adjusted, but more rings means
#greater memory and slower computation

#Check inputs and extract dates
date_str = re.search(r'\d{4}\d{2}\d{2}',fname).group(0)
tile_check = re.search(image_tile, fname)
if tile_check is None:
    print("Image tile does not match user input. Check and try again.")
    print("Terminating execution.")
    exit()

#Open shapefile and generate 300km buffer if not already created
buffer_name = roi + '_300km_buffer.json'
if not os.path.exists(buffer_name):
    gdf = gpd.read_file(geodb, layer = roi, driver = 'FileGDB')
    gdf_proj = gdf.to_crs({'init': 'epsg:{}'.format(out_proj)})
    gdf_buffer = gdf_proj.buffer(300*1000) #300 km in METERS
    gdf_buffer.to_file(buffer_name, driver = 'GeoJSON')

#Open file in memory, crop and reproject
verboseprint("Starting read raster and clip by shapefile")
s2 = time.time()
tar = tarfile.open(fname, 'r:gz')
member = tar.getnames()[0] #this is the ave_rade9h.tif file
img_data = tar.extractfile(member)
gdal.FileFromMemBuffer('/vsimem/tiffinmem', img_data.read())
dataset = gdal.Open('/vsimem/tiffinmem', gdal.GA_ReadOnly)
gt_orig = dataset.GetGeoTransform() #for getting original raster resolution
x_orig_res, y_orig_res = gt_orig[1], -gt_orig[5]
#Reproject and clip raster in memory
OutTile = gdal.Warp('/vsimem/clipped_reprojected.tif',dataset,cutlineDSName=buffer_name, xRes = 450, 
                    yRes=450, srcSRS='EPSG:4326', 
                    dstSRS='EPSG:'+str(out_proj), cropToCutline=True, dstNodata=-9999)

verboseprint(str(time.time() - s2) + " seconds required to read raster into memory and clip by shapefile.")

gt = OutTile.GetGeoTransform()
x_res, y_res = gt[1], -gt[5]

if x_res != y_res:
    print("x-resolution should be equal to y resolution. Check gdal.Warp.")
    print("Terminating execution.")
    exit()

#Save output to open as memory-mapped array
arr = OutTile.ReadAsArray()
arr[arr == -9999] = np.nan
arr[np.less(arr,0.5,where=~np.isnan(arr))] = 0 #per Duriscoe, ignore less than 0.5 in rad
shp = arr.shape

#Free up memory
del OutTile
del dataset
gdal.Unlink('/vsimem/tiffinmem')
gdal.Unlink('/vsimem/clipped_reprojected.tif')

#Quick conversion tools and other useful lambdas
cell2dist = lambda x: x*x_res/1000 #from cell pixels to km
dist2cell = lambda x: x*1000/x_res #from km to cell pixels
alpha = lambda d: 2.3*(d/350.)**0.28

#Calculate annulus ring cutoffs, assuming N rings
annulus = np.linspace(0,dist2cell(300),N+1, dtype = 'int')
#calculate average radius for each ring - these are the distance weights
dist = np.convolve(cell2dist(annulus),np.ones((2,))/2,mode = 'valid')
dist_weights = [d**(-alpha(d)) for d in dist] #from Duriscoe et al (2018)

eps = .001 #epsilon needed for first annulus (to exclude central point)
ALR = np.zeros(shp)

#Calculate ALR using Fast Fourier transform
verboseprint("Starting annulus calculations")
s3 = time.time()
for i in range(N):
    s4 = time.time()
    kernel = circular_annulus_footprint(annulus[i] + eps,annulus[i+1])
    wgt = dist_weights[i]
    out = conv.convolve_fft(arr, kernel, normalize_kernel = False, 
                            allow_huge = True, preserve_nan = True, fft_pad = False, 
                            crop = True)
    out *= wgt
    ALR += out
    verboseprint(str(time.time() - s4) + " seconds required for {}th annulus".format(i))

verboseprint(str(time.time() - s3) + " seconds required to calculate ALR.")     

ALR = ALR/562.72 #calibration constant from Duriscoe

#Save output
driver = gdal.GetDriverByName('MEM')
ds = driver.Create('', ALR.shape[1], ALR.shape[0],1,gdal.GDT_Float64)
srs = osr.SpatialReference()
srs.ImportFromEPSG(out_proj)
ds.SetProjection(srs.ExportToWkt())
ds.SetGeoTransform(gt)
outband = ds.GetRasterBand(1)
outband.WriteArray(ALR)

#Clip to region of interest (this is max extent that output is valid for) and reproject to original rad raster projection
OutTile = gdal.Warp(ALR_ras.format(date_str), ds, cutlineDSName=geodb, xRes = x_orig_res, 
                    yRes = y_orig_res, cutlineLayer = roi, srcSRS='EPSG:'+str(out_proj), 
                    dstSRS='EPSG:4326', cropToCutline = True, dstNodata=-9999)

ds = None

verboseprint(str(time.time() - s1) + " seconds elapsed total.")
