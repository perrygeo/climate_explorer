Simple interactive map to browse future climate projections

* Front end uses Leaflet and D3js
* Back end uses Flask and [rasterstats](https://github.com/perrygeo/rasterstats) (based on GDAL, Numpy)  to query climate surfaces and return JSON containing time-series of projected climatic variables
 at different points in the future.

The same technique could be applied to any series of raster datasets.
