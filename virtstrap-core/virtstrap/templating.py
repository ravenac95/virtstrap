"""
virtstrap.templating
--------------------

Defines tools for dealing with templating.
"""

from os import path
from contextlib import contextmanager
import constants
from packages.tempita import Template as TempitaTemplate

_global_environment = None

class TemplateDoesNotExist(Exception):
    pass

# Taken from Jinja2
def split_template_path(template):
    """Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if path.sep in piece \
           or (path.altsep and path.altsep in piece) or \
           piece == path.pardir:
            raise TemplateDoesNotExist(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces

def environment():
    """Get the global templating environment"""
    global _global_environment
    if not _global_environment:
        _global_environment = TempitaEnvironment(
                loaders=[PackageLoader('virtstrap', 'templates')],
                namespace=dict(constants=constants))
    return _global_environment

@contextmanager
def temp_template_environment(directory):
    """Provide a template environment for testing

    This creates a template environment based on the passed in directory.
    It will save and replace the global environment.
    """
    global _global_environment
    original_environment = None
    if _global_environment:
        original_environment = None
    _global_environment = TempitaEnvironment(
            loaders=[FileSystemLoader(directory)])
    try:
        yield
    finally:
        _global_environment = original_environment

class TempitaEnvironment(object):
    """A tempita environment similar to jinja's environment

    The loader can be updated on the fly.
    """
    def __init__(self, loaders=None, namespace=None):
        loaders = loaders or []
        self._loaders = loaders[:]
        self._namespace = {}
        if namespace:
            self._namespace = namespace.copy()

    @property
    def namespace(self):
        return self._namespace
    
    def add_to_namespace(self, key, value):
        self._namespace[key] = value

    def add_loader(self, loader):
        """Last loader takes most precedence"""
        self._loaders.insert(0, loader)

    def get_template(self, template_name, from_template=None):
        for loader in self._loaders:
            template = loader.get_template(template_name, self)
            if template:
                return template
        raise TemplateDoesNotExist(
                'Template "%s" does not exist' % template_name)
    
    def from_string(self, template_string):
        return Template.from_string(template_string, self)

    def get_tempita_template(self, template_name, from_template=None):
        template = self.get_template(template_name, from_template)
        return template._template

def handle_template_kwargs(env, kwargs):
    kwargs['get_template'] = env.get_tempita_template
    # Combine the namespaces
    kwargs['namespace'] = env.namespace


class Template(object):
    """Wraps tempita's template to match the current usage of templates."""
    @classmethod
    def from_filename(cls, path, env, **kwargs):
        handle_template_kwargs(env, kwargs)
        tempita_template = TempitaTemplate.from_filename(path, **kwargs)
        return cls(tempita_template, env)

    @classmethod
    def from_string(cls, string, env, **kwargs):
        handle_template_kwargs(env, kwargs)
        tempita_template = TempitaTemplate(string, **kwargs)
        return cls(tempita_template, env)

    def __init__(self, template, environment=None):
        self._template = template
        self._environment = environment

    def render(self, *args, **kwargs):
        context = dict(*args, **kwargs)
        return self._template.substitute(context)

class TemplateLoader(object):
    def get_template(self, name, env):
        raise NotImplementedError("get_template not implemented")

    def load_template_file(self, path, env):
        template = Template.from_filename(path, env)
        return template

    def load_template_string(self, source, env):
        template = Template.from_string(source, env)
        return template

class FileSystemLoader(TemplateLoader):
    def __init__(self, base_path):
        self._base_path = path.abspath(base_path)

    def get_template(self, name, env):
        pieces = split_template_path(name)
        template_path = path.join(self._base_path, "/".join(pieces))
        return self.load_template_file(template_path, env)

# Edited from Jinja2
class PackageLoader(TemplateLoader):
    """Package loader very similar to jinja2's package loader"""
    def __init__(self, package_name, package_path='templates', 
            encoding='utf-8'):
        from pkg_resources import DefaultProvider, ResourceManager, \
                                  get_provider
        provider = get_provider(package_name)
        self._encoding = encoding
        self._manager = ResourceManager()
        self._filesystem_bound = isinstance(provider, DefaultProvider)
        self._provider = provider
        self._package_path = package_path

    def get_template(self, name, env):
        try:
            source = self.get_source(name)
        except TemplateDoesNotExist:
            return None
        return self.load_template_string(source, env)

    def get_source(self, template):
        pieces = split_template_path(template)
        p = '/'.join((self._package_path,) + tuple(pieces))
        if not self._provider.has_resource(p):
            raise TemplateDoesNotExist(template)

        filename = uptodate = None
        if self._filesystem_bound:
            filename = self._provider.get_resource_filename(self._manager, p)
            mtime = path.getmtime(filename)
            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False

        source = self._provider.get_resource_string(self._manager, p)
        return source.decode(self._encoding)
