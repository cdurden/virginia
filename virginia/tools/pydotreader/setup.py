#from distutils.core import setup, Extension
#from distutils.core import Extension
from setuptools import setup, find_packages, Extension
 
module1 = Extension('_pydotreader', sources = ['dotreader.c','y.tab.c', 'gdi.c', 'graph.c', 'lex.yy.c', 'list.c', 'set.c'])
 
setup (name = 'pydotreader',
        version = '1.0',
        package_dir = {'pydotreader':'lib'},
        packages = ['pydotreader'],
        install_requires = ['networkx==1.10', 'graphviz'],
        description = 'This is a demo package',
        ext_modules = [module1])
