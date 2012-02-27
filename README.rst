virtstrap suite
===============

The virtstrap suite contains all the subprojects relevant to virtstrap. These
subprojects are:

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
then run ``make getsubs``. This will initialize all of the submodules for the
virtstrap suite. 
