import os
from os.path import getmtime
import mimetypes

mimetypes.add_type('text/html', '.stx')
mimetypes.add_type('application/pdf', '.pdf')

from pyramid.response import FileResponse, Response
from pyramid.httpexceptions import HTTPFound

from pyramid.view import render_view_to_response
from pyramid.view import view_config
from pyramid.renderers import render

from virginia.models import File
from virginia.models import Directory

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from zope.structuredtext import stx2html
import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown_include.include import MarkdownInclude

#try: import mdx_mathjax
#except: pass
#try: import mdx_latex
#except: pass

import tempfile
import pydotreader

import re
from collections import defaultdict
import bib2html

# default views: router will call these 

@view_config(context=File)
def file_view(context, request):
    dirname, filename = os.path.split(context.path)
    name, ext = os.path.splitext(filename)
    # Set the last modified header to the last modified time of the file being served
    request.response.last_modified = getmtime(context.path)
    if ext == '':
        result = raw_view(context,request)
    else:
        #The prototype for this function is
        #render_view_to_response(context, request, name='', secure=True)
        #our views are based on the extension of the file being served, so we pass this as the name parameter to the view callable
        result = render_view_to_response(context, request, ext)
    return result

@view_config(context=Directory)
def directory_view(context, request):
    path_info = request.environ['PATH_INFO']
    if not path_info.endswith('/'):
        response = HTTPFound(location=path_info + '/')
        return response

    defaults = ('index.html', 'index.pt', 'index.md')
    for name in defaults:
        try:
            index = context[name]
        except KeyError:
            continue
        return file_view(index, request)
    response = Response('No default view for %s' % context.path)
    response.content_type = 'text/plain'
    return response

# custom views: FileView will call these

lexer_lookup = dict(Rnw='r', R='r', m='matlab')
@view_config(context=File, name='.c', renderer='templates/layout.pt')
@view_config(context=File, name='.py', renderer='templates/layout.pt')
@view_config(context=File, name='.m', renderer='templates/layout.pt')
@view_config(context=File, name='.hs', renderer='templates/layout.pt')
@view_config(context=File, name='.m2', renderer='templates/layout.pt')
@view_config(context=File, name='.R', renderer='templates/layout.pt')
@view_config(context=File, name='.Rnw', renderer='templates/layout.pt')
@view_config(context=File, name='.tex', renderer='templates/layout.pt')
def code_view(context, request):
    dirname, filename = os.path.split(context.path)
    name, ext = os.path.splitext(filename)
    try:
        lexer = get_lexer_by_name(lexer_lookup[ext[1:]], stripall=True)
    except:
        lexer = get_lexer_by_name(ext[1:], stripall=True)
    formatter = HtmlFormatter(linenos=False, cssclass="highlight")
    context.css.append(HtmlFormatter().get_style_defs('.highlight'))
    code = context.source
    result = highlight(code, lexer, formatter)
    return dict(title=name, content=result)

@view_config(context=File, name='.stx', renderer='templates/layout.pt')
def structured_text_view(context, request):
    """ Filesystem-based STX view
    """
    result = stx2html(context.source)
    return dict(title=context.title(), content=result)

@view_config(context=File, name='.csv', renderer='templates/layout.pt')
def csv_view(context, request):
    import pandas as pd
    import numpy as np
    df = pd.read_csv(context.path, na_filter=False)#, names=columns)
    #df = df.replace(np.nan, '', regex=True)
    df = df.fillna('')
    result = df.to_html()
    return dict(title='untitled', content=result, head=None)

@view_config(context=File, name='.md', renderer='templates/layout.pt', request_param='content_type=tex')
def markdown_view_as_tex(context, request):
    """ Filesystem-based MD view
    """
    re_citations = re.compile(r'\(@(\S*?):(\S*?)\)')
    citations = re_citations.findall(context.source.decode('utf-8')) # list of bibliographyfile:citation pairs
    source = re_citations.sub("(#\\2)",context.source.decode('utf-8'))

    bibs = defaultdict(list)
    for (bib,citation) in citations:
        if citation not in bibs[bib]:
            bibs[bib].append(citation)
    for bib,citations in bibs.items():
        source += '\bibliography{'+bib+'}{}'

# Markdown Extensions
    markdown_include = MarkdownInclude(
                           configs={'base_path':context.dirname()}
                       )
    result = markdown.markdown(source, extensions=['latex','extra','attr_list','markdown.extensions.extra','markdown.extensions.meta',markdown_include])

    response = Response(result)
    response.content_type = 'text/plain'
    return response

