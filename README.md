# pyBlast

pyBlast provides the ability to run BLAST searches and retrieve results for Django .

## Requirements

- Python 2.7
- Django 1.4+
- pyjade
- lxml

## Setup

- A path to the folder where the blast databases are stored. Must end with a /
```
BLAST_DB_PATH = '/Users/work/Projects/pyBlast/db/'
```
- A path to the folder where the blast executables are stored. Must end with a /
```   
BLAST_EXE_PATH = '/Users/work/Projects/pyBlast/bin/'
```
- A path to the folder where the results from a blast search are to be stored. Must end with a /
```
BLAST_RESULTS_STORE = '/Users/work/Projects/pyBlast/store/'
```
- Make sure you have pyjade enaabled
```
TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
```
