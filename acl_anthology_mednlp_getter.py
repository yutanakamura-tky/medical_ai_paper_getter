import bs4
import urllib
import pyperclip

def mednlp(conference_and_year, verbose=True, ashtml=False):
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
	
	# get html content
	url = 'https://aclweb.org/anthology/events/{}-{}'.format(conference.lower(), str(year))

	try:
		with urllib.request.urlopen(url) as res:
			mednlp_parse(res, verbose, ashtml)
	except urllib.error.HTTPError as err:
		print('An error occurred: {} {}'.format(err.code, err.reason))
	except urllib.error.URLError as err:
		print('An error occurred: {}'.format(err.reason))
			

def mednlp_parse(res, verbose=True, ashtml=False):
	html = res.read()
	soup = bs4.BeautifulSoup(html, 'html5lib')

	# query
	queries = ['medic', 'biomedic', 'health', 'clinic', 'life', 'care', 'pharm', 'drug', 'surg', 'emergency', 'ICU', 'hospital', 'patient', 'doctor', 'disease', 'illness', 'symptom', 'psychol', 'psychiat', 'mental', 'radiol', 'x-ray', 'report', 'CT', 'MRI', 'radiograph', 'tomograph', 'magnetic']

	result = []
	prev_title = ''

	# extract articles
	for tag in soup.select('a[class="align-middle"]'):
		skip = False
		title = tag.getText()
		if title != prev_title:
			for query in queries:
				if not skip:
					for q in (query, query.upper(), query.capitalize()):
						if (((' '+q) in title) or title.startswith(q)) and (not skip):
							link = tag.attrs['href']
							if link.startswith('/anthology/paper'):
								result.append([title, 'https://aclweb.org'+link])
								skip = True
								prev_title = title
								break

	if len(result) == 0:								
		print('No medical NLP papers found.')
		
	if verbose:
		print('\n\n'.join(['\n'.join(r) for r in result]))

	if not ashtml:
		return result
	else:
		pyperclip.copy('\n'.join(['<p><a href="{}">{}</a></p>'.format(r[1],r[0]) for r in result]))

if __name__ == '__main__':
	mednlp(input("Input conference name and year (e.g. 'naacl 2019') : ").split(), ashtml=bool(input('Would you like HTML-like output copied on clipboard? (True/False) : ')))
