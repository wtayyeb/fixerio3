"""
This file provides the get_rates and convert modules to interact with the fixerio API.
Both modules can be used as independent functions or as methods on Fixerio objects.
The independent functions fetch data every time from the API but the methods on Fiexerio
objects use caching to avoid having to wait for API queries.

get_rates(date: str = DEFAULT_DATE, base: str = DEFAULT_BASE, symbols: str = None) -> dict:
convert(amount: float, target: str, base: str = DEFAULT_BASE, date: str = DEFAULT_DATE) -> float:

NOTE: Whenever using the class, you are responsible for calling the clear_cache() method
whenever you see fit so that the cache does not get to large in size (which shouldn't be
a concern for most people)
"""

from datetime import date as dtdate
from datetime import timedelta
from datetime import datetime
import requests
from exceptions import FixerioException
from exceptions import FixerioInvalidDate
from exceptions import FixerioInvalidCurrency
from exceptions import FixerioCurrencyUnavailable
from string import whitespace
import json
import re

HTTPS_BASE_URL = 'https://api.fixer.io/'
# Modify BASE_URL if you want to use a different URL to fetch data
BASE_URL = HTTPS_BASE_URL
# Modify DEFAULT BASE if you want to use a different base when 'base' is
# omitted in the 'convert' or 'get_rates' methods
DEFAULT_BASE = 'USD'
LATEST = 'latest'
# Modify DEFAULT_DATE if you want use a different date when 'date' is
# omitted in the 'convert' or 'get_rates' methods
DEFAULT_DATE = LATEST
MIN_DATE = dtdate(1999, 1, 4)
UPDATE_TIME_UTC = 15  # rates are updated at 3pm (15:00) UTC (10am ET)
# Modify SPECIFIC_CURRENCIES if you want to only retrieve a subset of
# ALL_CURRENCIES when 'symbols' is omitted in the 'get_rates' method.
# You need to also modify the CURRENCIES variable below
SPECIFIC_CURRENCIES = set()
ALL_CURRENCIES = {"AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK",
                  "DKK", "EUR", "GBP", "HKD", "HRK", "HUF", "IDR",
                  "ILS", "INR", "ISK", "JPY", "KRW", "MXN", "MYR",
                  "NOK", "NZD", "PHP", "PLN", "RON", "RUB", "SEK",
                  "SGD", "THB", "TRY", "USD", "ZAR"}
# Modify currencies to specify which currencies to retrieve when 'symbols'
# is omitted in the 'get_rates' method
CURRENCIES = ALL_CURRENCIES
CACHE_FILE_NAME = 'fixerio3_cache'
CACHE_FILE_FORMAT = 'json'


def _date(date=None):
    """ Returns the date fixer.io should've been last updated """
    if (date == LATEST) or (date is None):
        if datetime.utcnow().time().hour < UPDATE_TIME_UTC:
            return str(datetime.utcnow().date() - timedelta(1))
        else:
            return str(datetime.utcnow().date())
    else:
        return date


def _valid_date(date):
    """ Validates that the given date is withing the accepted ranges for the fixer.io API """
    try:
        if date == LATEST:
            return True
        else:
            date = _format_date(date)
            if date is None:
                return False
            if (date <= datetime.utcnow().date()) and (date >= MIN_DATE):
                return True
            else:
                return False
    except Exception:
        raise FixerioInvalidDate("Error validating date.\n"
                                 "Please enter a valid date in the format 'yyyy-mm-dd' or 'latest' "
                                 "between 1999-01-04 and today's date")


def _format_date(date: str):
    """ Takes string representation of a date in the format 'yyyy-mm-dd' or 'latest'
        and returns a date object or 'latest' """
    try:
        if date == LATEST:
            return date
        elif type(date) is dtdate:
            return date
        else:
            dates = [int(x.lstrip('0' + whitespace)) for x in date.strip().split('-')]
            if len(dates) == 3:
                return dtdate(*dates)
            else:
                return None
    except Exception as e:
        raise FixerioInvalidDate('Please enter a valid date in the format "yyyy-mm-dd"') from e


def _valid_currency(args):
    """ Raises an exception only for the first currency not found in the list ALL_CURRENCIES """
    try:
        if args is None:
            return True
        args = _format_currency(args)
        if args is None:
            return False

        for x in args:
            if x not in ALL_CURRENCIES:
                return False
        else:
            return True
    except Exception as e:
        raise FixerioCurrencyUnavailable('Please enter valid currencies such as "USD" or "AUD" '
                                         'either on a list or as a string of comma separated values') from e


