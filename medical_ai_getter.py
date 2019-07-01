import bs4
import pyperclip
import re
import sys
import urllib
import urllib.request

def medicalai(conference_and_year, verbose=True, toclipboard=False):
    # conference_and_year: list or tuple
    #   (conference, year) where:
    #
    #   conference: str
    #
    #     for natural language processing conferences:
    #     ('acl', 'anlp', 'cl', 'conll', 'eacl',
    #      'emnlp', 'naacl', 'semeval', 'tacl',
    #      'ws', 'sigs', 'alta', 'coling', 'hlt',
    #      'ijcnlp', 'jep-taln-recital', 'lrec',
    #      'muc', 'paclic', 'ranlp',
    #      'rocling-ijclclp', 'tinlap', 'tipster')
    #
    #     for machine learning conferences:
    #     ('nips', 'icml', 'iclr', 'ijcnn', 'aaai', 'ijcai')
    #
    #    year: str or int
    #      (1965 or greater)
    #
    # verbose: bool
    #   print extracted articles if set True
    
    conference, year = conference_and_year

    conferences = { 'NLP' : ['acl', 'anlp', 'cl', 'conll', 'eacl', 'emnlp', 'naacl',\
                   'semeval', 'tacl', 'ws', 'sigs', 'alta', 'coling', 'hlt',\
                   'ijcnlp', 'jep-taln-recital', 'lrec', 'muc', 'paclic', 'ranlp',\
                            'rocling-ijclclp', 'tinlap', 'tipster'],\
                    'ML' : ['nips', 'icml', 'iclr', 'ijcnn', 'aaai', 'ijcai']}

    if conference.lower() in conferences['NLP']:
        url = 'https://aclweb.org/anthology/events/{}-{}'.format(conference.lower(), str(year))
        if verbose:
            print('Connecting...')
        try:
            with urllib.request.urlopen(url) as res:
                mednlp_parse(res, verbose, toclipboard)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))
        
    elif conference.lower() in conferences['ML']:
        url = 'https://dblp.org/db/conf/{0}/{0}{1}.html'.format(conference.lower(), str(year))
        print(url)
        if verbose:
            print('Connecting...')
        try:
            with urllib.request.urlopen(url) as res:
                medml_parse(res, verbose, toclipboard)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))
        
    else:
        print("Error: cannot find conference '{}'.\nAvailable conferences: {}.".format(conference, ', '.join(conferences['NLP']+conferences['ML'])))



def mednlp_parse(res, verbose=True, toclipboard=False):
    # get html content
    html = res.read()
    soup = bs4.BeautifulSoup(html, 'html5lib')
    
    # query
    queries = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg',
               'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',
               'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'x-ray', 'CT', 'MRI', 'radiograph', 'tomograph',
               'magnetic']
        
    result = []
    prev_title = ''
    n_total = 0
    n_match = 0
    spacer = '=' * 30
               
    # extract articles
    for tag in soup.select('a[class="align-middle"]'):
        n_total += 1
        skip = False
        title = tag.getText()
        if title != prev_title:
            for query in queries:
                if not skip:
                    for q in (query, query.upper(), query.capitalize()):
                        if (((' ' + q) in title) or title.startswith(q)) and (not skip):
                            link = tag.attrs['href']
                            if link.startswith('/anthology/paper'):
                                result.append([title, 'https://aclweb.org' + link])
                                n_match += 1
                                skip = True
                                prev_title = title
                                break
        if verbose:
            sys.stdout.write('\rSearching... {} match / {}'.format(n_match, n_total))
            sys.stdout.flush()
        
    # result of search    
    if verbose:
        sys.stdout.write('\n')
        if n_match > 0:
            print(spacer)
            print('\n\n'.join(['\n'.join(r) for r in result]))
            print(spacer)
            print('Medical-like NLP papers: {} / {}'.format(n_match, n_total))
            print(spacer)
        else:
            print('No medical NLP papers found.')

    if toclipboard:
        pyperclip.copy('\n\n'.join(['\n'.join(r) for r in result]))
    
    return result


def medml_parse(res, verbose=True, toclipboard=False):
    # get html content
    html = res.read()
    soup = bs4.BeautifulSoup(html, 'html5lib')
    
    # query
    queries = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg',
               'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',
               'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'x-ray', 'CT', 'MRI', 'radiograph', 'tomograph',
               'magnetic']
        
    result = []
    prev_title = ''
    n_total = 0
    n_match = 0
    spacer = '=' * 30

    #regexp_title = re.compile(r'<span class="title" itemprop="name">(.+?)</span>')
    #regexp_link = re.compile(r'<li class="drop-down">(.+?)<a href="(.+?)">(.+?)</li>')
               
    # extract articles
    for tag in soup.select('span[class="title"]'):
        n_total += 1
        skip = False
        title = tag.getText()
        if title != prev_title:
            for query in queries:
                if not skip:
                    for q in (query, query.upper(), query.capitalize()):
                        if (((' ' + q) in title) or title.startswith(q)) and (not skip):
                            # tag.parent
                            #   -> <div class="data"> ~ </div>
                            # tag.parent.parent
                            #   -> <li class="entry inproceedings"> ~ </li>
                            # tag.parent.parent.contents[2]
                            #   -> <nav class="publ"> ~ </nav>
                            # tag.parent.parent.contents[2].ul
                            #   -> <ul> ~ </ul>
                            # tag.parent.parent.contents[2].ul.li
                            #   -> <li class="dropdown"> ~ </li>
                            # tag.parent.parent.contents[2].ul.li.div
                            #   -> <div class="head"> ~ </div>
                            # tag.parent.parent.contents[2].ul.li.div.a
                            #   -> <a href="..."> ~ </a>
                            link = tag.parent.parent.contents[2].ul.li.div.a['href']
                            result.append([title, link])
                            n_match += 1
                            skip = True
                            prev_title = title
                            break
        if verbose:
            sys.stdout.write('\rSearching... {} {} / {}'.format(n_match, 'matches' if n_match!=1 else 'match', n_total))
            sys.stdout.flush()
        
    # result of search    
    if verbose:
        sys.stdout.write('\n')
        if n_match > 0:
            print(spacer)
            print('\n\n'.join(['\n'.join(r) for r in result]))
            print(spacer)
            print('Medical-like AI papers: {} / {}'.format(n_match, n_total))
            print(spacer)
        else:
            print('No medical AI papers found.')

    if toclipboard:
        pyperclip.copy('\n\n'.join(['\n'.join(r) for r in result]))
    
    return result


if __name__ == '__main__':
    medicalai(input("Input conference name and year (e.g. 'naacl 2019') : ").split(),
           toclipboard=bool(input('Copy result on clipboard? (True/False) : ')))
