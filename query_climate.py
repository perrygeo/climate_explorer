from rasterstats import raster_stats
import os

raster_dir = "./clipped_imgs"


def raster_path(year, climate, variable):
    if year == 1990:
        path = os.path.join(raster_dir, "current_%s.img" % variable)
    else:
        path = os.path.join(raster_dir, "%s_y%d_%s.img" % (climate, year, variable))
    return path


years = [1990, 2030, 2060, 2090]
climates = [
    "Ensemble_rcp45",
    "Ensemble_rcp60",
    "Ensemble_rcp85",
]
variables = [
    ('mat_tenths', 'Mean Annual Temperature'),
    ('map', 'Mean Annual Precipitation'),
    #('d100', 'Julian date that dd5 reaches 100'),
    #('dd0', 'Degree days below 0 degrees'),
    #('dd5', 'Degree days above 5 degrees C'),
    #('fday', 'Number of frost days'),
    ('ffp', 'Number of frost-free days'),
    #('gsdd5', 'dd5 accumulated within the frost-free period'),
    ('gsp', 'Growing Season Precipitation'),
    ('mmax_tenths', 'Mean maximum Temperature'),
    #('mmindd0', 'Mean Minimum Temperature for days below 0'),
    ('mmin_tenths', 'Mean minimum Temperature'),
    ('mtcm_tenths', 'Mean Temperature of the coldest month'),
    ('mtwm_tenths', 'Mean Temperature of the warmest month'),
    ('sday', 'Julian date of first frost-free day'),
    #('smrpb', 'Summer Precipitation balance'),
]

def query_climate(pt):
    wkt = "POINT(%f %f)" % pt
    data = {}
    for variable in variables:
        data[variable[1]] = {}
        for climate in climates:
            data[variable[1]][climate] = []
            for year in years:
                path = raster_path(year, climate, variable[0])
                stats = raster_stats(wkt, path, stats="max")
                val = stats[0]['max']
                if "_tenths" in variable[0]:
                    val = val / 10.0
                data[variable[1]][climate].append(val)

    return data


if __name__ == "__main__":
    pt = (-122.722, 45.514)
    import pprint
    pprint.pprint(query_climate(pt))