def _format_currency(currencies):
    """ Returns a list of currencies to be iterated over """
    try:
        if isinstance(currencies, str):
            if len(currencies) > 3:
                return [x.strip() for x in currencies.strip().split(',')]
            elif len(currencies) == 3:
                return [currencies]
            else:
                return None
        elif isinstance(currencies, list):
            return currencies
        else:
            return None
    except Exception as e:
        raise FixerioCurrencyUnavailable('Please enter valid currencies such as "USD" or "AUD" '
                                         'either on a list or as a string of comma separated values') from e


def get_rates(date: str=DEFAULT_DATE, base: str=DEFAULT_BASE, symbols=None) -> dict:
    """ Fetches rates for the given parameters (NO CACHING)

        date: OPTIONAL type str
            a date form January 4th 1999 to today in the format 'yyyy-mm-dd'
            or 'latest'. If omitted, DEFAULT_DATE is used (usually 'latest' if you haven't changed it).

        base: OPTIONAL type str
            a 3 letter currency code such as 'EUR'. If omitted, DEFAULT_BASE is used
            (usually 'USD' if you haven't changed it).

        symbols: OPTIONAL type str or list
            a string of comma separated currency codes like 'USD,JPY,EUR' or list like ['USD', 'EUR'].
            If omitted, all rates are returned for the corresponding base and date.
    """
    url = BASE_URL + date
    if symbols is None:
        payload = dict(base=base)
    elif isinstance(symbols, list):
        symbols = ','.join(symbols)
        payload = dict(base=base, symbols=symbols)
    elif isinstance(symbols, str):
        payload = dict(base=base, symbols=symbols)
    else:
        raise ValueError(""" Invalid value entered for the symbols parameter.
                             Check your input and try again """)
    response = requests.get(url, params=payload)
    json_data = response.json()
    return json_data['rates']


def convert(amount: float, target: str, base: str=DEFAULT_BASE, date=DEFAULT_DATE) -> float:
    """ Converts an amount from the base currency to the target currency (NO CACHING)

        amount: REQUIRED type float or str
            an integer or float amount of the base currency to convert.

        target: REQUIRED type str
            a 3 letter currency code such as 'JPY'.

        base: OPTIONAL type str
            a 3 letter currency code such as 'EUR'. If omitted, DEFAULT_BASE is used
            (usually 'USD' if you haven't changed it).

        date: OPTIONAL type str
            a date form January 4th 1999 to today in the format 'yyyy-mm-dd'
            or 'latest'. If omitted, DEFAULT_DATE is used (usually 'latest' if you haven't changed it).
    """
    if base == target:
        return amount
    conversion_rate = get_rates(date=date, base=base, symbols=target)
    return float(amount) * conversion_rate[target]


def write_to_file(data=None, file=CACHE_FILE_NAME, wformat=CACHE_FILE_FORMAT):
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


def read_from_file(file=CACHE_FILE_NAME, rformat=CACHE_FILE_FORMAT):
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
    currency = re.compile(r'[A-Z]{3,3},{1}[0-9,.]+')
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


