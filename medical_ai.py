import bs4
import pyperclip
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
    #      'ws', 'alta', 'coling', 'hlt',
    #      'ijcnlp', 'jep-taln-recital', 'lrec',
    #      'muc', 'paclic', 'ranlp',
    #      'rocling-ijclclp', 'tinlap', 'tipster')
    #
    #     for machine learning conferences:
    #     ('nips', 'icml', 'iclr', 'ijcnn', 'ijcai')
    #
    #     for computer vision conferences:
    #     ('cvpr', 'iccv')
    #
    #    year: str or int
    #      (1965 or greater)
    #
    # verbose: bool
    #   print extracted articles if set True
    #
    # toclipboard: bool
    #   copy paper names and URLs on clipboard if set True
    
    conference, year = conference_and_year

    conferences = { 'NLP' : ['acl', 'anlp', 'cl', 'conll', 'eacl', 'emnlp', 'naacl',\
                             'semeval', 'tacl', 'ws', 'alta', 'coling', 'hlt',\
                             'ijcnlp', 'jep-taln-recital', 'lrec', 'muc', 'paclic', 'ranlp',\
                            'rocling-ijclclp', 'tinlap', 'tipster'],\
                    'ML' : ['nips', 'icml', 'iclr', 'ijcnn', 'ijcai'],\
                    'CV' : ['cvpr', 'iccv']}

    sources = {}

    for conf in conferences['NLP']:
        sources[conf] = 'aclweb'
    for conf in conferences['ML']:
        sources[conf] = 'dblp'
    for conf in conferences['CV']:
        sources[conf] = 'dblp'
    
    urls = { 'aclweb' : 'https://aclweb.org/anthology/events/{}-{}'.format(conference.lower(), str(year)),\
             'dblp' : 'https://dblp.org/db/conf/{0}/{0}{1}.html'.format(conference.lower(), str(year))}

    
    # check conference name
    try:
        source = sources[conference.lower()]

        # make a connection
        if verbose:
            print('Connecting...')
        try:
            with urllib.request.urlopen(urls[source]) as res:
                medicalai_parse(res, verbose, toclipboard, source)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))

    except KeyError:
        seps = '=' * 35
        print("Error: unavailable conference '{}'.".format(conference))
        print(seps)
        print('Available conferences:')
        print('\tML, AI:\n\t\t{}'.format(', '.join(conferences['ML'])))
        print('\tCV:\n\t\t{}'.format(', '.join(conferences['CV'])))
        print('\tNLP:\n\t\t{}'.format(', '.join(conferences['NLP'])))
        print(seps)
        

def medicalai_parse(res, verbose, toclipboard, source):
    # get html content
    html = res.read()
    soup = bs4.BeautifulSoup(html, 'html5lib')
    
    # query
    queries = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg',
               'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',
               'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'patho', 'x-ray', 'x-Ray', 'mammogr', 'CT', 'MRI', 'radiograph', 'tomograph',
               'magnetic']

    result = []
    prev_title = ''
    n_total = 0
    n_match = 0
    seps = '=' * 35

    selector = {'aclweb' : 'a[class="align-middle"]',\
                'dblp' : 'span[class="title"]'}
    
    # extract articles
    for tag in soup.select(selector[source]):
        n_total += 1
        skip = False
        title = tag.getText()
        if title != prev_title:
            for query in queries:
                if not skip:
                    for q in (query, query.upper(), query.capitalize()):
                        if (((' ' + q) in title) or title.startswith(q)) and (not skip):
                            if source == 'aclweb':
                                link = tag.attrs['href']
                                if link.startswith('/anthology/paper'):
                                    result.append([title, 'https://aclweb.org' + link])
                                    n_match += 1
                                    skip = True
                                    prev_title = title
                                    break
                            elif source == 'dblp':
                                link = tag.parent.parent.contents[2].ul.li.div.a['href']
                                result.append([title, link])
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
            print(seps)
            print('\n\n'.join(['\n'.join(r) for r in result]))
            print(seps)
            print('Medical-like AI papers: {} / {}'.format(n_match, n_total))
            print(seps)
        else:
            print('No medical-like AI papers found.')

    if toclipboard:
        pyperclip.copy('\n\n'.join(['\n'.join(r) for r in result]))
    
    return result


if __name__ == '__main__':
    medicalai(input("Input conference name and year (e.g. 'naacl 2019') : ").split(),
           toclipboard=bool(input('Copy result on clipboard? (True/False) : ')))
