from setuptools import setup

setup(
    name='WebServerStatusCheckerAJM',
    version='1.2',
    packages=['WebServerStatusCheckerAJM'],
    url='https://github.com/amcsparron2793-Water/WebServerStatusCheckerAJM',
    download_url='https://github.com/amcsparron2793-Water/WebServerStatusCheckerAJM/archive/refs/tags/1.2.tar.gz',
    keywords=['Web Server', 'Server Status', 'Django Server', 'Apache Server'],
    install_requires=['requests', 'EasyLoggerAJM'],
    license='MIT License',
    author='Amcsparron',
    author_email='amcsparron@albanyny.gov',
    description='Pings a machine to see if it is up, then checks for the presence of a given http server '
                '(originally conceived for use with Django and Apache).'
)
