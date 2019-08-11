import argparse
import bs4
import collections
import pyperclip
import sys
import urllib
import urllib.request


# consts

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

url_container = { 'aclweb' : 'https://aclweb.org/anthology/events/{0}-{1}',\
                  'dblp' : 'https://dblp.org/db/conf/{0}/{0}{1}.html'}

selector = {'aclweb' : 'a[class="align-middle"]',\
            'dblp' : 'span[class="title"]'}

keywords = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg',\
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



# get args when executed via command-line

def get_args():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    group_output = parser.add_mutually_exclusive_group()
    group_less = parser.add_mutually_exclusive_group()
    parser.add_argument(dest='conference', help='specify one conference (e.g. acl)')
    parser.add_argument(dest='year', help='specify one year (e.g. 2019)')
    parser.add_argument('-q', '--quiet', help='be more quiet', action='store_true', dest='quiet')
    parser.add_argument('--copy', help='copy result to clipboard', action='store_true', dest='copy')
    group_output.add_argument('-m', '--md', '--markdown', help='output as markdown links\ncollaborates with --url-only\nignores --title-only\n', action='store_true', dest='markdown')
    group_output.add_argument('--html', help='output as HTML <a> tags\ncollaborates with --url-only\nignores --title-only\n', action='store_true', dest='html')
    group_less.add_argument('--title-only', help='output paper title only', action='store_true', dest='title_only')
    group_less.add_argument('--url-only', help='output paper URL only', action='store_true', dest='url_only')
    args = parser.parse_args()
    return args



# throw HTTP request

def medicalai(conference, year, *config):
    # <input>
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
    #   year: str or int (1965 or greater)
    #
    #   *config: argparse.Namespace object (optional)
    #
    # <output>
    #   collections.OrderedDict {<PAPER_TITLE>:<PAPER_URL>}
    
    global conferences
    global sources
    global url_container

    class Query():
        def __init__(self):
            self.conference = None
            self.year = None
            self.res = None
            self.config = None
            self.url = None
            self.source = None

    query = Query()
    query.conference = conference.lower()
    query.year = str(year)
    query.config = config[0]
    
    # check conference name
    try:
        query.source = sources[conference]
        query.url = url_container[query.source].format(query.conference, query.year)

        # make a connection
        print('Connecting...')
        try:
            with urllib.request.urlopen(query.url) as res:
                medicalai_parse(res, query)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))

    except KeyError:
        seps = '=' * 35
        print("Error: unavailable conference '{}'.".format(query.conference))
        print(seps)
        print('Available conferences:')
        print('\tML, AI:\n\t\t{}'.format(', '.join(conferences['ML'])))
        print('\tCV:\n\t\t{}'.format(', '.join(conferences['CV'])))
        print('\tNLP:\n\t\t{}'.format(', '.join(conferences['NLP'])))
        print(seps)
        

# process received HTTP response
        
def medicalai_parse(res, query):
    global selector
    global keywords
    prev_title = ''
    n_total = 0
    seps = '=' * 35
    result = collections.OrderedDict()
    
    # get html content
    html = res.read()
    soup = bs4.BeautifulSoup(html, 'html5lib')
    
    # extract articles
    for tag in soup.select(selector[query.source]):
        n_total += 1
        skip = False
        title = tag.getText()
        if title != prev_title:
            for keyword in keywords:
                if not skip:
                    for kw in (keyword, keyword.upper(), keyword.capitalize()):
                        if (((' ' + kw) in title) or title.startswith(kw)) and (not skip):
                            if query.source == 'aclweb':
                                link = tag.attrs['href']
                                if link.startswith('/anthology/paper'):
                                    result[title] = 'https://aclweb.org' + link
                                    skip = True
                                    prev_title = title
                                    break
                            elif query.source == 'dblp':
                                link = tag.parent.parent.contents[2].ul.li.div.a['href']
                                result[title] = link
                                skip = True
                                prev_title = title
                                break
        if not query.config.quiet:
            sys.stdout.write('\rSearching... {} match / {}'.format(len(result), n_total))
            sys.stdout.flush()

    # prepare output display
    output = ''
    if result:
        if query.config.markdown:
            if query.config.url_only:
                output = '\n'.join([ '[{0}]({0})'.format(url) for url in result.values() ])
            else:
                output = '\n'.join([ '[{0}]({1})'.format(title, url) for title, url in result.items() ])
        elif query.config.html:
            if query.config.url_only:
                output = '<br/>\n'.join([ '<a href="{0}" target="_blank" alt="{0}">{0}</a>'.format(url) for url in result.values() ])
            else:
                output = '<br/>\n'.join([ '<a href="{1}" target="_blank" alt="{0}">{0}</a>'.format(title.replace('"', "'"), url) for title, url in result.items() ])
        else:
            if query.config.title_only:
                output = '\n'.join(list(result.keys()))
            elif query.config.url_only:
                output = '\n'.join(list(result.values()))
            else:
                output = '\n\n'.join([ '{0}\n{1}'.format(title, url) for title, url in result.items() ])
    else:
        output = 'No medical-like AI papers found.'
            

    # display output
    if query.config.quiet:
        if result:
            print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(result), n_total))
        else:
            print(output)
    else:
        sys.stdout.write('\n')
        if result:
            print(seps)
            print(output)
            print(seps)
            print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(result), n_total))
            print(seps)
        else:
            print(output)

            
    # copy onto clipboard if needed
    if query.config.copy:
        pyperclip.copy(output)
        print(' * * * Copied this result to clipboard * * *')

    # return OrderedDict
    return result


if __name__ == '__main__':
    config = get_args()
    medicalai(config.conference, config.year, config)
