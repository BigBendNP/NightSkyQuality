import arcpy
import calendar
import glob
import re 
import os

arcpy.env.workspace = r"../Data"
os.chdir(arcpy.env.workspace)

rasters = glob.glob(r"/ALR_outputs/ALR_*.tif")
year_expr = "(?<=ALR_)[0-9]{4}"
month_expr = "(?<=20[0-9]{2})[0-9]{2}"
mosaic_fmt = "ALR_{}_{}_BIBE_300km"

for ras in rasters:
	print(ras)
	month_int = int(re.search(month_expr, ras).group(0))
	yy = int(re.search(year_expr, ras).group(0))
	msic = mosaic_fmt.format(yy, calendar.month_abbr[month_int])
	arcpy.management.CreateMosaicDataset("NightRadiance.gdb", msic, 
		"GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],\
		PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
		None, '', "NONE", None)
	arcpy.management.AddRastersToMosaicDataset("NightRadiance.gdb/" + msic, "Raster Dataset", ras, 
		"UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "UPDATE_OVERVIEWS", None, 
		0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "BUILD_PYRAMIDS", 
		"CALCULATE_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE",
		"ESTIMATE_STATISTICS", None, "NO_PIXEL_CACHE", 
		r"../AppData/Local/ESRI/rasterproxies/"+ msic)
