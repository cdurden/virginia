import os
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
    if ext == '':
        result = raw_view(context,request)
    else:
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

    result = markdown.markdown(source, extensions=['latex','markdown.extensions.extra','markdown.extensions.meta'])

    response = Response(result)
    response.content_type = 'text/plain'
    return response

@view_config(context=File, name='.md', renderer='templates/layout.pt')
@view_config(context=File, name='.md', renderer='templates/layout.pt', request_param='content_type=html')
def markdown_view(context, request):
    """ Filesystem-based MD view
    """
    re_citations = re.compile(r'\(@(\S*?):(\S*?)\)')
    citations = re_citations.findall(context.source.decode('utf-8')) # list of bibliographyfile:citation pairs
    source = re_citations.sub("(#\\2)",context.source.decode('utf-8'))

#    result = markdown.markdown(source, extensions=['mathjax',TableExtension(), TocExtension(baselevel=1),'markdown.extensions.extra', 'markdown.extensions.meta'])
    md = markdown.Markdown(extensions=['mathjax',TableExtension(),TocExtension(baselevel=1),'markdown.extensions.extra','markdown.extensions.meta'])
    result = md.convert(source)
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
    return dict(title=title, content=result)

@view_config(context=File, name='.html', renderer='templates/layout.pt')
def html_view(context, request):
    """ Filesystem-based HTML view
    """
    result = context.source.decode('utf-8')
    return dict(title=context.title(), content=result)

@view_config(context=File, name='.dot', renderer='templates/layout.pt')
def dot_view(context, request):
    """ Filesystem-based DOT view
    """
    nx_digraph = pydotreader.load_networkx_digraph_from_dot(context.path)
    graphviz_digraph = pydotreader.convert_networkx_digraph_to_graphviz_digraph(nx_digraph)
    result = graphviz_digraph._repr_svg_()
#    here = os.path.dirname(__file__)
#    dir = os.path.join(here,'static','tmp')
#    fd, path = tempfile.mkstemp(suffix='.svg',dir=dir) 
#    try:
#        with open(path,'w') as f:
#            f.write(graphviz_digraph._repr_svg_())
#    except IOError as e:
#        raise(DotRenderError(e.value))
#    return(request.static_url(os.path.join(here,'static','tmp',os.path.split(path)[1])))
    return dict(title="untitled", content=result) # pydotreader currently does not parse the graph id, so we cannot currently use this field as a title for the rendered graph

@view_config(context=File, name='.bib', renderer='templates/layout.pt')
def bib_view(context, request):
    """ Filesystem-based BibTeX view
    """
    result = bib2html.html(context.path, rootdir=context.filesystem.root_path) 
    return dict(title="untitled", content=result)
    

#@view_config(context=File, name='.html')
@view_config(context=File, name='.pdf')
@view_config(context=File, name='.png')
@view_config(context=File, name='.txt')
#@view_config(context=File, name='.jpg')
@view_config(context=File, name='.js')
@view_config(context=File, name='.sh')
@view_config(context=File, name='.svg')
def raw_view(context, request):
    """ Just return the source raw.
    """
#    response = Response(context.source)
    response = FileResponse(context.path)
#    dirname, filename = os.path.split(context.path)
#    name, ext = os.path.splitext(filename)
#    mt, encoding = mimetypes.guess_type(filename)
#    response.content_type = mt or 'text/plain'
    return response
