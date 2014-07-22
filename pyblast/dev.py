from app import run

PYBLAST_LOC = '/Users/thomas/Projects/pyblast'

settings = {
    #'BASE_TEMPLATE': '/Users/work/Projects/pyBlast/alt_template/base.html',
    'BLAST_EXECUTABLE_PATH': PYBLAST_LOC+'/bin/',
    'BLAST_DATABASE_PATH': PYBLAST_LOC+'/db/',
    'BLAST_RESULTS_PATH': PYBLAST_LOC+'/results/',
    'BASE_URL': '/blast/',
    'EXTERNAL_DETAILS_URL': '/annotations/details',
    'LINKED_DEFS': ['bmy', 'scaffold'],
}

if __name__ == '__main__':
    run(settings, run_server=True)
