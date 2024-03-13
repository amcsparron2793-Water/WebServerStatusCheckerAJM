from setuptools import setup
import re
project_name = 'WebServerStatusCheckerAJM'


def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(project + '/_version.py').read())
    return result.group(1)


setup(
    name=project_name,
    version=get_property('__version__', project_name),
    packages=['WebServerStatusCheckerAJM'],
    url='https://github.com/amcsparron2793-Water/WebServerStatusCheckerAJM',
    download_url=f'https://github.com/amcsparron2793-Water/WebServerStatusCheckerAJM/archive/refs/tags/{get_property("__version__", project_name)}.tar.gz',
    keywords=['Web Server', 'Server Status', 'Django Server', 'Apache Server'],
    install_requires=['requests', 'EasyLoggerAJM'],
    license='MIT License',
    author='Amcsparron',
    author_email='amcsparron@albanyny.gov',
    description='Pings a machine to see if it is up, then checks for the presence of a given http server '
                '(originally conceived for use with Django and Apache).'
)
