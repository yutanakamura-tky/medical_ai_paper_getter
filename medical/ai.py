# -*- coding: utf-8 -*-

import argparse
import bs4
import collections
import pyperclip
import sys
import threading
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


        

        
class MedicalClassifier():
    # keyword-based classification of medical/non-medical AI papers

    # class variables
    keywords = ['medic', 'biomedic', 'bioMedic', 'health', 'clinic', 'EHR', 'MeSH', 'RCT', 'life', 'care', 'pharm', 'food-drug', 'drug', 'surg',\
                'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'treatment',\
                'cancer', 'psycholog', 'psychiat', 'mental', 'radiol', 'patho', 'autopsy', 'x-ray', 'x-Ray', 'mammogr', 'CT', 'MRI', 'radiograph', 'tomograph',\
                'magnetic']
    
    def __init__(self):
        pass

    def title_is_medical(self, title):
        for keyword in MedicalClassifier.keywords:
            for kw in (keyword, keyword.upper(), keyword.capitalize()):
                if (((' ' + kw) in title) or title.startswith(kw)):
                    return True
                else:
                    continue
        return False



class HTMLParser():
    # process received HTTP response

    # class variables
    selector = {'aclweb' : 'a[class="align-middle"]',\
                'dblp' : 'span[class="title"]'}
    url_getter = {'aclweb' : lambda tag: 'https://aclweb.org' + tag.attrs['href'] if tag.attrs['href'].startswith('/anthology/paper') else None,\
                  'dblp' : lambda tag: tag.parent.parent.contents[2].ul.li.div.a['href']}
    
    def __init__(self):
        pass

    def parse(self, res, conference):
        prev_title = ''
        n_total = 0
        papers = []

        classifier = MedicalClassifier()
    
        # get html content
        html = res.read()
        soup = bs4.BeautifulSoup(html, 'html5lib')
    
        # extract papers
        for tag in soup.select(HTMLParser.selector[conference.source]):
            title = tag.getText()
            if title != prev_title:
                n_total += 1
                prev_title = title

                url = HTMLParser.url_getter[conference.source](tag)                
                if url is None:
                    continue
                else:
                    paper = Paper(title=title, url=url, conference_name=conference.conference_name, year=conference.year)
                    paper.medical = classifier.title_is_medical(paper.title)
                    papers.append(paper)
                
            if not conference.config.quiet:
                sys.stdout.write('\rDownloading from {} {} ... {} papers'.format(conference.conference_name.upper(), conference.year, n_total))
                sys.stdout.flush()

        if not conference.config.quiet:    
            print('\rDownloading from {} {} ... {} papers Complete!'.format(conference.conference_name.upper(), conference.year, n_total))

        # return OrderedDict
        return papers
                


class Paper():
    def __init__(self, title='', author=[], abstract='', conference_name='', year=0, url=''):
        self.title = title
        self.author = author
        self.abstract = abstract
        self.conference_name = conference_name
        self.year = year
        self.url = url
        self.medical = False


    
class Conference(threading.Thread):
    conference_map = { 'NLP' : ['acl', 'anlp', 'cl', 'conll', 'eacl', 'emnlp', 'naacl',\
                        'semeval', 'tacl', 'ws', 'alta', 'coling', 'hlt',\
                        'ijcnlp', 'jep-taln-recital', 'lrec', 'muc', 'paclic', 'ranlp',\
                        'rocling-ijclclp', 'tinlap', 'tipster'],\
                        'ML' : ['nips', 'icml', 'iclr', 'ijcnn', 'ijcai'],\
                        'CV' : ['cvpr', 'iccv']}

    source_map = {}

    url_container = { 'aclweb' : 'https://aclweb.org/anthology/events/{0}-{1}',\
                      'dblp' : 'https://dblp.org/db/conf/{0}/{0}{1}.html'}

    parser = HTMLParser()
        
    def __init__(self, conference_name, year):
        super().__init__()
        for c in Conference.conference_map['NLP']:
            Conference.source_map[c] = 'aclweb'
        for c in Conference.conference_map['ML']:
            Conference.source_map[c] = 'dblp'
        for c in Conference.conference_map['CV']:
            Conference.source_map[c] = 'dblp'
            
        self.conference_name = conference_name
        self.year = year
        self.config = None
        self.papers = []
        self.n_papers = 0
        self.medical_ai_papers = []
        self.n_medical_ai_papers = 0
        try:
            self.source = Conference.source_map[self.conference_name]
            self.url = Conference.url_container[self.source].format(self.conference_name, self.year)
        except KeyError:
            seps = '=' * 35
            print("Error: unavailable conference '{}'.".format(self.conference_name))
            print(seps)
            print('Available conferences:')
            print('\tML, AI:\n\t\t{}'.format(', '.join(Conference.conference_map['ML'])))
            print('\tCV:\n\t\t{}'.format(', '.join(Conference.conference_map['CV'])))
            print('\tNLP:\n\t\t{}'.format(', '.join(Conference.conference_map['NLP'])))
            print(seps)

    def run(self):
        print('Connecting for {} {} ...'.format(self.conference_name.upper(), self.year))
        try:
            with urllib.request.urlopen(self.url) as res:
                self.papers = Conference.parser.parse(res, self)
                self.n_papers = len(self.papers)
                self.medical_ai_papers = list(filter(lambda paper: paper.medical, self.papers))
                self.n_medical_ai_papers = len(self.medical_ai_papers)
        except urllib.error.HTTPError as err:
            print('Error: {} {}'.format(err.code, err.reason))
        except urllib.error.URLError as err:
            print('Error: {}'.format(err.reason))

    def catalog(self, config=Config()):
        if self.papers:
            if config.markdown:
                separator = '\n\n'
                if config.url_only:
                    info_container = '[{1}]({1})'
                else:
                    info_container = '[{0}]({1})'
            elif config.html:
                separator = '<br/>\n\n'
                if config.url_only:
                    info_container = '<a href="{1}" target="_blank" alt="{1}">{1}</a>'
                else:
                    info_container = '<a href="{1}" target="_blank" alt="{0}">{0}</a>'
            else:
                separator = '\n\n'
                if config.title_only:
                    info_container = '{0}'
                elif config.url_only:
                    info_container = '{1}'
                else:
                    info_container = '{0}\n{1}'

            if config.all:
                output = separator.join([ info_container.format(paper.title.replace('"', "'"), paper.url) for paper in self.papers ] + [''])
            else:
                output = separator.join([ info_container.format(paper.title.replace('"', "'"), paper.url) for paper in self.medical_ai_papers ] + [''])

        else:
            output = 'No medical-like AI papers found.'

        return output



        

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
        if type(conference) is not list:
            self.conference_names = [conference.lower()]
        else:
            self.conference_names = conference
            
        if type(year) is not list:
            self.year = [year]
        else:
            self.year = year

        self.conferences = []
        self.parser = HTMLParser()
        
        for c in self.conference_names:
            for y in self.year:
                sub_query = Conference(c.lower(), str(y))
                self.conferences.append(sub_query)

    def search(self, config=Config()):
        # throw HTTP request
        for sub_query in self.conferences:
            sub_query.config = config
            sub_query.start()
        for sub_query in self.conferences:
            sub_query.join()

    def print(self, config=Config()):        
        # prepare output display
        message = ''
        seps = '\n' + '=' * 35 + '\n'
        

        if not config.quiet:
            message += seps
            for conference in self.conferences:
                message += '\n{} {}\n\n'.format(conference.conference_name.upper(), conference.year)
                message += conference.catalog(config=config)
            message += seps

        for conference in self.conferences:
            if not conference.config.all:
                message += 'Medical-like AI papers in {} {}: {} / {}\n'.format(conference.conference_name.upper(), conference.year, conference.n_medical_ai_papers, conference.n_papers)
            else:
                message += 'All papers in {} {}: {}\n'.format(conference.conference_name.upper(), conference.year, conference.n_papers)

        print(message)

        # copy onto clipboard if needed
        if config.copy:
            pyperclip.copy(message)
            print(' * * * Copied this result to clipboard * * *')
    


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
    query.print(config)
