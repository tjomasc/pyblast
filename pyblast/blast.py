import subprocess
import base64
import json
import re
import hashlib
import tempfile
import os
from lxml import etree
import pprint

from math_tools import percentile

def get_blast_databases(exe_loc, db_loc):
    """ 
    Look for BLAST databases using in given path and return a list 

    Args:
        exe_loc: Location (directory) of the BLAST executables.
        db_loc: Directory containing the BLAST DB.
    Returns:
        A dict containing lists of databases available.

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

def get_blast_database_from_title(exe_loc, db_loc, title):
    """
    For a give title get the actual name of the database (it may differ from title)

    Args:
        exe_loc: Location (directory) of the BLAST executables.
        db_loc: Directory containing the BLAST DB.
        title: The title of the BLAST database to search for.
    Returns:
        The location of the BLAST database.

    """
    database_list = get_blast_databases(exe_loc, db_loc)
    flat = []
    for k,l in database_list.iteritems():
        flat.extend(l)
    for d in flat:
        if title == d['title']:
            return d['location'] 
    return False


def get_sequence_from_database(exe_loc, db, seq_id):
    """
    Extract a sequence from the given BLAST database and return it

    Args:
        exe_loc: Directory containing BLAST executables.
        db: The database to get sequence from.
        seq_id: The sequence ID of the sequence to get.
    Returns:
        The sequence if found else an empty string

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

    Args:
        option_string: A string containing extra blast options.
        exclude: Options to exclude from the generated list.
    Returns:
        A list of options except those in exclude

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

    Args:
        database: The database to search (full path).
        program: The program to use (e.g. BLASTN, TBLASTN, BLASTX).
        filestore: The directory to store the XML output.
        file_uuid: A unique identifier for the filename.
        sequence: The sequence to BLAST.
        options: Any extra options to pass to the BLAST executable.
    Returns:
        A tuple containing the stdout and stderr of the program.

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

    Args:
        name: The filename of the file that was created in a BLAST search.
    Returns:
        The file or False if it has not yet been created.
    """
    try:
        with open(name) as results:
            if os.path.getsize(name) > 0:
                return results.read()
            raise IOError
    except IOError:
        return False

def chunk_string(s, l=10):
    """
    Split a string into chunks of a set length.

    Args:
        s: The string to chunk.
        l: The length of the chunks.
    Returns:
        A list containing the string chunks.
    """
    return [s[i:i+l] for i in range(0,len(s),l)]

def format_bases(bases):
    """
    Generate HTML that colours the bases in a string.

    Args:
        bases: A string containing a genetic sequence.
    Returns:
        An HTML string.
    """
    formatted = ''
    for b in bases:
        formatted += '<span class="base-{}">{}</span>'.format(b,b)
    return formatted
        
def create_formatted_sequences(hsp):
    """
    Take a sequence and format it for display.

    Args:
        hsp: A dict containing the sequence information.
    Returns:
        An HTML string of the formatted sequence.
    """

    cl = 60

    query = chunk_string(hsp['query_seq'], cl)
    match = chunk_string(hsp['midline'], cl)
    subject = chunk_string(hsp['hit_seq'], cl)

    output = ""
    for ln, line in enumerate(query):
        query_from = int(hsp['query_from']) if ln == 0 else int(hsp['query_from'])+(ln*cl)
        query_to = query_from+(cl-1)
        subject_from = int(hsp['hit_from']) if ln == 0 else int(hsp['hit_from'])+(ln*cl)
        subject_to = subject_from+(cl-1)

        qseq = format_bases(line)
        sseq = format_bases(subject[ln])

        output += '''
<div class="row">
<pre class="col-xs-1 seq-col-sm">Query

Subject
</pre>
<pre class="col-xs-1 seq-col-sm">{qsnum}

{ssnum}
</pre>
<pre class="col-xs-7 seq-col-lg">{qseq}
{match}
{sseq}
</pre>
<pre class="col-xs-1 seq-col-sm">{qenum}

{senum}
</pre>
</div>
'''.format(qseq=qseq,
    match=match[ln],
    sseq=sseq,
    qsnum=str(query_from),
    qenum=query_to,
    ssnum=str(subject_from),
    senum=subject_to
    )

    return output.rstrip()

def process_blast_result(filecontents, cutoff=0.0001):
    """
    Take a BLAST XML results file and process into a usable dict.

    Args:
        filecontents: The contents of a BLAST XML file.
        cutoff: The cutoff for which a sequence is considered relevant.
    Returns:
        A dict of the results.

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
                    if float(hsp['evalue']) < cutoff: #float(hsp['bit_score']) > bit_score_filter:
                        query_from.append(int(hsp['query_from']))
                        query_to.append(int(hsp['query_to']))
                        hsp['formatted'] = create_formatted_sequences(hsp)
                        hsp['query_chunk'] = chunk_string(hsp['query_seq'], 60)
                        hsp['match_chunk'] = chunk_string(hsp['midline'], 60)
                        hsp['subject_chunk'] = chunk_string(hsp['hit_seq'], 60)
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
