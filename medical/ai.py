# -*- coding: utf-8 -*-

import argparse
import bs4
import collections
import pyperclip
import sys
import urllib
import urllib.request



class Config():
    def __init__(self, quiet=False, copy=False, get_all=False, markdown=False, html=False, title_only=False, url_only=False):
        self.quiet = quiet
        self.copy = copy
        self.all = get_all
        self.markdown = markdown
        self.html = html
        self.title_only = title_only
        self.url_only = url_only


        
class Article():
    def __init__(self, title='', author=[], abstract='', conference='', year=0, url=''):
        self.title = title
        self.author = author
        self.abstract = abstract
        self.conference = conference
        self.year = year
        self.url = url


        
class Medical_Classifier():
    # keyword-based classification of medical/non-medical AI papers
    def __init__(self):
        self.keywords = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'EHR', 'MeSH', 'RCT', 'life', 'care', 'pharm', 'food-drug', 'drug', 'surg',\
                          'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',\
                          'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'patho', 'autopsy', 'x-ray', 'x-Ray', 'mammogr', 'CT', 'MRI', 'radiograph', 'tomograph',\
                          'magnetic']

    def title_is_medical(self, title):
        for keyword in self.keywords:
            for kw in (keyword, keyword.upper(), keyword.capitalize()):
                if (((' ' + kw) in title) or title.startswith(kw)):
                    return True
                else:
                    continue
        return False



class HTMLParser():
    # process received HTTP response
    def __init__(self):
        self.selector = {'aclweb' : 'a[class="align-middle"]',\
                    'dblp' : 'span[class="title"]'}

        self.url_getter = {'aclweb' : lambda tag: 'https://aclweb.org' + tag.attrs['href'] if tag.attrs['href'].startswith('/anthology/paper') else None,\
                      'dblp' : lambda tag: tag.parent.parent.contents[2].ul.li.div.a['href']}

    def parse(self, res, query):
        prev_title = ''
        n_total = 0
        articles = []

        classifier = Medical_Classifier()
    
        # get html content
        html = res.read()
        soup = bs4.BeautifulSoup(html, 'html5lib')
    
        # extract articles
        for tag in soup.select(self.selector[query.source]):
            skip = False
            title = tag.getText()
            if title != prev_title:
                n_total += 1
                prev_title = title
                if query.config.all or classifier.title_is_medical(title):
                    url = self.url_getter[query.source](tag)                
                    if url is None:
                        continue
                    else:
                        article = Article(title=title, url=url, conference=query.conference, year=query.year)
                        articles.append(article)

            if not query.config.quiet:
                sys.stdout.write('\rSearching... {} match / {}'.format(len(articles), n_total))
                sys.stdout.flush()
                
        # prepare output display
        output = ''
    
        if articles:
            if query.config.markdown:
                if query.config.url_only:
                    output = '\n'.join([ '[{0}]({0})'.format(article.url) for article in articles ])
                else:
                    output = '\n'.join([ '[{0}]({1})'.format(article.title, article.url) for article in articles ])
            elif query.config.html:
                if query.config.url_only:
                    output = '<br/>\n'.join([ '<a href="{0}" target="_blank" alt="{0}">{0}</a>'.format(article.url) for article in articles ])
                else:
                    output = '<br/>\n'.join([ '<a href="{1}" target="_blank" alt="{0}">{0}</a>'.format(article.title.replace('"', "'"), article.url) for article in articles ])
            else:
                if query.config.title_only:
                    output = '\n'.join([ article.title for article in articles ])
                elif query.config.url_only:
                    output = '\n'.join([ article.url for article in articles ])
                else:
                    output = '\n\n'.join([ '{0}\n{1}'.format(article.title, article.url) for article in articles ])
        else:
            output = 'No medical-like AI papers found.'
            

        # display output
        seps = '=' * 35
    
        if query.config.quiet:
            if articles:
                if not query.config.all:
                    print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(articles), n_total))
                else:
                    print('All papers in {} {}: {}'.format(query.conference.upper(), query.year, len(articles)))
            else:
                print(output)
        else:
            sys.stdout.write('\n')
            if articles:
                print(seps)
                print(output)
                print(seps)
                if not query.config.all:
                    print('Medical-like AI papers in {} {}: {} / {}'.format(query.conference.upper(), query.year, len(articles), n_total))
                else:
                    print('All papers in {} {}: {}'.format(query.conference.upper(), query.year, len(articles)))
                print(seps)
            else:
                print(output)
            
        # copy onto clipboard if needed
        if query.config.copy:
            pyperclip.copy(output)
            print(' * * * Copied this result to clipboard * * *')

        # return OrderedDict
        return articles
                


    
