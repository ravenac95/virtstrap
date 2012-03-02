"""
virtstrap.basecommand
---------------------

This module contains both the Command and ProjectCommand classes. These
classes are used for creating new commands in virtstrap.
"""

from argparse import ArgumentParser
from jinja2 import Environment
from virtstrap.log import logger
from virtstrap.templating import environment
from virtstrap.project import Project

__all__ = ['Command', 'ProjectMixin', 'ProjectCommand']

class Command(object):
    """Command class for creating global virtstrap commands"""

    name = None
    args = None
    parser = ArgumentParser()
    description = None

    def __init__(self):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.options = None
        self.logger = logger

    def execute(self, options, **kwargs):
        """Wraps the user defined run method in the proper environment"""
        self.options = options
        self.logger.debug('Running "%s" command' % self.name)
        return_code = 0
        try:
            self.run(options, **kwargs)
        except SystemExit, e:
            return_code = e.code
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return_code = 2
        finally:
            self.options = None
        return return_code

    def render_template_string(self, source, **context):
        """Render's a string using Jinja2 templates"""
        env = self.template_environment()
        template = env.from_string(source)
        return self._render(template, context)

    def render_template(self, template_name, **context):
        """Render's a template file using Jinja2 templates"""
        env = self.template_environment()
        template = env.get_template(template_name)
        return self._render(template, context)

    def template_context(self):
        """Loads the current template context. Used by _render"""
        return dict(options=self.options, command=self)

    def template_environment(self):
        """Grabs the template environment"""
        return environment()

    def _render(self, template, context):
        """Render's a template from render_template and render_template_string
        """
        base_context = self.template_context()
        base_context.update(context)
        return template.render(base_context)

    def run(self, options, **kwargs):
        """Must be overriden by subclasses"""
        raise NotImplementedError('This command does nothing')

class ProjectMixin(object):
    """A mixin that knows how to load projects"""

    def load_project(self, options):
        return Project.load(options)

class ProjectCommand(Command, ProjectMixin):
    """A command that is aware of the current project

    The current project is determined using 3 different methods:

        - VIRTUAL_ENV is in environment (this will change to a virtstrap
          specific environment variable)
        - Current working directory or parent directory contains
          a '.vs.env' directory
        - The virtstrap directory (e.g. .vs.env) and the project directory
          are both explicitly specified.

    If these methods fail, the command will fail as well.
    """
    def execute(self, options, project=None, **kwargs):
        """Wraps the user defined run method in a proper environment"""
        if not project:
            project = self.load_project(options)
        self.project = project
        self.logger.debug('Running "%s" command' % self.name)
        return_code = 0
        try:
            self.run(project, options, **kwargs)
        except SystemExit, e:
            return_code = e.code
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return_code = 2
        finally:
            self.project = None
        return return_code

    def template_context(self):
        base_dict = super(ProjectCommand, self).template_context()
        base_dict.update(dict(project=self.project))
        return base_dict

    def run(self, project, options, **kwargs):
        """Must be overriden by subclasses"""
        raise NotImplementedError('This command does nothing')
