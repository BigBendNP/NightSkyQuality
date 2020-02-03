#Script that ingests all ALR images and outputs the image classified by
#different thresholds per Duriscoe (i.e. 0 - 0.33 (good), .33 - 2.0 (moderate)
# 2-10 (poor), 10+ (Milky Way invisible)), saving to a new folder.

import os
import gdal
import numpy as np 
import glob
import re
import pandas as pd

working_dir = '../ALR_outputs'
name = 'BIBE'
os.chdir(working_dir)
files = glob.glob(working_dir + "/*.tif")

driver = gdal.GetDriverByName('GTiff')

cut = [-9999, 0.33, 2., 10.]

re_date_str = '(?<=ALR_)[0-9]{8}'

for file in files:
    print(file)
    try: 
        date_str = re.search(re_date_str, file)[0]
    except TypeError:
        print("Error!")
        continue #i.e. if you're opening a classification file, skip to next file
    ds = gdal.Open(file)
    band = ds.GetRasterBand(1)
    ras = band.ReadAsArray()
    cut_temp = cut.copy()
    cut_temp.append(np.nanmax(ras))
    ras_copy = ras.copy()
    for i in range(1,5):
        ras_copy[np.where((ras > cut_temp[i-1]) & (ras <= cut_temp[i]))] = i
    #Save output
    file2 = driver.Create("ALRclass_{} _{}.tif".format(date_str, name),
                ds.RasterXSize, ds.RasterYSize, 1)
    file2.GetRasterBand(1).WriteArray(ras_copy)
    proj = ds.GetProjection()
    georef = ds.GetGeoTransform()
    file2.SetProjection(proj)
    file2.SetGeoTransform(georef)
    file2.FlushCache()
    file2 = None

#Calculate areas of each class
files = glob.glob(working_dir + "/ALRclass*.tif")
re_date_str = '(?<=ALRclass_)[0-9]{8}'

data = []
for file in files:
    date_str = re.search(re_date_str, file)[0]
    ds = gdal.Open(file)
    band = ds.GetRasterBand(1)
    ras = band.ReadAsArray()
    total_pix = np.size(ras) - np.sum(ras == 0) #remove NoData, which is coded as 0
    percents = [np.sum(ras == i)*100/total_pix for i in range(1,5)]
    data.append([date_str] + percents) #append data for a dataframe

df = pd.DataFrame(data, columns = ['date', 'percentage_ones', 'percentage_twos', 'percentage_threes', 'percentage_fours'])
df.to_csv("{}_raster_classification.csv".format(name))
