import json
import re
from fixerio3.exceptions import FixerioException

ERROR_CODES = {
    404: 'The requested resource does not exist.',
    101: 'No API Key was specified or an invalid API Key was specified.',
    103: 'The requested API endpoint does not exist.',
    104: 'The maximum allowed API amount of monthly API requests has been reached.',
    105: 'The current subscription plan does not support this API endpoint.',
    106: 'The current request did not return any results.',
    102: 'The account this API request is coming from is inactive.',
    201: 'An invalid base currency has been entered.',
    202: 'One or more invalid symbols have been specified.',
    301: 'No date has been specified. [historical]',
    302: 'An invalid date has been specified. [historical, convert]',
    403: 'No or an invalid amount has been specified. [convert]',
    501: 'No or an invalid timeframe has been specified. [timeseries]',
    502: 'No or an invalid "start_date" has been specified. [timeseries, fluctuation]',
    503: 'No or an invalid "end_date" has been specified. [timeseries, fluctuation]',
    504: 'An invalid timeframe has been specified. [timeseries, fluctuation]',
    505: 'The specified timeframe is too long, exceeding 365 days. [timeseries, fluctuation]'}


def write_to_file(data=None, file=None, wformat=None):
    """
    Writes cached data to a file in JSON or CSV format.
    If the specified file name already exists, it is overwritten

    :param data: JSON data to write to file
    :param file: name of the file to write the cached data to
    :param wformat: output format. Options are 'json' or 'csv'
    :return: None
    """
    if data is None:
        raise Exception('Data missing. Please specify the data to write to file.')
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to write to.')

    with open(file, 'w') as f:
        if wformat == 'json':
            json.dump(data, f, ensure_ascii=False)
        elif wformat == 'csv':
            f.write(_json_to_csv(data))
        else:
            raise ValueError("Please enter a valid write format. Supported values are 'json' (default), and 'csv'")


def read_from_file(file=None, rformat=None):
    """
    Reads cached data from a file in JSON or CSV format

    :param file: name of the file to read from
    :param rformat: format of the file being read
    :return: the data read from the file
    """
    if file is None:
        raise Exception('File name missing. Please specify the name of a file to read from.')

    with open(file, 'r') as f:
        contents = f.read()
        if rformat == 'json':
            return json.loads(contents)
        elif rformat == 'csv':
            return contents
        else:
            raise ValueError("Please enter a valid rformat. Valid values are 'json', 'numpy', and 'csv'.")


def _csv_to_json(data=None):
    """ Takes properly formatted csv data and returns it in json format """
    converted = dict()
    base_date = re.compile(r'base,date')
    currency = re.compile(r'[A-Z]{3},{1}[0-9,.]+')
    base = None
    date = None
    for line in data.splitlines():
        if base_date.match(line) is not None:
            base, date = line.split(',')[2:]
            if base not in converted:
                converted[base] = dict()
            if date not in converted[base]:
                converted[base][date] = dict()
            continue
        elif currency.match(line) is not None:
            curr, rate = line.split(',', 1)
            converted[base][date][curr] = rate
            continue
    else:
        return converted


def _json_to_csv(data=None):
    """ Takes properly formatted json data and returns it in csv format """
    output = ''
    if data is None:
        raise FixerioException('Data missing, please input json data to convert to csv.')
    for x in data:
        for y in data[x]:
            output += 'base,date,' + x + ',' + y + '\n'
            for z in data[x][y]:
                output += z + ',' + str(data[x][y][z]) + '\n'
    return output

# TODO use new caching function
class Cache:
    def __init__(self):
        _cache = dict()

    def __call__(self, *args, **kwargs):
        pass