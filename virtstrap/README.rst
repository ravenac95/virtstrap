virtstrap
=========

A simple script that allows you to setup a repeatable project using a
variety of tools. The project came out of a need to use some things
from buildout and some things from pip and virtualenv. However,
eventually buildout support was abandoned as pip and virtualenv
were powerful enough for the job.

Main Goals
----------
    
- Create repeatable projects between other developers and environments
- Provide a simple and easy to use interface
- Create Gemfile/Gemfile.lock like system
- Set custom environment variables in the virtualenv
- Setup multi python virtualenvs
- Create a plugin system similar to buildout with more flexibility
- Allow for local repository of compiled python modules so new virtstrap
  environments don't continually go online to find a module.
- A configuration file that is portable to more than just virtstrap. This
  allows for programs that aren't virtstrap to take advantage of the 
  the configuration file.

Why I made virtstrap
--------------------

Essentially, there was a short period of time where I was a little 
obsessed with using zc.buildout. However, I quickly found out that
if I needed to quickly experiment a library it was not as simple
as installing it through pip. In addition, I found buildout's support
for a ``--no-site-packages`` like function to be unsatisfactory. One
package on my Mac, ipython, was particularly finicky when using buildout.
For those of you who have not experienced it, ipython does not work well
with Leopard's version of libedit. However, installing readline via
``easy_install`` is the only way to get it to work (oddly enough it won't
work through a pip installation). So this forced me to come up with a 
solution that would solve my problems of repeatability and flexibility.

The result is virtstrap.

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

virtstrap Quick Start Guide
---------------------------

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

Links
-----

* Website Coming Soon!
* `development version 
  <http://github.com/ravenac95/virtstrap/zipball/develop#egg=virtstrap-dev>`_
