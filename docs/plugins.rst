.. _plugins:

Plugin Development Quickstart
=============================

.. note::
    This part of the documentation is extremely sparse and will be updated very
    soon.

One of the main goals of virtstrap is to provide a simple way to create plugins
that can extend the functions of virtstrap for each project. Plugins can add
functionality using two different objects:

- *Command* - A Command is any new command that you'd like to add to the
  command line interface

- *Hook* - A Hook is essentially an event listener. The hooks listen for 
  events that occur during a command. The default events for almost every
  command are ``before`` and ``after``. As a convention, commands should
  declare the events they call.

This quickstart guide goes through the creation of a hook. Eventually this will
contain information on creating new commands. 

A quick note about virtstrap's structure
----------------------------------------

In order to understand plugins, you have to understand a bit about how
virtstrap works. Virtstrap has multiple packages explained below:

* ``virtstrap-core`` - The majority of virtstrap's logic is here. The other
  packages are dependent on this package. You cannot write plugins for this
  package. If you wish to extend it then refer to :ref:`contributing`.
* ``virtstrap`` - This is the system wide package that contains the script
  for the ``vstrap`` command. It also contains the logic for the ``init``
  and ``commands`` commands. Plugins written for ``virtstrap`` apply to the
  entire system. So the plugins for ``virtstrap`` should most likely be
  commands as hooks may cause unwanted functionality on different projects.
* ``virtstrap-local`` - Contains all the logic pertaining to anything project
  specific. Plugins written for ``virtstrap-local`` allow you to vary
  functionality depending on project. In general, the suggestion is to write
  plugins for ``virtstrap-local``.

So let's start by creating a new ``virtstrap-local`` plugin.

Creating a virtstrap-local plugin
---------------------------------

Like mentioned previously, ``virtstrap-local`` is the suggested package to
extend with plugins. The reason is that your changes won't interfere with other
projects on your system and it allows your plugins to be used in a repeatable
fashion.

Step 1: Start a new python package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Virtstrap plugins, like buildout recipe's, are simply python packages. The
package simple registers a module to an entry point and virtstrap takes over
from there. So let's start out by creating a new package for to create our 
new plugin::
    
    $ mkdir virtstrap-new-plugin
    $ cd virtstrap-new-plugin
    $ mkdir virtstrap_new_plugin
    $ touch virtstrap_new_plugin/__init__.py

.. note::
    For the time being, virtstrap assumes you're using a unix environment. At
    this time windows is untested although plans are in the works for a future
    release.

What we just did is create the scaffolding for a new python package. Next,
we need to create a ``setup.py`` file. Open up your favorite editor (mine is
vim) and copy this code (you can edit this if you are actually going to use
this)::

    from setuptools import setup, find_packages
    import sys, os
    
    version = '0.0.0-dev'
    
    setup(
        name='virtstrap-new-plugin',
        version=version,
        description="A new virtstrap plugin",
        long_description="""A new virtstrap plugin""",
        classifiers=[],
        keywords='virtstrap',
        author='John Doe',
        author_email='someone@someemail-place.com',
        url='',
        license='MIT',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            #'virtstrap-local',
        ],
        entry_points={
            'virtstrap_local.plugins': [
                'plugin = virtstrap_new_plugin.plugin',
            ]
        },
    )

Step 2: Write the plugin!
~~~~~~~~~~~~~~~~~~~~~~~~~

In general the best way to get something new out of virtstrap is to use hooks
to listen for events that commands issue. Commands will almost always issue
the ``before`` and ``after`` event. The easiest way to determine what events
are available is to use the event attribute of a command. 

Here is a simple example::
    
    from virtstrap import hooks

    @hooks.create('install', ['after'])
    def new_install_hook(event, options, **kwargs):
        print "I appear after install has completed!"

So what did this all do? Let's break it down!

#. First we need to import virtstrap.hooks which provides the
   ``virtstrap.hooks.create`` decorator.

