import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='python_advanced_logger',
    version='0.9',
    packages=['python_advanced_logger', 'python_advanced_logger.tests'],
    url='http://python-advanced-logger.readthedocs.org/en/latest/',
    license='GPLv2',
    author='Dan Strohl',
    author_email='dan@wjcg.net',
    description='A set of python utilities for more advanced logging.',
    long_description=read('README.rst'),
    tests_require=['testfixtures'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Logging'
    ],
    keywords='log LogAdapter indent logger logging extension plugin helper Logger readable'
)
