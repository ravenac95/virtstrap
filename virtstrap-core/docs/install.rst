.. _install:

Virtstrap Installation Guide
============================

Recommended Method
------------------

Pip is the recommended method for installing virtstrap. Simply do::

    $ pip install virtstrap==dev

.. admonition:: Do not install previous versions

    Please do not install any previous versions of virtstrap. This
    development documentation does not cover any of those versions 
    and starting with 0.3.0 the usage has changed significantly. The
    older versions are only being supported for internal use and 
    historical reasons. Eventually those will be removed from PyPI
    to avoid confusion.

If you only have easy_install, you should install pip before continuing and
execute the command above.

Once it has completed all the correct dependencies should be installed. 

Installation from source
------------------------

If you'd like the bleeding edge you can clone the repository on GitHub::
    
    $ git clone git://github.com/ravenac95/virtstrap.git

To install it onto your system do::
    
    $ python setup.py install
