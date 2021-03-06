import os
import uuid
import json
import random

import web
from jinja2 import Environment, Template, FileSystemLoader

from config import settings
from blast import get_blast_databases, run_blast, get_sequence_from_database, process_blast_result, get_blast_database_from_title, poll

NBLAST = ('blastn', 'tblastn', 'tblastx',)
PBLAST = ('blastp', 'blastx',)

settings = settings()

'''
urls = (
    '{}'.format(settings.get('BASE_URL')), 'index',
    '{}results/(.*)/'.format(settings.get('BASE_URL')), 'results',
    '{}run/(.*)/'.format(settings.get('BASE_URL')), 'start_blast',
    '{}status/(.*)/'.format(settings.get('BASE_URL')), 'status',
    '{}sequence/(.*)/(.*)/'.format(settings.get('BASE_URL')), 'sequence',
    '{}multisequence'.format(settings.get('BASE_URL')), 'multisequence',
    )
'''

#app = web.application(urls, globals())
#application = app.wsgifunc()

def render_template(template_name, base_template=None, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    if base_template is not None and base_template != 'base.html':
        context['layout_template'] = Template(open(base_template).read())
    else:
        context['layout_template'] = 'base.html'

    location = os.path.join(os.path.dirname(__file__), 'templates')

    jinja_env = Environment(
        loader=FileSystemLoader(location),
        extensions=extensions,
        )

    jinja_env.filters['startswith'] = startswith

    jinja_env.globals.update(globals)

    return jinja_env.get_template(template_name).render(context)

def startswith(value, start):
    return value.startswith(start)

class index:
    def POST(self):
        return self.GET()

    def GET(self):
        databases = get_blast_databases(settings.get('BLAST_EXECUTABLE_PATH'), settings.get('BLAST_DATABASE_PATH'))
        programs = {'nucleotide': NBLAST, 'protein': PBLAST}
        qs = web.input()
        identifier = qs.get('settings')
        db = qs.get('db', '')
        pgrm = qs.get('pgrm', '')
        seq = qs.get('seq', '')
        adv = ''
        if identifier is not None:
            with open('{0}{1}.json'.format(settings.get('BLAST_RESULTS_PATH'), identifier)) as sp:
                opt = json.loads(sp.read())
                db = opt['database']
                pgrm = opt['program']
                seq = opt['sequence']
                adv = opt['advanced']
        return render_template('index.html', 
            base_template = settings.get('BASE_TEMPLATE'),
            settings = settings,
            title="pyBlast | Enter sequence to BLAST", 
            databases = databases,
            programs = programs,
            uuid = uuid.uuid4(), 
            db = db,
            pgrm = pgrm,
            sequence = seq,
            advanced = adv, 
            rndm = random.random(), 
        )

class results:
    def POST(self, identifier):
        options = web.input()
        return render_template('results_container.html', 
            base_template = settings.get('BASE_TEMPLATE'),
            settings = settings,
            title="pyBlast | BLAST results", 
            identifier = identifier,
            options = json.dumps(options),
            execute = True,
            rndm = random.random(), 
        )

    def GET(self, identifier):
        file_loc = "{0}{1}.xml".format(settings.get('BLAST_RESULTS_PATH'), identifier)
        qs = web.input()
        cutoff = qs.get('cutoff')
        processed = None
        exists = False
        with open(file_loc) as results:
            if cutoff is not None:
                processed = process_blast_result(results.read(), cutoff=float(cutoff)) 
            else:
                processed = process_blast_result(results.read())            
            exists = True
        return render_template('results_container.html', 
            base_template = settings.get('BASE_TEMPLATE'),
            settings = settings,
            title="pyBlast | BLAST results", 
            identifier = identifier,
            rndm = random.random(), 
            uuid = uuid.uuid4(),
            results = processed,
            exists = exists,
        )

class start_blast:
    def POST(self, identifier):
        options = web.input()
        web.header('Content-type', 'application/json')
        try:
            database = get_blast_database_from_title(settings.get('BLAST_EXECUTABLE_PATH'),settings.get('BLAST_DATABASE_PATH'),options.database)
            #database = settings.get('BLAST_DATABASE_PATH')+options.database
            program = settings.get('BLAST_EXECUTABLE_PATH')+options.program
            sequence = options.sequence
            advanced = options.advanced
            out, err = run_blast(database, program, settings.get('BLAST_RESULTS_PATH'), identifier, sequence, advanced)
            with open('{0}/{1}.json'.format(settings.get('BLAST_RESULTS_PATH'), identifier), 'w+') as sp:
                sp.write(json.dumps({
                    'database': options.database,
                    'program': options.program,
                    'sequence': sequence,
                    'advanced': advanced,
                }))
            return json.dumps({'running': True, 'out': out, 'err': err})
        except KeyError:
            web.ctx.status = 400
            return json.dumps({'running': False})

class status:
    def GET(self, identifier):
        web.header('Content-type', 'application/json')
        file_loc = "{0}{1}.xml".format(settings.get('BLAST_RESULTS_PATH'), identifier)
        qs = web.input()
        cutoff = qs.get('cutoff')
        with open(file_loc) as results:
            '''
            if cutoff is not None:
                processed = process_blast_result(results.read(), cutoff=float(cutoff)) 
            else:
                processed = process_blast_result(results.read())            
            
            results_page = render_template('results.html', 
                settings = settings,
                results = processed,
                uuid = uuid.uuid4(), 
                identifier = identifier,
            )
            '''
            return json.dumps({'active': False}) #, 'results': processed, 'results_page': results_page})
        return json.dumps({'active': False, 'err': 'There has been an error'})

class sequence:
    def GET(self, db, sequence):
        seqs = sequence.split(',')
        results = []
        for s in seqs:
            results.append([s, get_sequence_from_database(settings.get('BLAST_EXECUTABLE_PATH'), settings.get('BLAST_DATABASE_PATH')+db, s)])
        return render_template('sequences.html',
            base_template = settings.get('BASE_TEMPLATE'),
            settings = settings,
            title = 'pyBlast | Retrieved sequences',
            results = results,
        )

class multisequence:
    def GET(self):
        qs = web.input(sequences=[])
        seqs = u','.join(qs.sequences)
        s = sequence()
        return s.GET(qs.db, seqs)

app = None

def run(overidden_settings={}, run_server=False):
    settings.merge(overidden_settings)
    urls = (
        '{}'.format(settings.get('BASE_URL')), 'index',
        '{}results/(.*)/'.format(settings.get('BASE_URL')), 'results',
        '{}run/(.*)/'.format(settings.get('BASE_URL')), 'start_blast',
        '{}status/(.*)/'.format(settings.get('BASE_URL')), 'status',
        '{}sequence/(.*)/(.*)/'.format(settings.get('BASE_URL')), 'sequence',
        '{}multisequence/'.format(settings.get('BASE_URL')), 'multisequence',
        )
    app = web.application(urls, globals())
    if run_server:
        app.run()
    else:
        return app.wsgifunc()

if __name__ == '__main__':
    app.run()
