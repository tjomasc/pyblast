import subprocess
import base64
import json
import re
import hashlib
import tempfile
import os
from lxml import etree

from math_tools import percentile

def get_blast_databases(exe_loc, db_loc):
    """ 
    Look for BLAST databases using in given path and return a list 

    # Test it!
    >>> get_blast_databases('/Users/work/Projects/pyBlast/bin/', '/Users/work/Projects/pyBlast/db/')
    {'protein': [{'location': '/Users/work/Projects/pyBlast/db/yeast.aa', 'title': 'yeast.aa'}], 'nucleotide': [{'location': '/Users/work/Projects/pyBlast/db/yeast.nt', 'title': 'yeast.nt'}]}
    """
    found = subprocess.check_output([exe_loc+'blastdbcmd', '-list', db_loc, '-list_outfmt', "'%f %p %t'"])
    try:
        found = subprocess.check_output([exe_loc+'blastdbcmd', '-list', db_loc, '-list_outfmt', "'%f %p %t'"])
    except:
        found = ''
    found = [entry.split(' ',2) for entry in re.split(r'\n', re.sub(r'\'', '', found)) if len(entry) > 1] 
    databases = {}
    for f in found:
        if f[1].lower() not in databases:
            databases[f[1].lower()] = []
        databases[f[1].lower()].append({'location': f[0], 'title': f[2]})
    return databases

def get_sequence_from_database(exe_loc, db, seq_id):
    """
    Extract a sequence from the given BLAST database and return it

    # Test:
    >>> get_sequence_from_database('/Users/work/Projects/pyBlast/bin/', '/Users/work/Projects/pyBlast/db/yeast.nt', 'gi|6226515|ref|NC_001224.1|')
    """
    try:
        found = subprocess.check_output([exe_loc+'blastdbcmd', '-db', db, '-entry', seq_id])
    except:
        found = ''
    return found

def parse_extra_options(option_string, exclude=[]):
    """
    Create an list of options filtering out excluded options
    """
    options = re.findall(r'((-\w+) ([\w\d\.]+)?)\s?', option_string)
    extras = []
    for o in options:
        if o[1] not in exclude:
            extras.extend(o[1:])
    return extras

