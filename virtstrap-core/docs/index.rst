.. virtstrap documentation master file, created by
   sphinx-quickstart on Thu Jan 26 08:41:30 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Virtstrap: Simple, Repeatable Environments
==========================================

virtstrap makes your life easier, by providing a simple and repeatable
bootstrapping process. It was inspired by pip+virtualenv and buildout, but
seeks to create a unified and standard way that won't scare away any new 
python developers and will make old pythonista's lives a bit easier. All with
the wonderful convenience of the MIT License. 

With virtstrap, setting up your development environment is as simple as this::
    
    $ vstrap init

Current Features
----------------

- Provides a standard location for virtualenv
- Provide a quick and simple way to activate the current environment

Future Features
---------------

- Provide a simple plugin system
- Generate a requirements file much like a Gemfile.lock
- Allow for arbitrary environment variables to be set

User Guide
----------

.. toctree::
    :maxdepth: 2
    
    install
    quickstart
    vefile

