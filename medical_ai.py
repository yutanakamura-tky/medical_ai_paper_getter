# -*- coding: utf-8 -*-

import argparse
import bs4
import collections
import pyperclip
import sys
import urllib
import urllib.request


# get args when executed via command-line

def get_args():
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
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    group_output = parser.add_mutually_exclusive_group()
    group_less = parser.add_mutually_exclusive_group()
    parser.add_argument(dest='conferences_and_years', nargs='+', help='speficy conferences and years\n example1: acl 2019\n example2: acl naacl 2019\n example3: acl 2018 2019\n example4: acl naacl 2018 2019')
    parser.add_argument('-q', '--quiet', help='be more quiet', action='store_true', dest='quiet')
    parser.add_argument('--copy', help='copy result to clipboard', action='store_true', dest='copy')
    parser.add_argument('-a', '--all', help='get also non-medical AI papers', action='store_true', dest='all')
    group_output.add_argument('-m', '--md', '--markdown', help='output as markdown links\ncollaborates with --url-only\nignores --title-only\n', action='store_true', dest='markdown')
    group_output.add_argument('--html', help='output as HTML <a> tags\ncollaborates with --url-only\nignores --title-only\n', action='store_true', dest='html')
    group_less.add_argument('--title-only', help='output paper title only', action='store_true', dest='title_only')
    group_less.add_argument('--url-only', help='output paper URL only', action='store_true', dest='url_only')
    args = parser.parse_args()
    return args



# throw HTTP request

def medicalai(conference, year, *config):
    # <input>
    #   conference: str or list
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
    #   year: str or int or list (1965 or greater)
    #
    #   *config: argparse.Namespace object (optional)
    #
    # <output>
    #   collections.OrderedDict {<PAPER_TITLE>:<PAPER_URL>}

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

    class Query():
        def __init__(self):
            self.conference = None
            self.year = None
            self.res = None
            self.config = None
            self.url = None
            self.source = None

    queries = []

    if type(conference) is not list:
        conference = [conference]
    if type(year) is not list:
        year = [year]

    for c in conference:
        for y in year:
            query = Query()
            query.conference = c.lower()
            query.year = str(y)
            query.config = config[0]
            
            # check conference name
            try:
                query.source = sources[query.conference]
                query.url = url_container[query.source].format(query.conference, query.year)
                queries.append(query)
            except KeyError:
                seps = '=' * 35
                print("Error: unavailable conference '{}'.".format(query.conference))
                print(seps)
                print('Available conferences:')
                print('\tML, AI:\n\t\t{}'.format(', '.join(conferences['ML'])))
                print('\tCV:\n\t\t{}'.format(', '.join(conferences['CV'])))
                print('\tNLP:\n\t\t{}'.format(', '.join(conferences['NLP'])))
                print(seps)
                
    
    # make connections
    for q in queries:
        print('Connecting for {} {} ...'.format(q.conference.upper(), q.year))
        try:
            with urllib.request.urlopen(q.url) as res:
                medicalai_parse(res, q)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))

        

# process received HTTP response
        
def medicalai_parse(res, query):
    selector = {'aclweb' : 'a[class="align-middle"]',\
                'dblp' : 'span[class="title"]'}

    keywords = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'EHR', 'MeSH', 'RCT', 'life', 'care', 'pharm', 'food-drug', 'drug', 'surg',\
                'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',\
                'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'patho', 'autopsy', 'x-ray', 'x-Ray', 'mammogr', 'CT', 'MRI', 'radiograph', 'tomograph',\
                'magnetic']

    url_getter = {'aclweb' : lambda tag: 'https://aclweb.org' + tag.attrs['href'] if tag.attrs['href'].startswith('/anthology/paper') else None,\
                  'dblp' : lambda tag: tag.parent.parent.contents[2].ul.li.div.a['href']}
    
    prev_title = ''
    n_total = 0
    seps = '=' * 35
    result = collections.OrderedDict()
    
    # get html content
    html = res.read()
    soup = bs4.BeautifulSoup(html, 'html5lib')
    
    # extract articles
    for tag in soup.select(selector[query.source]):
        skip = False
        title = tag.getText()
        if title != prev_title:
            for keyword in keywords:
                if not skip:
                    if not query.config.all:
                        for kw in (keyword, keyword.upper(), keyword.capitalize()):
                            if (((' ' + kw) in title) or title.startswith(kw)) and (not skip):
                                url = url_getter[query.source](tag)
                                if url is not None:
                                    result[title] = url
                                    skip = True
                                    prev_title = title
                                    n_total += 1
                                    break
                                else:
                                    pass
                    else:
                        url = url_getter[query.source](tag)
                        if url is not None:
                            result[title] = url
                            skip = True
                            prev_title = title
                            n_total += 1
                        else:
                            pass

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
            if not query.config.all:
                print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(result), n_total))
            else:
                print('All papers in {} {}: {}'.format(query.conference.upper(), query.year, len(result)))
        else:
            print(output)
    else:
        sys.stdout.write('\n')
        if result:
            print(seps)
            print(output)
            print(seps)
            if not query.config.all:
                print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(result), n_total))
            else:
                print('All papers in {} {}: {}'.format(query.conference.upper(), query.year, len(result)))
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
    config.conferences = []
    config.years = []
    
    for value in config.conferences_and_years:
        try:
            value = int(value)
            config.years.append(value)
        except ValueError:
            config.conferences.append(value)
    
    medicalai(config.conferences, config.years, config)
