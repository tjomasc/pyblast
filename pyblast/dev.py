from app import run

settings = {
    #'BASE_TEMPLATE': '/Users/work/Projects/pyBlast/alt_template/base.html',
    'BLAST_EXECUTABLE_PATH': '/Users/work/Projects/pyBlast/bin/',
    'BLAST_DATABASE_PATH': '/Users/work/Projects/pyBlast/db/',
    'BLAST_RESULTS_PATH': '/Users/work/Projects/pyBlast/results/',
}

if __name__ == '__main__':
    run(settings)
