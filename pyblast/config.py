class settings:
    
    settings = {
        'BLAST_EXECUTABLE_PATH': 'blast/',
        'BLAST_DATABASE_PATH': 'db/',
        'BLAST_RESULTS_PATH': 'store/',
        'BASE_TEMPLATE': 'base.html',
        'BASE_URL': '/',
        'STATIC_URL': '/static/',
        'EXTERNAL_DETAILS_URL': '',
        'LINKED_DEFS': [],
    }

    def merge(self, new):
        self.settings.update(**new)

    def get(self, item):
        return self.settings[item]
