# nps-night-rad
This repository contains a collection of scripts for calculating all-sky average light pollution from satellite data and visualizing changes in night-time sky quality over time. It was created to understand the effects of nearby and faraway light sources on Big Bend National Park's sky quality, using open-source tools. 

![image](images/2018_ALR_class.png?raw=true)

Night sky quality in 2018 in the Big Bend region, visualized by sky-quality classes.

## How the algorithm works
[Duriscoe et al. (2018)](https://www.researchgate.net/publication/324789721_A_simplified_model_of_all-sky_artificial_sky_glow_derived_from_VIIRS_DayNight_band_data) used [VIIRs Day/Night Band upward radiance](https://maps.ngdc.noaa.gov/viewers/VIIRS_DNB_nighttime_imagery/index.html) to calculate what they called the all-sky average light pollution ratio (ALR), a unitless ratio of anthropogenic to natural conditions that takes into account the effects of skyglow over the entire hemisphere of vision.

![image](https://www.nps.gov/subjects/nightskies/images/panoramic-big_1.jpg?maxwidth=650&autorotate=false) <br/>
False color negative, panoramic image from Palomar Observatory (California Institute of Technology) identifies natural and human-caused sky brightness
NPS / Palomar Observatory (California Institute of Technology)

ALR at a point can be calculated by summing the contributions of individual upward radiance values, weighted by their distance from the point, up to a radius of 300 km away. i.e. ALR = c &sum;r<sub>i</sub>d<sub>i</sub><sup>-&alpha;</sup>, where c is a calibration constant to compare the calculated output to observation data, &alpha; is a weighting function relating brightness to distance, d<sub>i</sub> is the distance from the point, and r<sub>i</sub> is the upward radiance at the distance of interest.

Duriscoe et al. also derived a brightness/distance function using observational data from the western United States to relate brightness to distance from a source, with &alpha; = 2.3 ((d &#47; 350)<sup>0.28</sup>)

Below is a schematic from Duriscoe et al. explaining this process. 

![image](https://www.researchgate.net/profile/Dan_Duriscoe/publication/324789721/figure/fig4/AS:628370182258695@1526826534880/The-flowchart-for-the-python-script-that-creates-the-dataset-a-TIFF-image-of-ALR-values.png)

This process can be optimized using open-source geospatial tools and image-processing techniques. ALR is calculated by summing the contributions of 



