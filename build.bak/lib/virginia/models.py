import os
from pyramid.decorator import reify
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

    def read(self, path):
        return self.open(path).read()

class Base(object):
    @reify
    def nav(context): # this function assumes that context will be a File or Directory object, but it could be a Filesystem object
        fs = context.filesystem
        navfile = File(fs, fs.join(fs.root_path,"nav.md"))
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
    def __init__(self, filesystem, path):
        self.filesystem = filesystem
        self.path = os.path.abspath(os.path.normpath(path))
        self.use_mathjax = False

    def _source(self):
        return self.filesystem.read(self.path)

    def title(self):
        return None

    source = property(_source)

class Directory(Base):
    file_class = File

    def __init__(self, filesystem, path):
        self.filesystem = filesystem
        self.path = os.path.abspath(os.path.normpath(path))
        self.use_mathjax = False

    def __getitem__(self, name):
        nextpath = self.filesystem.join(self.path, name)
        if self.filesystem.islink(nextpath):
            realpath = self.filesystem.realpath(nextpath)
            if  ( realpath.startswith(self.path) and
                  self.filesystem.isfile(realpath) ):
                realdir = self.filesystem.dirname(realpath)
                if len(self.path.split(os.sep)) == len(realdir.split(os.sep)):
                    # if this symlink to a file is in the same
                    # directory as the original file, treat it as a
                    # primitive alias; use the link target as the
                    # filename so we get the right renderer (eg. stx
                    # vs html).
                    return File(self.filesystem, realpath)
                else:
                    raise KeyError(name)
            else:
                raise KeyError(name)
        elif self.filesystem.isdir(nextpath):
            return self.__class__(self.filesystem, nextpath)
        elif self.filesystem.isfile(nextpath):
            return self.file_class(self.filesystem, nextpath)
        else:
            raise KeyError(name)