def run_blast(database, program, filestore, file_uuid, sequence, options):
    """ 
    Perform a BLAST search on the given database using the given query 

    # Test:
    >>> seq = ">test\\nTTCATAATTAATTTTTTATATATATATTATATTATAATATTAATTTATATTATAAAAATAATATTTATTATTAAAATATT\\nTATTCTCCTTTCGGGGTTCCGGCTCCCGTGGCCGGGCCCCGGAATTATTAATTAATAATAAATTATTATTAATAATTATT\\n>test 2\\nAATGGTATTAGATTCAGTGAATTTGGTACAAGACGTCGTAGATCTCTGAAGGCTCAAGATCTAATTATGCAAGGAATCATGAAAGCTGTGAACGGTAACCCAGACAGAAACAAATCGCTATTATTAGGCACATCAAATATTTTATTTGCCAAGAAATATGGAGTCAAGCCAATCGGTACTGTGGCTCACGAGTGGGTTATGGGAGTCGCTTCTATTAGTGAAGATTATTTGCATGCCAATAAAAATGCAATGGATTGTTGGATCAATACTTTTGGTGCAAAAAATGCTGGTTTAGCATTAACGGATACTTTTGGAACTGATGACTTTTTAAAATCATTCCGTCCACCATATTCTGATGCTTACGTCGGTGTTAGACAAGATTCTGGAGACCCAGTTGAGTATACCAAAAAGATTTCCCACCATTACCATGACGTGTTGAAATTGCCTAAATTCTCGAAGATTATCTGTTATTCCGATTCTTTGAACGTCGAAAAGGCAATAACTTACTCCCATGCAGCTAAAGAGAATG"
    >>> blast('/Users/work/Projects/pyBlast/db/yeast.nt', '/Users/work/Projects/pyBlast/bin/blastn', '/Users/work/Projects/pyBlast/store/', seq, {u'-evalue': 10.0, u'-strand': u'both'})

    >>> seq = ">test\\nTTC"
    >>> blast('/Users/work/Projects/pyBlast/db/yeast.nt', '/Users/work/Projects/pyBlast/bin/blastn', '/Users/work/Projects/pyBlast/store/', seq, {u'-evalue': 10.0, u'-strand': u'both'})
    
    """

    query = [program, '-db', database, '-outfmt', '5', '-query', '-', '-out', "{0}{1}.xml".format(filestore, file_uuid), '-max_target_seqs', '50']
    exclude = [
        '-db',
        '-query',
        '-out',
        '-subject',
        '-html',
        '-gilist',
        '-negative_gilist',
        '-entrez_query',
        '-remote',
        '-outfmt',
        '-num_threads',
        '-import_search_strategy',
        '-export_search_strategy',
        '-window_masker_db',
        '-index_name',
        '-use_index',
    ]
    extra = parse_extra_options(options, exclude)
    query.extend(extra)

    p = subprocess.Popen(query, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
    stdout, stderr = p.communicate(sequence)

    return (stdout, stderr)

def poll(name):
    """
    Check if the file <name> has been created, indicating BLAST has finished, and return results
    """
    try:
        with open(name) as results:
            if os.path.getsize(name) > 0:
                return results.read()
            raise IOError
    except IOError:
        return False

def chunk_string(s, l=10):
    return [s[i:i+l] for i in range(0,len(s),l)]

def format_bases(bases):
    formatted = ''
    for b in bases:
        formatted += '<span class="base-{}">{}</span>'.format(b,b)
    return formatted
        
def create_formatted_sequences(hsp):

    query = chunk_string(hsp['query_seq'], 60)
    match = chunk_string(hsp['midline'], 60)
    subject = chunk_string(hsp['hit_seq'], 60)

    output = ""
    for ln, line in enumerate(query):

        fpad = len(hsp['hit_from'])
        tpad = len(hsp['hit_to'])
        pad = fpad if fpad > tpad else tpad

        query_from = int(hsp['query_from']) if ln == 0 else int(hsp['query_from'])+(ln*60)
        query_to = query_from+59
        subject_from = int(hsp['hit_from']) if ln == 0 else int(hsp['hit_from'])+(ln*60)
        subject_to = subject_from+59

        qseq = format_bases(line)
        sseq = format_bases(subject[ln])

        output += """
Query    {qsnum}  {qseq}  {qenum}
         {mspad}  {match}
Subject  {ssnum}  {sseq}  {senum}
""".format(qseq=qseq,
    match=match[ln],
    mspad="".join([" " for i in range(pad)]),
    sseq=sseq,
    qsnum=str(query_from).rjust(pad),
    qenum=query_to,
    ssnum=str(subject_from).rjust(pad),
    senum=subject_to
    )

    return output.rstrip()

def process_blast_result(filecontents, cutoff=0.0001):
    """
    With the give contents proccess the blast results into a usable format
    """
    results = {'results':[], 'messages':[]}
    messages = []
    b = etree.fromstring(filecontents)

    # Get BLAST details
    db_loc = b.xpath('string(BlastOutput_db/text())').split('/')
    results['details'] = {
        'program': b.xpath('string(BlastOutput_program/text())'),
        'version': b.xpath('string(BlastOutput_version/text())'),
        'reference': b.xpath('string(BlastOutput_reference/text())'),
        'db': db_loc[-1],
        'query_id': b.xpath('string(BlastOutput_query-ID/text())'),
        'query_def': b.xpath('string(BlastOutput_query-def/text())'),
        'query_length': b.xpath('string(BlastOutput_query-len/text())'),
        'params': {},
    }
    for t in b.findall('BlastOutput_param/Parameters/*'):
        name = t.tag.split('_', 1)
        results['details']['params'][name[-1]] = t.text
    for it in b.findall('BlastOutput_iterations/Iteration'):
        # The file may contain a message, stor that for later use
        if it.find('.//Iteration_message') is not None:
            results['messages'].append(it.find('.//Iteration_message').text)
        else:
            r = {
                'details': {
                    'id': it.xpath('string(Iteration_query-ID/text())'),
                    'def': it.xpath('string(Iteration_query-def/text())'),
                    'length': it.xpath('string(Iteration_query-len/text())'),
                },
                'statistics': {
                    'db_num': b.xpath('string(Iteration_stat/Statistics/Statistics_db-num/text())'),
                    'db_length': b.xpath('string(Iteration_stat/Statistics/Statistics_db-len/text())'),
                    'hsp_length': b.xpath('string(Iteration_stat/Statistics/Statistics_hsp-len/text())'),
                    'eff_space': b.xpath('string(Iteration_stat/Statistics/Statistics_eff-space/text())'),
                    'kappa': b.xpath('string(Iteration_stat/Statistics/Statistics_kappa/text())'),
                    'lambda': b.xpath('string(Iteration_stat/Statistics/Statistics_lambda/text())'),
                    'entropy': b.xpath('string(Iteration_stat/Statistics/Statistics_entropy/text())'),
                },
                'hits': []
            }

            '''
            bit_score = []
            for ht in it.findall('Iteration_hits/Hit'):
                for hs in ht.findall('.//Hsp'):
                    bit_score.append(float(hs.xpath('string(Hsp_bit-score/text())')))
            if show_all:
                bit_score_filter = 0
            else:
                bit_score_filter = percentile(bit_score, 0.25)
            print bit_score_filter
            '''
            for ht in it.findall('Iteration_hits/Hit'):
                h = {
                    'num': ht.xpath('string(Hit_num/text())'),
                    'id': ht.xpath('string(Hit_id/text())'),
                    'def': ht.xpath('string(Hit_def/text())'),
                    'accession': ht.xpath('string(Hit_accession/text())'),
                    'length': ht.xpath('string(Hit_len/text())'),
                    'hsps': [],
                }
                query_from = []
                query_to = []
                for hs in ht.findall('.//Hsp'):
                    hsp = {
                        'num': hs.xpath('string(Hsp_num/text())'),
                        'bit_score': hs.xpath('string(Hsp_bit-score/text())'),
                        'score': hs.xpath('string(Hsp_score/text())'),
                        'evalue': hs.xpath('string(Hsp_evalue/text())'),
                        'query_from': hs.xpath('string(Hsp_query-from/text())'),
                        'query_to': hs.xpath('string(Hsp_query-to/text())'),
                        'hit_from': hs.xpath('string(Hsp_hit-from/text())'),
                        'hit_to': hs.xpath('string(Hsp_hit-to/text())'),
                        'query_frame': hs.xpath('string(Hsp_query-frame/text())'),
                        'hit_frame': hs.xpath('string(Hsp_hit-frame/text())'),
                        'identity': hs.xpath('string(Hsp_identity/text())'),
                        'positive': hs.xpath('string(Hsp_positive/text())'),
                        'gaps': hs.xpath('string(Hsp_gaps/text())'),
                        'align_length': hs.xpath('string(Hsp_align-len/text())'),
                        'query_seq': hs.xpath('string(Hsp_qseq/text())'),
                        'hit_seq': hs.xpath('string(Hsp_hseq/text())'),
                        'midline': hs.xpath('string(Hsp_midline/text())'),
                    }
                    hsp['identity_percent'] = int(hsp['identity'])/float(hsp['align_length'])*100
                    hsp['gaps_percent'] = int(hsp['gaps'])/float(hsp['align_length'])*100
                    '''
                    if hsp['query_from'] < query_from:
                        query_from = hsp['query_from']
                    if hsp['query_to'] > query_to:
                        query_to = hsp['query_to']
                    '''
                    if float(hsp['evalue']) < cutoff: #float(hsp['bit_score']) > bit_score_filter:
                        query_from.append(int(hsp['query_from']))
                        query_to.append(int(hsp['query_to']))
                        hsp['formatted'] = create_formatted_sequences(hsp)
                        h['hsps'].append(hsp)
                if len(h['hsps']) > 0:
                    if sum(query_from) > sum(query_to):
                        h['query_from'] = max(query_from)
                        h['query_to'] = min(query_to)
                    else:
                        h['query_from'] = min(query_from)
                        h['query_to'] = max(query_to)
                    r['hits'].append(h)
            results['results'].append(r)
    return results
