.. _quickstart:

Virtstrap Quickstart Guide
==========================

First, make sure you have virtstrap installed. If you do not, head on over to
the :ref:`install`.

Simplest virtstrap example
--------------------------

After virtstrap has been installed a command, vstrap, will be available on 
your command line. You can create an virtstrap enabled project just by
doing the following::

    $ mkdir myproject
    $ cd myproject
    $ vstrap init

This creates a virtualenv in the directory ``myproject/.vs.env`` and a 
bash script at ``myproject/quickactivate``. 

Finally, do::

    $ source quickactivate

You now have a virtualenv for ``myproject``. 

Virtstrap with basic configuration
----------------------------------

In the previous section we created the most simple type of virtstrap
environment possible. However, without any configuration files virtstrap
is a bit anemic. So let's start a simple configuration file to go along
with the previous example.

In your favorite editor start a file called ``VEfile`` in your myproject 
directory (mine is vim)::

    $ vim VEfile

Let's say you'd like to grab two packages: Armin Ronacher's wonderful 
`Flask`_ micro web framework, and Kenneth Reitz's amazing `requests`_
HTTP library. Put the following inside ``VEfile``::
    
    requirements
      - flask
      - requests: '>=0.10'

.. _Flask: http://flask.pocoo.org/
.. _requests: http://python-requests.org/

Save your file and run this command in your shell::
    
    $ vstrap install

This command runs the installation portion of the init command. Doing 
``vstrap init`` would have had the same effect. The ``install`` command 
skips some of the steps involved in ``init``

After the command completes it's work, you will now have the latest version 
of *flask* and any *requests* package greater than version 0.10 inside your 
virtual environment. In order for this to happen, virtstrap converted the
requirements defined in VEfile to a pip requirements. Pip then takes over
and installs all of the requirements.

In the future, the VEfile will also generate a file called VEfile.lock which
will contain the exact versions of the packages you just installed. This file
like, Ruby Bundler's Gemfile.lock, should be added into your repository to
create a truly repeatable project environment.

Repeatable environments. Because it matters
-------------------------------------------

A repeatable environment is the main goal of virtstrap. As such let's take a
look at exactly how that all works. 

First let's get rid of the virtstrap environment. *VEfile and VEfile.lock are
not deleted*::
    
    $ vstrap clean

This brings an almost bare directory, save the configurations defined in 
VEfile.lock and VEfile. Finally do::
    
    $ vstrap init

Your project is now brought us back to the state before we ran 
``vstrap clean``. The implication of this is that say you and Bob are working
on this project together. Instead of emailing you and asking you about all the
dependencies or manually creating a virtualenv and running a pip requirements
all bob has to do is type the following inside his cloned project directory::
    
    $ vstrap init

Now you're both ready to go. Beautiful isn't it :-)?
