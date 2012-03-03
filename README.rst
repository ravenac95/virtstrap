virtstrap
=========

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