class Child_Query():
    def __init__(self, conf, yr):
        self.conference = conf
        self.year = yr
        self.res = None
        self.url = None
        self.source = None
        self.config = None


        

class Query():
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
    #   list of Article objects

    def __init__(self, conference, year):
        self.conference_map = { 'NLP' : ['acl', 'anlp', 'cl', 'conll', 'eacl', 'emnlp', 'naacl',\
                             'semeval', 'tacl', 'ws', 'alta', 'coling', 'hlt',\
                             'ijcnlp', 'jep-taln-recital', 'lrec', 'muc', 'paclic', 'ranlp',\
                             'rocling-ijclclp', 'tinlap', 'tipster'],\
                             'ML' : ['nips', 'icml', 'iclr', 'ijcnn', 'ijcai'],\
                             'CV' : ['cvpr', 'iccv']}
        
        self.source_map = {}
        for conf in self.conference_map['NLP']:
            self.source_map[conf] = 'aclweb'
        for conf in self.conference_map['ML']:
            self.source_map[conf] = 'dblp'
        for conf in self.conference_map['CV']:
            self.source_map[conf] = 'dblp'

        self.url_container = { 'aclweb' : 'https://aclweb.org/anthology/events/{0}-{1}',\
                               'dblp' : 'https://dblp.org/db/conf/{0}/{0}{1}.html'}

        if type(conference) is not list:
            self.conference = [conference.lower()]
        else:
            self.conference = conference
            
        if type(year) is not list:
            self.year = [year]
        else:
            self.year = year
            
        self.queries = []
        self.result = []

        for c in self.conference:
            for y in self.year:
                query = Child_Query(c.lower(), str(y))

                # check conference name
                try:
                    query.source = self.source_map[query.conference]
                    query.url = self.url_container[query.source].format(query.conference, query.year)
                    self.queries.append(query)
                except KeyError:
                    seps = '=' * 35
                    print("Error: unavailable conference '{}'.".format(query.conference))
                    print(seps)
                    print('Available conferences:')
                    print('\tML, AI:\n\t\t{}'.format(', '.join(self.conference_map['ML'])))
                    print('\tCV:\n\t\t{}'.format(', '.join(self.conference_map['CV'])))
                    print('\tNLP:\n\t\t{}'.format(', '.join(self.conference_map['NLP'])))
                    print(seps)

    def search(self, config=Config()):        
        # throw HTTP request
        parser = HTMLParser()
        for q in self.queries:
            q.config = config
            print('Connecting for {} {} ...'.format(q.conference.upper(), q.year))
            try:
                with urllib.request.urlopen(q.url) as res:
                    self.result.append(parser.parse(res, q))
            except urllib.error.HTTPError as err:
                print('Error: {} {}'.format(err.code, err.reason))
            except urllib.error.URLError as err:
                print('Error: {}'.format(err.reason))
        return self.result



if __name__ == '__main__':

    # get args when executed via command-line

    def get_args():
        description='''
        ++++++++++++++++++++++++++++++++++++++++++++++++++
        Pickup medical AI paper titles and URLs from specified conference and year.
        会議名と年数を指定すると, 医療に関連するAI論文のみを探し出してタイトルとURLを列挙します.
        
        To get from ACL 2019, input like this: python3 medical/ai.py acl 2019
        例えばACL 2019採択論文から探すには本プログラムを python3 medical/ai.py acl 2019 と実行してください.
        
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
    
    config = get_args()
    config.conferences = []
    config.years = []
    
    for value in config.conferences_and_years:
        try:
            value = int(value)
            config.years.append(value)
        except ValueError:
            config.conferences.append(value)

    query = Query(config.conferences, config.years)
    query.search(config)
