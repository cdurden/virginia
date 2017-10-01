
allfields = ['address', 'author', 'booktitle', 'chapter', 'edition',
	     'editor', 'howpublished', 'institution', 'journal', 'month',
	     'number', 'organization', 'pages', 'publisher', 'school',
	     'series', 'title', 'type', 'volume',
	     'year', 'note', 'code', 'url', 'crossref', 'annote', 'abstract'];

# list of all reference types
alltypes = ['article', 'book', 'booklet', 'inbook', 'incollection',
	    'inproceedings', 'manual', 'mastersthesis', 'misc', 'phdthesis',
	    'proceedings', 'techreport', 'unpublished'];

# list of additional fields, ignored by the standard BibTeX styles
ign = ['crossref', 'code', 'url', 'annote', 'abstract'];

# lists of required and optional fields for each reference type

required_fields = {
  'article' :		['author', 'title', 'journal', 'year'],
  'book' :		['author', 'title', 'publisher', 'year'],
  'booklet' :		['title'],
  'inbook' :		['author', 'title', 'chapter', 'pages', 
  				'publisher', 'year'],
  'incollection' :	['author', 'title', 'booktitle', 'publisher', 'year'],
  'inproceedings' :	['author', 'title', 'booktitle', 'year'],
  'manual' :		['title'],
  'misc' : 		[],
  'mastersthesis' :	['author', 'title', 'school', 'year'],
  'phdthesis' :		['author', 'title', 'school', 'year'],
  'proceedings' :	['title', 'year'],
  'techreport' :	['author', 'title', 'institution', 'year'],
  'unpublished' :	['author', 'title', 'note']
};

opt_fields = {
  'article' :		['volume', 'number', 'pages', 'month', 'note'],
  'book' :		['editor', 'volume', 'number', 'series', 'address',
  				'edition', 'month', 'note'],
  'booklet' :		['author', 'howpublished', 'address', 'month', 'year',
  				'note'],
  'inbook' :		['editor', 'volume', 'series', 'address', 'edition',
  				'month', 'note'],
  'incollection' :	['editor', 'volume', 'number', 'series', 'type', 
  				'chapter'  'pages', 'address', 'edition',
				'month', 'note'],
  'inproceedings' :	['editor', 'pages', 'organization', 'publisher', 
  				'address', 'month', 'note'],
  'manual' :		['author', 'organization', 'address', 'edition',
  				'month', 'year', 'note'],
  'misc' :		['title', 'author', 'howpublished', 'month', 'year',
  				'note'],
  'mastersthesis' :	['address', 'month', 'note'],
  'phdthesis' :		['address', 'month', 'note'],
  'proceedings' :	['editor', 'publisher', 'organization', 'address', 
  				'month', 'note'],
  'techreport' :	['type', 'number', 'address', 'month', 'note'],
  'unpublished' :	['month', 'year']
};
