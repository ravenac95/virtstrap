.. _contributing:

Contributing to virtstrap
=========================

In order to provide for the an easy setup for the user, virtstrap has been
split into 3 different packages. That are all combined into a single
repository, `virtstrap`_. 

- **virtstrap** - This is the main package that users see. It provides the
  console script ``vstrap`` which is the main interface to anything virtstrap
  related. It also contains the commands that can be used without the presence
  of a project.
- **virtstrap-core** - This is the core of all of the virtstrap logic. The
  majority of virtstrap's code is contained in this core package. It is also a
  dependency for the other two packages.
- **virtstrap-local** - This package contains any commands that can only be used
  within a project and not throughout the system.

Start developing!
-----------------

To start contributing to virtstrap is pretty simple. First, fork the
repository on `github`_. Once you've
done that do the following::
    
    $ make develop
    $ source quickactivate.sh

Now you'll be in a virtualenv made for virtstrap.

Virtstrap Makefile
------------------

The virtstrap repository contains a Makefile that has the following commands:

- ``environment`` - Setup the development environment using an old version of
  virstrap
- ``develop`` - Runs getsubs and environment.
- ``testall`` - Runs all of the tests in all the packages
- ``supportfiles`` - Builds the support files and places them into the
  virtstrap_support folder inside the virtstrap package.
- ``install`` -  Installs virtstrap and virtstrap-core 
- ``install-develop`` -  Installs virtstrap and virtstrap-core as 
  development versions (they're editable)

.. _virtstrap: https://github.com/ravenac95/virtstrap
.. _github: https://github.com/ravenac95/virtstrap
