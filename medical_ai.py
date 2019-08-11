import argparse
import bs4
import collections
import pyperclip
import sys
import urllib
import urllib.request

'''
class Modality():
    def __init__(self):
        self.conferences = []

class Conference():
    def __init__(self):
        self.source = None

class Source():
    def __init__(self):
        self.source = None

nlp = Modality()
cv = Modality()
acl = Conference()
'''
        
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


queries = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg',\
           'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',\
           'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'patho', 'x-ray', 'x-Ray', 'mammogr', 'CT', 'MRI', 'radiograph', 'tomograph',\
           'magnetic']



description='''
++++++++++++++++++++++++++++++++++++++++++++++++++
Pickup medical AI papers from specified conference and year.
会議名と年数を指定すると, 医療に関連するAI論文のみを探し出して列挙します.

To get from ACL 2019, input like this: python3 medical_ai.py acl 2019
例えばACL 2019採択論文から探すには本プログラムを python3 medical medical_ai.py acl 2019 と実行してください.

Conference name is case insensitive.
会議名は大文字でも小文字でも構いません.

To specify multiple conferences and year or copy results on clipboard, use options shown below.
以下に示すオプションを使うと, 複数の国際会議や年度を一括で検索したり, 結果をクリップボードにコピーしたりすることも可能です.
++++++++++++++++++++++++++++++++++++++++++++++++++
'''

def get_args():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('conference', help='specify one conference (e.g. acl)')
    parser.add_argument('year', help='specify one year (e.g. 2019)')
    #parser.add_argument('-c', '--conference', help='specify one or more conferences (e.g. acl)', metavar='<conferences>', type=str)
    #parser.add_argument('-y', '--year', help='specify one or more years (e.g. 2019)', metavar='<years>', type=int)
    #parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()
    return args

def medicalai(args, verbose=True, toclipboard=False):
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
    
    conference = args.conference.lower()
    year = str(args.year)
  
    global conferences
    global sources
    
    urls = { 'aclweb' : 'https://aclweb.org/anthology/events/{}-{}'.format(conference, year),\
             'dblp' : 'https://dblp.org/db/conf/{0}/{0}{1}.html'.format(conference, year)}

    
    # check conference name
    try:
        source = sources[conference]

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
    global queries

    result = collections.OrderedDict()
    prev_title = ''
    n_total = 0
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
                                    result[title] = 'https://aclweb.org' + link
                                    skip = True
                                    prev_title = title
                                    break
                            elif source == 'dblp':
                                link = tag.parent.parent.contents[2].ul.li.div.a['href']
                                result[title] = link
                                skip = True
                                prev_title = title
                                break
        if verbose:
            sys.stdout.write('\rSearching... {} match / {}'.format(len(result), n_total))
            sys.stdout.flush()
        
    # result of search    
    if verbose:
        sys.stdout.write('\n')
        if result:
            print(seps)
            for key, val in result.items():
                print('{}\n{}\n'.format(key, val))
            print(seps)
            print('Medical-like AI papers: {} / {}'.format(len(result), n_total))
            print(seps)
        else:
            print('No medical-like AI papers found.')

    #if toclipboard:
        #pyperclip.copy('\n\n'.join(['\n'.join(r) for r in result]))
    
    return result


if __name__ == '__main__':
    args = get_args()
    medicalai(args)
    #medicalai([args.conference, args.year], toclipboard=input('Copy result on clipboard? (y/n) : '))
