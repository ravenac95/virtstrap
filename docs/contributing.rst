.. _contributing:

Contributing to virtstrap
=========================

In order to provide for the an easy setup for the user, virtstrap has been
split into 3 different packages. 

* `virtstrap`_ - This is the main package that users see. It provides the
  console script ``vstrap`` which is the main interface to anything virtstrap
  related. It also contains the commands that can be used without the presence
  of a project.
* `virtstrap-core`_ - This is the core of all of the virtstrap logic. The
  majority of virtstrap's code is contained in this core package. It is also a
  dependency for the other two packages.
* `virtstrap-local`_ - This package contains any commands that can only be used
  within a project and not throughout the system.

.. _virtstrap: https://github.com/ravenac95/virtstrap
.. _virtstrap-core: https://github.com/ravenac95/virtstrap-core
.. _virtstrap-local: https://github.com/ravenac95/virtstrap-local

Virtstrap-suite: A more convenient way to contribute
----------------------------------------------------

In order to facilitate some easier development with virtstrap. It has all been
combined into a convenient repository, `virtstrap-suite`_. This repository
contains: 

- All three of the virtstrap repositories as a submodule. 
- A ``Makefile`` that contains some convenience commands which will be
  explained below. 
- This documentation source.
  
.. note::
    It is possible that all of the three repositories will be combined into a
    single repository in the future. This might make development much more
    trivial than it is currently. However, at this time, this is the setup.

.. _virtstrap-suite: https://github.com/ravenac95/virtstrap-suite

Using virtstrap-suite to develop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the suggested process for using virtstrap-suite. First, clone the
repository from github::

    $ git clone git://github.com/ravenac95/virtstrap-suite.git

Then create the working environment. This uses an old version of virtstrap.
Eventually that may be replaced by the latest stable virtstrap::
    
    $ make develop

Finally source the environment::
    
    $ source quickactivate.sh

Virtstrap-suite Makefile
~~~~~~~~~~~~~~~~~~~~~~~~

The virtstrap-suite repository contains a Makefile that has the following 
commands:

- ``getsubs`` - Initializes and updates all of the submodules
- ``environment`` - Setup the development environment using an old version of
  virstrap
- ``develop`` - Runs getsubs and environment.
- ``testall`` - Runs all of the tests in each of the submodules
- ``supportfiles`` - Builds the support files and places them into the
  virtstrap_support folder inside the virtstrap package.
- ``install`` -  Installs virtstrap and virtstrap-core 
- ``install-develop`` -  Installs virtstrap and virtstrap-core as 
  development versions (they're editable)
