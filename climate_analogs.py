import os 
import math
from rasterstats import raster_stats
import numpy as np
from sklearn.neighbors import NearestNeighbors
import itertools
import json
from osgeo import gdal
from numpy import arange

gdal.PushErrorHandler('CPLQuietErrorHandler')

raster_dir = "./clipped_imgs"

def raster_path(year, climate, variable):
    if year == 1990:
        path = os.path.join(raster_dir, "current_%s.img" % variable)
    else:
        path = os.path.join(raster_dir, "%s_y%d_%s.img" % (climate, year, variable))
    return path

variables = [
    ('mat_tenths', 'Mean Annual Temperature'),
    ('map', 'Mean Annual Precipitation'),
    #('d100', 'Julian date that dd5 reaches 100'),
    ('dd0', 'Degree days below 0 degrees'),
    ('dd5', 'Degree days above 5 degrees C'),
    #('fday', 'Number of frost days'),
    ('ffp', 'Number of frost-free days'),
    ('gsdd5', 'dd5 accumulated within the frost-free period'),
    ('gsp', 'Growing Season Precipitation'),
    ('mmax_tenths', 'Mean maximum Temperature'),
    #('mmindd0', 'Mean Minimum Temperature for days below 0'), 
    ('mmin_tenths', 'Mean minimum Temperature'),
    ('mtcm_tenths', 'Mean Temperature of the coldest month'),
    ('mtwm_tenths', 'Mean Temperature of the warmest month'),
    ('sday', 'Julian date of first frost-free day'),
    ('smrpb', 'Summer Precipitation balance'),
]

def get_current_clims(pts):
    data = []
    wkts = ["POINT(%f %f)" % pt for pt in pts]
    for variable in variables:
        print variable[1]
        year = 1990
        climate = "Ensemble_rcp45"
        print "\tgetting raster stats..."
        path = raster_path(year, climate, variable[0])
        stats = raster_stats(wkts, path, stats="max")
        #vals = [x['max'] for x in stats if not math.isnan(x['max'])]
        vals = [x['max'] for x in stats]
        data.append(vals)

    # transpose
    print "Transposing..."
    data = map(list, zip(*data))
    return data


def scale_data(data, stds, means):
    return (data - means) / stds


def get_future_clim(pt):
    wkt = "POINT(%f %f)" % pt
    future_clim = []
    for variable in variables:
        year = 2060
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
    print indices
    matches = indices[0]
    return [potentials[m][0] for m in matches]


print "Gathering potential climate analogs...."

# Create grid of climate query points
minx = -125
miny = 34.2
maxx = -115
maxy = 50.05
step = 0.1
lons = arange(minx, maxx, step)
lats = arange(miny, maxy, step)


# grab data from cache of query the rasters
USE_CACHE = True
ccache = ".climate.cache"
if USE_CACHE and os.path.exists(ccache):
    potentials = json.loads(open(ccache).read())
else:
    potential_pts = list(itertools.product(lons, lats))
    potential_pts_clims = get_current_clims(potential_pts)

    potentials = zip(potential_pts, potential_pts_clims)
    # remove anything with nan
    potentials = [p for p in potentials if not (None in p[1] or math.isnan(sum(p[1])))]

    with open(ccache, 'w') as fh:
        fh.write(json.dumps(potentials))

# scaling params
clims = np.array([x[1] for x in potentials])
stds = np.std(clims, axis=0)
means = np.mean(clims, axis=0)
# print [round(x, 2) for x in stds]
# print [round(x, 2) for x in means]

# Prepare nearest neighbor search space
scaled_clims = scale_data(clims, stds, means)
search_space = NearestNeighbors(n_neighbors=10, algorithm='ball_tree').fit(scaled_clims)

print
print "Ready!"
print

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
