import os 
import math
from rasterstats import raster_stats
import numpy as np
from sklearn.neighbors import NearestNeighbors
import itertools
import json
from osgeo import gdal
gdal.PushErrorHandler('CPLQuietErrorHandler')

raster_dir = "./clipped_imgs"

def raster_path(year, climate, variable):
    if year == 1990:
        path = os.path.join(raster_dir, "current_%s.img" % variable)
    else:
        path = os.path.join(raster_dir, "%s_y%d_%s.img" % (climate, year, variable))
    return path

years = [1990, 2030, 2060, 2090]
climates = [
    #"Ensemble_rcp45",
    "Ensemble_rcp60",
    #"Ensemble_rcp85",
]
variables = [
    # ('mat_tenths', 'Mean Annual Temperature'),
    ('map', 'Mean Annual Precipitation'),
    # ('d100', 'Julian date that dd5 reaches 100'),
    # ('dd0', 'Degree days below 0 degrees'),
    # ('dd5', 'Degree days above 5 degrees C'),
    # ('fday', 'Number of frost days'),
    ('ffp', 'Number of frost-free days'),
    # ('gsdd5', 'dd5 accumulated within the frost-free period'),
    ('gsp', 'Growing Season Precipitation'),
    # ('mmax_tenths', 'Mean maximum Temperature'),
    # ('mmindd0', 'Mean Minimum Temperature for days below 0'), 
    # ('mmin_tenths', 'Mean minimum Temperature'),
    ('mtcm_tenths', 'Mean Temperature of the coldest month'),
    ('mtwm_tenths', 'Mean Temperature of the warmest month'),
    # ('sday', 'Julian date of first frost-free day'),
    ('smrpb', 'Summer Precipitation balance'),
]

def get_current_clims(pts):
    data = []
    wkts = ["POINT(%f %f)" % pt for pt in pts]
    for variable in variables:
        year = 2030
        climate = "Ensemble_rcp45"

        path = raster_path(year, climate, variable[0])
        stats = raster_stats(wkts, path, stats="max")
        #vals = [x['max'] for x in stats if not math.isnan(x['max'])]
        vals = [x['max'] for x in stats]
        data.append(vals)

    # transpose
    data = map(list, zip(*data))
    return data

print "Gathering potential climate analogs...."
from numpy import arange
minx = -125
miny = 34.2
maxx = -115
maxy = 50.05
step = 0.1

lons = arange(minx, maxx, step)
lats = arange(miny, maxy, step)

ccache = ".climate.cache"
if os.path.exists(ccache):
    potentials = json.loads(open(ccache).read())
else:
    potential_pts = list(itertools.product(lons, lats))
    potential_pts_clims = get_current_clims(potential_pts)

    potentials = zip(potential_pts, potential_pts_clims)
    # remove anything with nan
    potentials = [p for p in potentials if not (None in p[1] or math.isnan(sum(p[1])))]

    with open(ccache, 'w') as fh:
        fh.write(json.dumps(potentials))

clims = np.array([x[1] for x in potentials])
high = 100.0
low = 0.0
mins = np.min(clims, axis=0)
maxs = np.max(clims, axis=0)
stds = np.std(clims, axis=0)
means = np.mean(clims, axis=0)

rng = maxs - mins
# print [float(x) for x in mins]
# print [float(x) for x in maxs]
print [round(x, 2) for x in stds]
print [round(x, 2) for x in means]
# scale
def scale_data(data, stds, means):
    #return high - (((high - low) * (maxs - clims)) / rng)
    return (data - means) / stds

scaled_clims = scale_data(clims, stds, means)

search_space = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(scaled_clims)

print
print "Ready!"
print
# for p in potentials:
#     print p[0]


def get_future_clim(pt):
    wkt = "POINT(%f %f)" % pt
    future_clim = []
    for variable in variables:
        year = 2090
        climate = "Ensemble_rcp60"
        path = raster_path(year, climate, variable[0])
        stats = raster_stats(wkt, path, stats="max")
        val = stats[0]['max']
        future_clim.append(val)

    return future_clim

def query_analog(pt):
    future_clim = get_future_clim(pt)
    scaled_future_clim = scale_data(future_clim, stds, means)
    distances, indices = search_space.kneighbors(scaled_future_clim)
    match = indices[0][0]
    return potentials[match][0]

if __name__ == "__main__":
    pt = (-122.722, 45.514)
    future_clim = get_future_clim(pt)

    print "Out of", len(potentials), "potential points"
    print "Find current analogs to the future climate of", pt
    print
    print future_clim

    #scaled_future_clim = high - (((high - low) * (maxs - future_clim)) / rng)
    scaled_future_clim = scale_data(future_clim, stds, means)
    distances, indices = search_space.kneighbors(scaled_future_clim)
    #print distances, indices
    match = indices[0][0]
    print potentials[match][1]
    print
    print potentials[match][0]
