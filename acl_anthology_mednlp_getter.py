import bs4
import pyperclip
import sys
import urllib
import urllib.request

def mednlp(conference_and_year, verbose=True, toclipboard=False):
    # conference_and_year: list or tuple
    #   (conference, year) where:
    #
    #   conference: str
    #     ('acl', 'anlp', 'cl', 'conll', 'eacl',
    #      'emnlp', 'naacl', 'semeval', 'tacl',
    #      'ws', 'sigs', 'alta', 'coling', 'hlt',
    #      'ijcnlp', 'jep-taln-recital', 'lrec',
    #      'muc', 'paclic', 'ranlp',
    #      'rocling-ijclclp', 'tinlap', 'tipster')
    #
    #    year: str or int
    #      (1965 or greater)
    #
    # verbose: bool
    #   print extracted articles if set True
    
    conference, year = conference_and_year

    conferences = ['acl', 'anlp', 'cl', 'conll', 'eacl', 'emnlp', 'naacl',\
                   'semeval', 'tacl', 'ws', 'sigs', 'alta', 'coling', 'hlt',\
                   'ijcnlp', 'jep-taln-recital', 'lrec', 'muc', 'paclic', 'ranlp',\
                   'rocling-ijclclp', 'tinlap', 'tipster']

    if conference.lower() not in conferences:
        print("Error: cannot find conference '{}'.\nAvailable conferences: {}.".format(conference, ', '.join(conferences)))
    else:
        # get html content
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


def mednlp_parse(res, verbose=True, toclipboard=False):
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
    if verbose:
        sys.stdout.write('\n')

        
    # result of search    
    if verbose:
        if len(result) > 0:
            print('\n\n'.join(['\n'.join(r) for r in result]))
        else:
            print('No medical NLP papers found.')

    if toclipboard:
        pyperclip.copy('\n\n'.join(['\n'.join(r) for r in result]))
    
    return result

if __name__ == '__main__':
    mednlp(input("Input conference name and year (e.g. 'naacl 2019') : ").split(),
           toclipboard=bool(input('Copy result on clipboard? (True/False) : ')))
