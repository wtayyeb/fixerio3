from fixerio3 import fixerio


def main():
    """ Usage examples for the fixerio modules """
    response = fixerio.convert(10, base='USD', target='EUR', date='2018-01-29', paid_membership=False, access_key=None)
    print(response, end='\n\n')
    response = fixerio.convert(10, target='EUR')
    print(response, end='\n\n')

    response = fixerio.get_rates()
    print(response, end='\n\n')
    response = fixerio.get_rates(symbols='JPY')
    print(response, end='\n\n')
    response = fixerio.get_rates(base='EUR', symbols=None)
    print(response, end='\n\n')
    response = fixerio.get_rates(date='latest', base='USD', symbols='EUR,JPY')
    print(response, end='\n\n')
    response = fixerio.get_rates(date='latest', base='USD', symbols=['EUR', 'JPY'])
    print(response, end='\n\n')


if __name__ == '__main__':
    main()
