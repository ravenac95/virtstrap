virtstrap
=========

A simple script that allows you to setup a repeatable project using a
variety of tools. The project came out of a need to use some things
from buildout and some things from pip and virtualenv. However,
eventually buildout support was abandoned as pip and virtualenv
were powerful enough for the job - they just needed better tools.

For the full documentation 
`go here <http://readthedocs.org/docs/virtstrap/en/latest/>`_

Main Goals
----------
    
- Create repeatable projects between other developers and environments
- Provide a simple and easy to use interface
- Create Gemfile/Gemfile.lock like system
- Set custom environment variables in the virtualenv
- Setup multi python virtualenvs
- Create a plugin system that is both flexible and simple
- Allow for local caching of compiled python modules so new virtstrap
  environments don't continually go online to find a module.
- A configuration file that is portable to more than just virtstrap. This
  allows for programs that aren't virtstrap to take advantage of the 
  the configuration file.

Current Features
----------------

- Provides a standard location for virtualenv
- Provides a quick and simple way to activate the current environment
- Generate a requirements file much like a Gemfile.lock
- Provides a simple plugin system
- Allows for arbitrary environment variables to be set

Is this yet another build tool?
-------------------------------

Yes and no. Virtstrap is meant as a layer above virtualenv+pip to give
the user buildout like capabilities without all the buildout overhead (I hope).

Why not virtualenv-wrapper?
---------------------------

I looked into using it but it did not fit my particular needs. It's a great
tool but I originally wanted to create a tool that didn't have to be installed 
system wide to see use. Now, however, I see that as a horrible oversight and 
an unnecessary limitation. Although I still feel there is something elegant 
about keeping the package out of the global system, it now seems unreasonable
to me. As a consequence, this question seems even more relevant. However,
after having built the initial versions of virtstrap, I realized 
that virtstrap could make virtualenv-wrapper even simpler. It could also be 
shared between developers, build systems, and any number of scenarios. So,
here's my crack at making something truly useful for python development.

virtstrap Quick Start
---------------------

The easiest way to get started with virtstrap is to install it
on your local machine by simply doing the following::

    pip install virtstrap

Note: If you don't want to install it into your system. Look below for
an alternative installation.

To add virtstrap to your project. The most basic usage is::

    cd path_to_your_project_path
    vstrap init

This will add a directory named ``.vs.env`` and a file called 
``quickactivate`` to your directory.

Configuration Files
-------------------

As of 0.3.x configuration files won't be required. Granted, virtstrap isn't
very useful without it, but, if you really want to start a virtstrapped 
environment without doing anything, it's as simple as ``vstrap init``.

To get more out of virtstrap you should define a ``VEfile``. This stands for
virtual environment file. This is a general purpose file to be used for 
defining your virtual environment.

The configuration file will be expected in the root directory of your project.
Any other location can be specified, but that is extremely discouraged. 

At the moment the file is a YAML file. Eventually I hope to move away from
yaml as its syntax can get in the way of defining requirements and
the general environment.

Using this repository
---------------------

This repository contains the entire suite of packages that comprise virtstrap.
These packages are:

- **virtstrap**: This is the main wrapper for the virtstrap suite. It is the
  package that is installed via pip or easy_install.
- **virtstrap-core**: The core data structures and logic for all of virtstrap
  exist in this package. It is the largest and most important of the three
  packages. 
- **virtstrap-local**: This contains the builtin commands that can only be used
  with the existence of a virtstrap project (i.e. you need to have run ``vstrap
  init`` in the directory to make a project)

This repository contains many tools to assist in the development of virtstrap.
Many of which will be documented later. 

In order to begin developing with the virtstrap suite, clone the repository
then run:: 

    $ make develop
    
This will initialize all of the submodules for the virtstrap suite and also
setup the proper virtualenv. Finally do::
    
    $ source quickactivate.sh 

and you'll be in the proper virtual environment.

Links
-----

- `Documentation <http://readthedocs.org/docs/virtstrap/en/latest/>`_
