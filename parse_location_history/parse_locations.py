import datetime, time, os
import json, math, cProfile

def file_to_dict(json_file):
    """ turns a json file into a dict """
    f = open(json_file, "r")
    return json.load(f)

def lat_long_diff(lat_long_1, lat_long_2):
    """ Diff in meters between two points
        for spherical triangle ABC where BC is what we want

        for reference, see :
        http://mathworld.wolfram.com/SphericalTrigonometry.html
        http://mathworld.wolfram.com/Arc.html
        https://en.wikipedia.org/wiki/Spherical_law_of_cosines
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
    """ Return updated version of calendar_obj

        location_obj - @param - dict including key-vals for timestampMs, latitudeE7, longitudeE7
                     - @type - dict
        calendar_obj - @param - {"date" : dist, "date" : dist, ...}
                     - @type - dict
        home_coords - @param - [lat, long] to find distance from
                    - @type - list
    """

    d = timestamp_to_date(location_obj["timestampMs"])
    away_coords = [location_obj["latitudeE7"] / 10000000.0, location_obj["longitudeE7"] / 10000000.0]
    dist = lat_long_diff(home_coords, away_coords)

    if (calendar_obj.get(d) and dist > calendar_obj[d]):
        calendar_obj[d] = dist
    elif (calendar_obj.get(d) is None):
        calendar_obj[d] = dist

    return calendar_obj

def process_file(start_date, end_date, file_path, home_coords):
    """ Return {date : dist, date : dist, ...}

        start_date - @param - the YYYY-MM-DD to begin search the file, inclusive
                   - @type - str
        end_date - @param - the YYYY-MM-DD to end searching the file, exclusive
                 - @type - str
        file_path - @param - the path of the source json file
                  - @type - str
        home_coords - @param - [lat, long] in decimal notation (e.g. 40.4, not 40deg 30min)
                    - @type - list
    """
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

def sort_data(obj, col):
    """ sort data by col number. Returns multidim. list """
    nt = []
    for key in obj:
        nt = insert_data(nt, [key, obj[key]], col)
    return nt

def convert_to_tsv(obj):
    """ turn list to tsv tbl """

    fs = ""
    for i in obj:
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
    parser.add_argument("-t","--format", help="`tsv` or `array`, a multidimensional array string", default="array", required=True)
    parser.add_argument("-o","--out", help="file to write to. If none, writes to stdout", required=False)

    args = parser.parse_args()

    # Parse date range. Defaults to epoch until today
    if (args.start):
        start_time = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    else:
        start_time = datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")
    if (args.end):
        end_time = datetime.datetime.strptime(args.end, "%Y-%m-%d")
    else:
        end_time = datetime.datetime.today()

    # Get path of the file supplied by --file.
    json_file = os.path.abspath(os.path.expanduser(args.file))
    if (not os.path.isfile(json_file)):
        raise ValueError("Specified file {} does not exist when expanded as {}".format(args.file, json_file))

    home_coords = [args.latitude, args.longitude]

    # read through the file, returning an unsorted list [[date, dist], [date, dist]]
    result = process_file(start_time, end_time, json_file, home_coords)

    if (args.distanceorder):
        result = sort_data(result, 1)
    else:
        result = sort_data(result, 0)

    if (args.format == "tsv"):
        result = convert_to_tsv(result)


    if (args.out):
        f = os.path.abspath(os.path.expanduser(args.out))
        d = os.path.dirname(f)
        if (not os.path.isdir(d)):
            print "the directory {} does not exist, writing to stdout".format(d)
            print result
        f = open(f, "w")
        f.write(result)
    else:
        print result
