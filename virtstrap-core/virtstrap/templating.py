"""
virtstrap.templating
--------------------

Defines tools for dealing with templating.
"""

import os
from contextlib import contextmanager
from jinja2 import (Environment, PackageLoader as JinjaPackageLoader, 
        FileSystemLoader as JinjaFileSystemLoader)
from packages.tempita import Template as TempitaTemplate

_global_environment = None

def environment():
    """Get the global templating environment"""
    global _global_environment
    if not _global_environment:
        _global_environment = Environment(
                loader=JinjaPackageLoader('virtstrap', 'templates'))
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
    _global_environment = Environment(
            loader=JinjaFileSystemLoader(directory))
    try:
        yield
    finally:
        _global_environment = original_environment

class TemplateDoesNotExist(Exception):
    pass

class TempitaEnvironment(object):
    """A tempita environment similar to jinja's environment

    The loader can be updated on the fly.
    """
    def __init__(self, loaders=None):
        loaders = loaders or []
        self._loaders = loaders[:]

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

    def get_tempita_template(self, template_name, from_template=None):
        template = self.get_template(template_name, from_template)
        return template._template

class Template(object):
    """Wraps tempita's template to match the current usage of templates."""
    @classmethod
    def from_filename(cls, path, env, **kwargs):
        kwargs['get_template'] = env.get_tempita_template
        tempita_template = TempitaTemplate.from_filename(path, **kwargs)
        return cls(tempita_template, env)

    def __init__(self, template, environment=None):
        self._template = template
        self._environment = environment

    def render(self, context):
        return self._template.substitute(context)

class TemplateLoader(object):
    def get_template(self, name, env):
        raise NotImplementedError("get_template not implemented")

    def load_template_file(self, path, env):
        template = Template.from_filename(path, env)
        return template

class FileSystemLoader(TemplateLoader):
    def __init__(self, base_path):
        self._base_path = os.path.abspath(base_path)

    def get_template(self, name, env):
        template_path = os.path.join(self._base_path, name)
        return self.load_template_file(template_path, env)

class PackageLoader(TemplateLoader):
    def __init__(self, package_name, package_path='templates'):
        from pkg_resources import DefaultProvider, ResourceManager, \
                                  get_provider
        self._provider = get_provider(package_name)
        self._manager = ResourceManager()
        self._package_path = package_path

    def get_template(self, name, env):
        template_path = os.path.join(self._base_path, name)
        return self.load_template_file(template_path, env)
