.. _install:

Virtstrap Installation Guide
============================

Recommended Method
------------------

Pip is the recommended method for installing virtstrap. Simply do::

    $ pip install virtstrap

If you only have easy_install, you should install pip before continuing and
execute the command above.

Once it has completed all the correct dependencies should be installed. 

Installation From Source
------------------------

Due to the complexity of installing from source. It is highly discouraged at
this time. However, this should hopefully work for most people

First grab the code::
    
    $ git clone git://github.com/ravenac95/virtstrap-suite.git

Install the code::
    
    $ make install

If you'd like to be able edit the code use this command instead::

    $ make install-develop

But if you're ready to do that you may want to look at :ref:`contributing` to
get started.