class Fixerio:
    """
    Class to interact with the free fixer.io API
    Similar to the 'get_rates' and 'convert' functions but uses caching to
    avoid invoking the fixer.io API on every request
    """

    def __init__(self, cache_to_file=False, out_name=CACHE_FILE_NAME, out_format=CACHE_FILE_FORMAT,
                 in_file=None, in_format=CACHE_FILE_FORMAT):
        self._cache = dict()
        self._cache_to_file = cache_to_file
        self._out_file_name = out_name
        self._format_to_file = out_format
        if in_file is not None:
            if in_format == 'json':
                self._cache = read_from_file(in_file, in_format)
            elif in_format == 'csv':
                self._cache = _csv_to_json(read_from_file(in_file, in_format))
            else:
                raise ValueError("Please enter a valid in_file format. "
                                 "Supported values are 'json' (default), and 'csv'")

    def _in_cache(self, base, symbols, date=_date()):
        """ Checks to see if the specified rates have already been retrieved and are in the cache """
        try:
            if symbols is None:
                in_date = dtdate(*(int(x.strip('0')) for x in date.split('-')))
                if in_date < dtdate(2011, 1, 3):
                    symbols = list(CURRENCIES.difference({base, 'ISK', 'ILS'}))
                elif in_date < dtdate(2018, 2, 1):
                    symbols = list(CURRENCIES.difference({base, 'ISK'}))
                else:
                    symbols = list(CURRENCIES.difference({base}))

            symbols = _format_currency(symbols)

            if base in self._cache:
                if date in self._cache[base]:
                    if symbols is not None:
                        for x in symbols:
                            if x not in self._cache[base][date]:
                                return False
                        else:
                            return True
                    else:
                        return CURRENCIES.difference({base}).issubset(self._cache[base][date].keys())
                else:
                    return False
            else:
                return False
        except KeyError:
            return False

    def _return_cache(self, base, symbols, date=_date()):
        """ Returns cached items if available (check availability with '_in_cache') """
        try:
            if symbols is None:
                symbols = CURRENCIES
            cached_items = {x: self._cache[base][date][x]
                            for x in self._cache[base][date] if x in symbols}
            return cached_items
        except KeyError as e:
            raise ValueError('Error returning cache. Make sure to first check if the '
                             'object is in the cache with the "_in_cache" method') from e

    def _to_cache(self, json_data):
        """ Caches the given info for future use """
        try:
            base = json_data['base']
            date = json_data['date']
            if base not in self._cache:
                self._cache[base] = dict()
            if date not in self._cache[base]:
                self._cache[base][date] = dict()
            self._cache[base][date] = json_data['rates']
            return None
        except KeyError as e:
            raise FixerioException("Error caching data. Make sure you are passing in the "
                                   "json_data portion of the response") from e

    def clear_cache(self):
        """ Clears any references to the cache dictionary """
        self._cache.clear()

    def get_cache(self):
        """ Returns all contents in the cache """
        return self._cache

    def get_rates(self, date: str=DEFAULT_DATE, base: str=DEFAULT_BASE, symbols=None) -> dict:
        """
        Returns rates based on the specified parameters below.
        From cache if available, otherwise from the API call.

        date
            :param date: a date to quote rates on. If omitted, DEFAULT_DATE is used
            :type: str in the format 'yyyy-mm-dd' or 'latest'

        base
            :param base: currency to quote rates against. If omitted, DEFAULT_BASE is used
            :type: str (e.g. 'USD')

        symbols
            :param symbols: currency symbols to request specific exchange rates for
            :type: str or list e.g. 'USD,JPY,EUR' or [USD, JPY, EUR]

        :return dict: a dictionary with the requested rates
        """
        if not _valid_date(date):
            raise FixerioInvalidDate('Please enter a valid date')
        if not _valid_currency(base):
            raise FixerioInvalidCurrency('Please enter a valid base currency')
        if not _valid_currency(symbols):
            raise FixerioInvalidCurrency('Please enter valid symbols (aka target currency)')
        if self._in_cache(base, symbols, _date(date)):
            if self._cache_to_file:
                write_to_file(self._cache, self._out_file_name, self._format_to_file)
            return self._return_cache(base, symbols, _date(date))
        else:
            url = BASE_URL + date
            symbols = _format_currency(symbols)
            if symbols is None:
                payload = dict(base=base)
            else:
                payload = dict(base=base, symbols=symbols)
            response = requests.get(url, params=payload)
            json_data = response.json()
            if 'error' in json_data:
                raise FixerioException('Something went wrong with your request.'
                                       'Error message: {}'.format(json_data['error']))
            self._to_cache(json_data)
            if self._cache_to_file:
                write_to_file(self._cache, self._out_file_name, self._format_to_file)

            return json_data['rates']

    def convert(self, amount, target, base=DEFAULT_BASE, date=DEFAULT_DATE):
        """
        Converts an amount from the base currency to the target currency.
        Fetches from cache if available, otherwise from the API call.

        amount
            :param amount: amount of base currency to convert
            :type: str, int or float

        date
            :param date: a date to quote rates on. If omitted, DEFAULT_DATE is used
            :type: str in the format 'yyyy-mm-dd' or 'latest'

        base
            :param base: currency to quote rates against. If omitted, DEFAULT_BASE is used
            :type: str (e.g. 'USD')

        target
            :param target: currency to convert to
            :type: str (e.g. 'EUR')

        :return float: the converted amount
        """
        try:
            if target is None:
                raise FixerioInvalidCurrency("Enter a valid 'target' currency")
            if not _valid_currency(','.join([base, target])):
                raise FixerioInvalidCurrency('Please enter a valid currencies for the conversion')
            if base == target:
                return float(amount)
            elif self._in_cache(base, target, date):
                conversion_rate = self._return_cache(base, target, date)
            else:
                conversion_rate = self.get_rates(date=date, base=base, symbols=target)
            return float(amount) * float(conversion_rate[target])
        except ValueError as e:
            raise ValueError('Please enter a valid numeric amount to convert') from e
        except TypeError as e:
            raise TypeError('Please enter valid currency codes.') from e

#TODO add support for API keys (just added)
