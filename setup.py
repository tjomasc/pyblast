import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'pyblast',
    version = '0.1.1',
    packages = ['pyblast'],
    include_package_data = True,
    zip_safe = False,
    license = 'BSD Licence',
    description = 'A python web frontend for BLAST+',
    long_description = README,
    url = 'https://github.com/tjomasc/pyblast',
    author = 'Thomas Craig',
    author_email = 'thomas.craig@tjc.me.uk',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)
