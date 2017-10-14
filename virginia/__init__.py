import os
import sys
import subprocess

from pyramid.httpexceptions import HTTPOk

from pyramid.config import Configurator
from pyramid.decorator import reify

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here,"tools"))
from virginia.models import Directory
from virginia.models import Filesystem

def main(global_config, **settings):
    here = os.path.dirname(__file__)
    sys.path.append(os.path.join(here,"tools","pybib-3.4"))
    sys.path.append(os.path.join(here,"tools"))
    root = settings.pop('root', None)
    if root is None:
        raise ValueError('virginia requires a root')
    root_path = os.path.abspath(os.path.normpath(root))
    fs = Filesystem(root_path)
    def get_root(request):
        #raise Exception(request.path_info)
        if request.path_info == '/Aa9sF92fJk3Hbsk23js9wjJNM':
            #cwd = os.path.join(os.path.expanduser("~"),"efs","jmamath7")
            subprocess.call(["git","fetch","origin"],cwd = root_path)
            subprocess.call(["git","reset","--hard","origin/master"], cwd = root_path)
            return(HTTPOk)
        else:
            return Directory(fs, root)
    config = Configurator(root_factory=get_root, settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view(name='static', path='virginia:static')
    config.scan()
    return config.make_wsgi_app()