#. Next we use the ``virtstrap.hooks.create`` decorator to define what command
   event we'd like to listen to. It requires two arguments. 

   #. The name of the command that you'd like to listen to - in our case the
      ``install`` command
   #. A list of events you'd like to listen for - in this case the ``after``
      event.

#. Now we create the actual hook logic in the decorated function
   ``new_install_hook``. The decorator expects the decorated function to accept
   two arguments and an arbitrary set of keyword arguments:

   #. ``event`` - This is the current event that is being processed
   #. ``options`` - This is an object representing the command line argument
      options. It should be used as read-only.

#. Finally we just print a message to the user (using a unrecommended method of
   output more on this later)

The above example is the bare minimum you'd need to write to create a hook.
Really, it's pretty lame. It simply prints the statement ``I appear after
install has completed`` upon receiving the ``after`` event from the ``install``
command. However, let's do something a tad more interesting::
 
    from virtstrap import hooks
    from virtstrap.log import logger

    @hooks.create('install', ['after'])
    def new_install_hook(event, options, project=None, **kwargs):
        logger.info('The current path of the project is %s' % project.path())

There are three changes here.

#. We added an import on the second line to ``virtstrap.log.logger``. This is
   the recommended way to output to the user. It allows virtstrap to log any
   messages, but also display pertinent messages to the user depending on the
   verbosity settings.

#. The ``new_install_hook`` function now has a different argument list. We've
   added ``project=None`` to the list of arguments. The project argument is
   passed in by ``install`` command's ``after`` event. The project object is an
   abstraction to the current project's directory and configuration
   information. 

#. Finally on the last line we use the ``logger``'s ``info`` method to display
   the current path of the project to the user.

There, that's a bit more interesting. However, it still does almost nothing.
Let's do something crazy - like initialize a git repository!

Here goes::

    from virtstrap import hooks
    from virtstrap.log import logger
    from virtstrap.utils import call_subprocess

    @hooks.create('install', ['after'])
    def new_install_hook(event, options, project=None, **kwargs):
        logger.info('Initializing a git repository for project at %s' 
                        % project.path())
        call_subprocess(['git', 'init', project.path()], show_stdout=False)

WOO! Finally, we're getting somewhere. This is what just happened:

#. We import ``virtstrap.utils.call_subprocess``. This allows us to call a
   subprocess. It just makes dealing with subprocesses a tad bit easier. For
   now, you'll just have to trust it.

#. The next major change we introduce is running ``call_subprocess`` on the
   last line of code. What this line does is creates a git repository in your
   project root. Granted, this isn't really that useful after the install
   command has been run but it is definitely more interesting than printing out
   useless strings.

Step 3: Using the plugin
~~~~~~~~~~~~~~~~~~~~~~~~

In order for you to use this plugin let's test it out with a new
project.

Do the following in any directory you wish to use::
    
    $ mkdir test-project
    $ cd test-project

Next create a VEfile::
    
    $ vim VEfile

Place this inside of it

.. code-block:: yaml
    
    plugins:
      - virtstrap-new-plugin:
        - file://PATH_TO_PLUGIN

Just replace ``PATH_TO_PLUGIN`` with the actual path to the plugin's directory.

Step 4: Init the project. Watch the magic happen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, from within your new project directory do this::
    
    $ vstrap init

You should see the following::
    
    ... (normal virtstrap messages)
    Initializing a git repository for project at SOME_DIRECTORY
    ... (more messages)

Now you can do this::

    $ git status

And it you should see that there's a git repository in your current directory!

Recap: This is just an example and not a useful one.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As stated previously, this example isn't very useful in a real project. If
you'd like to see a useful example of this type of plugin checkout
`virtstrap-ruby-bundler`_

.. _virtstrap-ruby-bundler: https://github.com/ravenac95/virtstrap-ruby-bundler
