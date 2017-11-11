import os
from pyramid.decorator import reify
asdf
import logging
log = logging.getLogger(__name__)
import markdown

class Filesystem(object):
    def __init__(self, root_path):
        self.root_path = os.path.abspath(os.path.normpath(root_path))

    join = staticmethod(os.path.join)
    dirname = staticmethod(os.path.dirname)
    realpath = staticmethod(os.path.realpath)
    islink = staticmethod(os.path.islink)
    isfile = staticmethod(os.path.isfile)
    isdir = staticmethod(os.path.isdir)

    def open(self, path):
        if path.startswith(self.root_path):
            return open(path, 'rb')
        #else: # allow access outside the filesystem
        #    return open(path, 'rb')

    def read(self, path):
        return self.open(path).read()

class Base(object):
    @reify
    def header(context): # this function assumes that context will be a File or Directory object, but it could be a Filesystem object
        fs = context.filesystem
        headerfile = File(fs, fs.join(fs.root_path,"header.md"), None)
        mdProcessor = markdown.Markdown(extensions=['mathjax'])
        result = mdProcessor.convert(headerfile.source.decode('utf-8'))
        return result

    @reify
    def nav(context): # this function assumes that context will be a File or Directory object, but it could be a Filesystem object
        fs = context.filesystem
        navfile = File(fs, fs.join(fs.root_path,"nav.md"), None)
        mdProcessor = markdown.Markdown(extensions=['mathjax'])
        result = mdProcessor.convert(navfile.source.decode('utf-8'))
        return result

    @reify
    def css(context):
        return []

    @reify
    def js(context):
        return []


class File(Base):
    def __init__(self, filesystem, path, name):
        self.filesystem = filesystem
        self.path = os.path.abspath(os.path.normpath(path))
        self.use_mathjax = False
        self.__name__ = name

    def dirname(self):
        return os.path.dirname(self.path)

    def _source(self):
        print(self.path)
        return self.filesystem.read(self.path)

    def title(self):
        return None

    source = property(_source)

class Directory(Base):
    file_class = File
    __name__ = ''
    __parent__ = None

    def __init__(self, filesystem, path, name):
        self.filesystem = filesystem
        self.path = os.path.abspath(os.path.normpath(path))
        self.use_mathjax = False

    def __getitem__(self, name):
        nextpath = self.filesystem.join(self.path, name)
        if self.filesystem.islink(nextpath):
            realpath = self.filesystem.realpath(nextpath)
            log.debug('Link encountered: %s -> %s)', nextpath, realpath)
#            if  ( realpath.startswith(self.path) and
#                  self.filesystem.isfile(realpath) ):
#                realdir = self.filesystem.dirname(realpath)
#                if len(self.path.split(os.sep)) == len(realdir.split(os.sep)):
#                    # if this symlink to a file is in the same
#                    # directory as the original file, treat it as a
#                    # primitive alias; use the link target as the
#                    # filename so we get the right renderer (eg. stx
#                    # vs html).
#                    return File(self.filesystem, realpath, name)
#                else:
#                    #raise KeyError(name)
#                    return File(self.filesystem, realpath, name)
#            elif ( realpath.startswith(self.filesystem.root_path) and
#                    self.filesystem.isdir(realpath) ):
#                return self.__class__(self.filesystem, nextpath, name)
            if self.filesystem.isfile(realpath):
                return File(self.filesystem, realpath, name)
            elif self.filesystem.isdir(realpath):
                return self.__class__(self.filesystem, nextpath, name)
            else:
                raise KeyError(name)
        elif self.filesystem.isdir(nextpath):
            return self.__class__(self.filesystem, nextpath, name)
        elif self.filesystem.isfile(nextpath):
            return self.file_class(self.filesystem, nextpath, name)
        else:
            raise KeyError(name)

