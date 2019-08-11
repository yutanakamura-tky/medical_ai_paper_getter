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
    def url(self, conference, year):
        return self.source.url(self, conference, year)

class Source():
    def __init__(self):
        self.selector = ''
        self.url_container = ''
    def url(self, conference, year):
        return self.url_container.format(conference, year)

aclweb = Source()
aclweb.selector = 'a[class="align-middle"]'
aclweb.url_container = 'https://aclweb.org/anthology/events/{}-{}'

dblp = Source()
dblp.selector = 'span[class="title"]'
dblp.url_container = 'https://dblp.org/db/conf/{0}/{0}{1}.html'

acl = Conference()
anlp = Conference()
cl = Conference()
conll = Conference()
eacl = Conference()
emnlp = Conference()
naacl = Conference()
semeval = Conference()
tacl = Conference()
ws = Conference()
alta = Conference()
hlt = Conference()
ijcnlp = Conference()
jep-taln-recital = Conference()



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
Pickup medical AI paper titles and URLs from specified conference and year.
会議名と年数を指定すると, 医療に関連するAI論文のみを探し出してタイトルとURLを列挙します.

To get from ACL 2019, input like this: python3 medical_ai.py acl 2019
例えばACL 2019採択論文から探すには本プログラムを python3 medical medical_ai.py acl 2019 と実行してください.

Conference name is case insensitive.
会議名は大文字でも小文字でも構いません.

To output HTML link tags or markdown links, use options below.
以下に示すオプションを使うと, 結果をHTMLリンクタグやMarkdownリンクとして出力することも可能です.
++++++++++++++++++++++++++++++++++++++++++++++++++
'''

def get_args():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(dest='conference', help='specify one conference (e.g. acl)')
    parser.add_argument(dest='year', help='specify one year (e.g. 2019)')
    parser.add_argument('-q', '--quiet', help='be more quiet', action='store_true', dest='quiet')
    parser.add_argument('--copy', help='copy result to clipboard', action='store_true', dest='copy')
    group.add_argument('-m', '--md', '--markdown', help='output as markdown links\ncollaborates with --url-only, ignores --title-only\n', action='store_true', dest='markdown')
    group.add_argument('--html', help='output as HTML <a> tags\ncollaborates with --url-only, ignores --title-only\n', action='store_true', dest='html')
    #parser.add_argument('-c', '--conference', help='specify one or more conferences (e.g. acl)', metavar='<conferences>', type=str)
    #parser.add_argument('-y', '--year', help='specify one or more years (e.g. 2019)', metavar='<years>', type=int)
    #parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()
    return args

def medicalai(args):
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
        print('Connecting...')
        try:
            with urllib.request.urlopen(urls[source]) as res:
                medicalai_parse(res, source, args)
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
        

def medicalai_parse(res, source, args):
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
        if not args.quiet:
            sys.stdout.write('\rSearching... {} match / {}'.format(len(result), n_total))
            sys.stdout.flush()

    # prepare output display
    output = ''
    if result:
        if args.markdown:
            output = '\n'.join([ '[{}]({})\n'.format(title, url) for title, url in result.items() ])
        elif args.html:
            output = '<br/>\n'.join([ '<a href="{1}" target="_blank" alt="{0}">{0}</a>'.format(title.replace('"', "'"), url) for title, url in result.items() ])
        else:
            output = '\n\n'.join([ '{}\n{}'.format(title, url) for title, url in result.items() ])
    else:
        output = 'No medical-like AI papers found.'
            

    # display output
    if args.quiet:
        if result:
            print('Medical-like AI papers in {} {}: {} / {}'.format(args.conference.upper(), args.year, len(result), n_total))
        else:
            print(output)
    else:
        sys.stdout.write('\n')
        if result:
            print(seps)
            print(output)
            print(seps)
            print('Medical-like AI papers in {} {}: {} / {}'.format(args.conference.upper(), args.year, len(result), n_total))
            print(seps)
        else:
            print(output)

            
    # copy onto clipboard if needed
    if args.copy:
        pyperclip.copy(output)
        print('Copied this result to clipboard.')

    # return OrderedDict
    return result


if __name__ == '__main__':
    args = get_args()
    medicalai(args)
    #medicalai([args.conference, args.year], toclipboard=input('Copy result on clipboard? (y/n) : '))
