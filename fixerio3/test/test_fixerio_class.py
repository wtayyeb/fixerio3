from fixerio3 import fixerio


def main():
    """ Usage examples for the fixerio class """
    test = fixerio.Fixerio(cache_to_file=False, out_name='fixerio3_cache.json', out_format='json',
                           in_file=None, in_format=None)
    response = test.convert(20, base='USD', target='JPY', date='2018-01-10')
    print(response, end='\n\n')
    response = test.convert(20, target='JPY', base='EUR')
    print(response, end='\n\n')
    response = test.convert(20, target='JPY')
    print(response, end='\n\n')
    response = test.get_rates(date='2010-12-31')
    print(response, end='\n\n')
    response = test.get_rates()
    print(response, end='\n\n')
    response = test.convert(1000.0, 'EUR', date='2010-12-31')
    print(response, end='\n\n')
    response = test.convert(1000.0, 'JPY', date='2010-12-31')
    print(response, end='\n\n')
    response = test.convert(1000.0, base='JPY', target='JPY')
    print(response, end='\n\n')
    response = test.convert(1000.0, base='EUR', target='JPY', date='2010-12-31')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', base='USD')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', symbols='JPY')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', base='USD', symbols='EUR, JPY')
    print(response, end='\n\n')
    response = test.get_rates(date='latest', base='USD', symbols=['EUR', 'JPY'])
    print(response, end='\n\n')


if __name__ == '__main__':
    main()
