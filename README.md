# nps-night-rad
This repository contains a collection of scripts for calculating all-sky average light pollution from satellite data and visualizing changes in night-time sky quality over time. It was created to understand the effects of nearby and faraway light sources on Big Bend National Park's sky quality, using open-source tools. 

![image](https://raw.githubusercontent.com/katyabbott/nps-night-rad/master/images/2018_ALR_class.png?token=AJSRWDRNQYUEQFL6S2LRW3S6HCWLE)

Night sky quality in 2018 in the Big Bend region, visualized by sky-quality classes.

## How the algorithm works
[Duriscoe et al. (2018)](https://www.researchgate.net/publication/324789721_A_simplified_model_of_all-sky_artificial_sky_glow_derived_from_VIIRS_DayNight_band_data) used [VIIRs Day/Night Band upward radiance](https://maps.ngdc.noaa.gov/viewers/VIIRS_DNB_nighttime_imagery/index.html) to calculate what they called the all-sky average light pollution ratio (ALR), a unitless ratio of anthropogenic to natural conditions that takes into account the effects of skyglow over the entire hemisphere of vision.

ALR at a point can be calculated by summing the contributions of individual upward radiance values, weighted by their distance from the point, up to a radius of 300 km away. i.e. ALR = c &sum;r<sub>i</sub>d<sub>i</sub><sup>-&alpha;</sup>, where c is a calibration constant to compare the calculated output to observation data, &alpha; is a weighting function relating brightness to distance, d<sub>i</sub> is the distance from the point, and r<sub>i</sub> is the upward radiance at the distance of interest.

Duriscoe et al. also derived a brightness/distance function using observational data from the western United States to relate brightness to distance from a source, with &alpha; = 2.3 ((d &#47; 350)<sup>0.28</sup>)

Below is a schematic from Duriscoe et al. explaining this process. 

![image](https://www.researchgate.net/profile/Dan_Duriscoe/publication/324789721/figure/fig4/AS:628370182258695@1526826534880/The-flowchart-for-the-python-script-that-creates-the-dataset-a-TIFF-image-of-ALR-values.png)

They used ESRI software, such as the Neighborhood Annulus method, to calculate ALR for the continental(?) U.S. This method sums the contributions across individual rings at varying distances from the point of interest, utilizing the fact that the same distance weighting can be applied to all points along a ring. 

However, in this case, the Neighborhood Annulus simplifies to a simple convolution. 



