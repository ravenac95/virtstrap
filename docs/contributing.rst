.. _contributing:

Contributing to Virtstrap
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

A more convenient way to contribute
-----------------------------------

In order to facilitate some easier development with virtstrap. It has all been
combined into a convenient repository, `virtstrap-suite`_. This repository
contains all three of the virtstrap repositories as a submodule. It also
contains a make file that contains some convenience commands which will be
explained at a later time. It is possible that all of the three repositories
will be combined into a single repository in the future. This might make 
development much more trivial than it is currently. However, at this time, this
is the setup.

.. _virtstrap-suite: https://github.com/ravenac95/virtstrap-suite