#@view_config(context=File, name='.md', renderer='templates/layout.pt')
@view_config(context=File, name='.md', renderer='templates/layout.pt')
@view_config(context=File, name='.md', renderer='templates/showdown.pt', request_param='content_type=showdown')
def markdown_view(context, request):
    """ Filesystem-based MD view
    """
    re_citations = re.compile(r'\(@(\S*?):(\S*?)\)')
    citations = re_citations.findall(context.source.decode('utf-8')) # list of bibliographyfile:citation pairs
    source = re_citations.sub("(#\\2)",context.source.decode('utf-8'))
    print(source)

    markdown_include = MarkdownInclude(
                           #configs={'base_path':context.filesystem.root_path}
                           configs={'base_path':context.dirname()}
                       )
    md = markdown.Markdown(extensions=['mdx_math','attr_list',TableExtension(),TocExtension(baselevel=1),'markdown.extensions.extra','markdown.extensions.meta','pymdownx.emoji',markdown_include])
    result = md.convert(source)
    context.use_mathjax=True
    #context.js.append("MathJax.Hub.Config({ 'tex2jax': { inlineMath: [ [ '$', '$' ] ] } });")

    bibs = defaultdict(list)
    for (bib,citation) in citations:
        if citation not in bibs[bib]:
            bibs[bib].append(citation)
    for bib,citations in bibs.items():
        bibfile = os.path.join(request.registry.settings['bibpath'],bib+".bib")
        try:
            result += bib2html.html(bibfile, citations, context.filesystem.root_path) 
        except IOError:
            pass
    try:
        title = md.Meta['title'][0]
    except:
        title = 'untitled'
    return dict(title=title, content=result, source=source, head=None)

@view_config(context=File, name='.rev', renderer='templates/reveal.pt')
@view_config(context=File, name='.rev', renderer='templates/reveal.pt', request_param='content_type=html')
def reveal_view(context, request):
    """ Filesystem-based MD view
    """
    re_citations = re.compile(r'\(@(\S*?):(\S*?)\)')
    citations = re_citations.findall(context.source.decode('utf-8')) # list of bibliographyfile:citation pairs
    source = re_citations.sub("(#\\2)",context.source.decode('utf-8'))

    context.use_mathjax=True
    context.js.append("MathJax.Hub.Config({ 'tex2jax': { inlineMath: [ [ '$', '$' ] ] } });")

    bibs = defaultdict(list)
    for (bib,citation) in citations:
        if citation not in bibs[bib]:
            bibs[bib].append(citation)
    for bib,citations in bibs.items():
        bibfile = os.path.join(request.registry.settings['bibpath'],bib+".bib")
        try:
            result += bib2html.html(bibfile, citations, context.filesystem.root_path) 
        except IOError:
            pass
    try:
        title = md.Meta['title'][0]
    except:
        title = 'untitled'
    return dict(title=title, content=source, head=None)

@view_config(context=File, name='.rem', renderer='templates/remark.pt')
@view_config(context=File, name='.rem', renderer='templates/remark.pt', request_param='content_type=html')
def remark_view(context, request):
    """ Filesystem-based MD view
    """
    re_citations = re.compile(r'\(@(\S*?):(\S*?)\)')
    citations = re_citations.findall(context.source.decode('utf-8')) # list of bibliographyfile:citation pairs
    source = re_citations.sub("(#\\2)",context.source.decode('utf-8'))

    markdown_include = MarkdownInclude(
                           #configs={'base_path':context.filesystem.root_path}
                           configs={'base_path':context.dirname()}
                       )
    md = markdown.Markdown(extensions=['mathjax','attr_list',TableExtension(),TocExtension(baselevel=1),'markdown.extensions.extra','markdown.extensions.meta','pymdownx.emoji',markdown_include])
    try:
        title = md.Meta['title'][0]
    except:
        title = 'untitled'
    return dict(title=title, content=source, head=None)


@view_config(context=File, name='.html', renderer='templates/layout.pt')
def html_view(context, request):
    """ Filesystem-based HTML view
    """
    source = context.source.decode('utf-8')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(source, 'html.parser')
    result = "".join([str(tag) for tag in soup.body.contents])
    head = soup.head.contents
    return dict(title=context.title(), content=result, head=head)

@view_config(context=File, name='.dot', renderer='templates/layout.pt')
def dot_view(context, request):
    """ Filesystem-based DOT view
    """
    nx_digraph = pydotreader.load_networkx_digraph_from_dot(context.path)
    graphviz_digraph = pydotreader.convert_networkx_digraph_to_graphviz_digraph(nx_digraph)
    result = graphviz_digraph._repr_svg_()
    return dict(title="untitled", content=result, head=None) # pydotreader currently does not parse the graph id, so we cannot currently use this field as a title for the rendered graph

@view_config(context=File, name='.bib', renderer='templates/layout.pt')
def bib_view(context, request):
    """ Filesystem-based BibTeX view
    """
    result = bib2html.html(context.path, rootdir=context.filesystem.root_path) 
    return dict(title="untitled", content=result, head=None)
    

#@view_config(context=File, name='.html')
@view_config(context=File, name='.js')
@view_config(context=File, name='.css')
@view_config(context=File, name='.pdf')
@view_config(context=File, name='.png')
@view_config(context=File, name='.ttf')
@view_config(context=File, name='.docx')
@view_config(context=File, name='.woff')
@view_config(context=File, name='.txt')
@view_config(context=File, name='.jpg')
@view_config(context=File, name='.sh')
@view_config(context=File, name='.svg')
@view_config(context=File, name='.md', renderer='templates/layout.pt', request_param='raw=true')
@view_config(context=File, name='.html', request_param='raw=true')
@view_config(context=File, name='.zip')
def raw_view(context, request):
    """ Just return the source raw.
    """
    response = FileResponse(context.path)
    return response
