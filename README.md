# pyBlast

pyBlast is a python based frontend for the BLAST+ suite of programs from NCBI.

## Features

- Visual display of sequences
- Easy extraction of sequences from the database
- Fully compatible with existing BLAST databases
- Return to previous BLAST results once search complete
- Fairly easy to set up

## Requirements

- Python 2.7
- web.py 
- jinja2
- lxml

## Setup

These instructions are for running under nginx and uwsgi. It will run under Apache or another wsgi server but you are required to consult their documentation.

## Installing pyBlast

You can get pyBlast currently from GitHub (it will be avilable on pypi soon).

```
pip install git+https://github.com/tjomasc/pyblast.git#egg=pyblast
```

You are then required to configure pyBlast for use. An example file is provided below with clarification of the options you can customise:

```
from pyblast import app

settings = {
        'BLAST_EXECUTABLE_PATH': 'blast/',
        'BLAST_DATABASE_PATH': 'db/',
        'BLAST_RESULTS_PATH': 'store/',
        'BASE_TEMPLATE': 'base.html',
        'BASE_URL': '/',
        'STATIC_URL': '/static/',
    }

application = app.run(overidden_settings=settings)
```

Place this in a directory for your site (e.g. `/srv/www/example.org/`) called, for example `run.py`. This will be the point of access for your server.


### Configuration options

**IMPORTANT**: All paths must end in a slash (/).

- `BLAST_EXECUTABLE_PATH`: The path that contains the BLAST+ executables.
- `BLAST_DATABASE_PATH`: The path to a directory containing the BLAST databases.
- `BLAST_RESULTS_PATH`: A path to a writable directory for storing the BLAST results (stored as XML and JSON files).
- `BASE_TEMPLATE`: A path to a template to be used to integrate pyBlast into your web sites layout. See the examples folder for an example and template. _(Optional)_
- `BASE_URL`: By default the pyBlast application will assume that it is in the root (/) of your domain. To run in another location you can specify this here (e.g. /blast/)
- `STATIC_URL`: The location of the static files. This allows the server reference the files correctly. See server setup below for why this can be required.

### Server setup with nginx and uwsgi

#### uwsgi

You will need to run uwsgi as a service or similar, on Ubuntu I use upstart so the following would go in `/etc/init/example_blast.conf`:

```
uwsgi --master --socket /var/run/blast.sock --chmod-socket --workers 5 \
 --pythonpath /srv/www/example.org/ --module run \
 --logto /srv/www/example.org/logs/wsgi-blast.log
```

#### nginx

```
server {
    listen 80;
    server_name blast.example.org;
    
    location /static {
        alias /srv/www/example.org/static;
    }

    location / {
        uwsgi_pass unix:///var/run/example.sock;
        include uwsgi_params;
    }
    
    # In this case there is already a site at example.org and so
    # we run blast under /blast/

    location /blast/ {
        uwsgi_pass unix:///var/run/blast.sock;
        include uwsgi_params;
    }
    
    # There are already files in /static/ from the example.org
    # site so we put ours under /staric/blast.
    # Don't forget to change the STATIC_URL setting if you
    # do this

    location /static/blast {
        alias /usr/local/lib/python2.7/site-packages/pyblast/static;
    }
}
```

You can either refer to the static files in the python package (as shown above) OR copy the files to a directory of your choosing and refer to them there.


## TODOs

- No clearing of old results implemented
- A good chance there are still bugs lurking!
