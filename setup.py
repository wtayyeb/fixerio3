from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='fixerio3',
      version='0.0.1',
      description='A python3 API to interact with the fixer.io foreign exchange rates and currency conversion JSON API',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Financial and Insurance Industry',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent'
          'Programming Language :: Python :: 3',
          'Topic :: Office/Business :: Financial',
          'Topic :: Software Development :: Build Tools',
      ],
      keywords=[
          'forex',
          'api',
          'currencies',
          'financial',
      ],
      url='https://github.com/saporitigianni/fixerio3',
      author='Gianni Saporiti',
      author_email='saporitigianni@outlook.com',
      license='MIT',
      packages=['fixerio3'],
      install_requires=[
          'requests',
      ],
      include_package_data=True,
      zip_safe=False)
