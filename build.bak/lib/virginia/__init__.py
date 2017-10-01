import os
import sys

from pyramid.config import Configurator
from pyramid.decorator import reify

from virginia.models import Directory
from virginia.models import Filesystem

def main(global_config, **settings):
    here = os.path.dirname(__file__)
    sys.path.append(os.path.join(here,"tools","pybib-3.4"))
    sys.path.append(os.path.join(here,"tools"))
    root = settings.pop('root', None)
    if root is None:
        raise ValueError('virginia requires a root')
    fs = Filesystem(os.path.abspath(os.path.normpath(root)))
    def get_root(environ):
        return Directory(fs, root)
    config = Configurator(root_factory=get_root, settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view(name='static', path='virginia:static')
    config.scan()
    return config.make_wsgi_app()

