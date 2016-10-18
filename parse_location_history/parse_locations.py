import datetime, time, os
import json, math, cProfile

def file_to_dict(json_file):
    """ turns a json file into a dict """
    f = open(json_file, "r")
    return json.load(f)

def lat_long_diff(lat_long_1, lat_long_2):
    """ Diff in meters between two points
        for spherical triangle ABC where BC is what we want...
    """

    # radians for arc AB
    lat_diff = math.radians(lat_long_2[0] - lat_long_1[0])
    # radians for arc AC
    long_diff = math.radians(lat_long_2[1] - lat_long_1[1])
    # radius of earth
    radius = 6378100
    # Spherical law of cosines (cos of angle BAC == 0)
    cos = math.cos(lat_diff) * math.cos(long_diff)
    ang = math.acos(cos)
    # arc length for the angle between both points
    return ang * radius

def timestamp_to_date(timestamp):
    """ takes unix timestamp (ms) and converts it to UTC YYYY-MM-DD string """
    d = datetime.datetime.utcfromtimestamp(int(timestamp)/1000)
    return datetime.datetime.strftime(d, "%Y-%m-%d")

def update_farthest(location_obj, calendar_obj, home_coords):
    d = timestamp_to_date(location_obj["timestampMs"])
    away_coords = [location_obj["latitudeE7"] / 10000000.0, location_obj["longitudeE7"] / 10000000.0]
    dist = lat_long_diff(home_coords, away_coords)

    if (calendar_obj.get(d) and dist > calendar_obj[d]):
        calendar_obj[d] = dist
    elif (calendar_obj.get(d) is None):
        calendar_obj[d] = dist

    return calendar_obj

def process_file(start_date, end_date, file_path, home_coords):
    json_data = file_to_dict(file_path)
    
    start_ts = time.mktime(start_date.timetuple())
    end_ts = time.mktime(end_date.timetuple())
    calendar_obj = {}
    i = 0
    j = 0
    for obj in json_data["locations"]:
        i += 1
        location_obj = obj
        ts = int(location_obj["timestampMs"])/1000
        if (ts >= start_ts and ts < end_ts):
            j += 1
            calendar_obj = update_farthest(location_obj, calendar_obj, home_coords)
        
    return calendar_obj

def insert_data(tbl, new_item, sort_key):
    """ tbl is a multidimensional list """
    
    tl = len(tbl)
    if (tl == 0):
        return [new_item]

    for i in range(tl):

        if (new_item[sort_key] <= tbl[i][sort_key]):
            
            nt = tbl[:i] + [new_item] + tbl[i:]
            return tbl[:i] + [new_item] + tbl[i:]
        
    tbl.append(new_item)
    return tbl

def dict_to_tbl(obj, col):
    """ turn dict to tbl, sort by col number """
    nt = []
    for key in obj:
        nt = insert_data(nt, [key, obj[key]], col)

    fs = ""
    for i in nt:
        fs += "{}\n".format("\t".join(map(str, i)))
    return fs


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--start", help="YYYY-MM-DD. The date to start reading from (inclusive). ", required=False)
    parser.add_argument("-e","--end", help="YYYY-MM-DD. The date to end reading from (exclusive)", required=False)
    parser.add_argument("-f","--file", help="The filepath with the data", required=True)
    parser.add_argument("-u","--longitude", help="longitude of home address (in decimal degrees)", required=True, type=float)
    parser.add_argument("-l","--latitude", help="latitude of home address (in decimal degrees)", required=True, type=float)
    parser.add_argument("-d","--distanceorder", help="order by distance ascending", required=False, action="store_true")

    args = parser.parse_args()

    if (args.start):
        start_time = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    else:
        start_time = datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")
    if (args.end):
        end_time = datetime.datetime.strptime(args.end, "%Y-%m-%d")
    else:
        end_time = datetime.datetime.today()

    json_file = os.path.abspath(os.path.expanduser(args.file))
    if (not os.path.isfile(json_file)):
        raise ValueError("Specified file {} does not exist when expanded as {}".format(args.file, json_file))

    home_coords = [args.latitude, args.longitude]
    result = process_file(start_time, end_time, json_file, home_coords)

    print "done with process_file"

    if (args.distanceorder):
        print dict_to_tbl(result, 1)
    else:
        print dict_to_tbl(result, 0)
