.. _vefile:

The VEfile
==========

The VEfile is a central point of virtstrap. It allows you to define project
metadata, requirements, and eventually options for plugins. The VEfile is
a YAML file that uses some unique conventions to define the configuration.

It's just YAML
--------------
To understand the VEfile here's a short introduction to it's structure. 
The following is a valid VEfile:

.. code-block:: yaml
    
    foo: bar
    unladen: swallow
    python_is: awesome

In it's most basic form the VEfile is a simple dictionary or key/value 
storage. The top most level of keys are considered "sections" and their 
values can be anything. In the example above the sections are ``foo``, 
``unladen``, and ``python_is``. In python this VEfile simply becomes:: 

    {'foo': 'bar', 'unladen': 'swallow', 'python_is': 'awesome' }

Just remember, you can define any key/value pair you wish in the VEfile 
and virtstrap will happily ignore any section (key) it doesn't recognize.

    
Virtstrap Sections
------------------

For the sections virtstrap does recognize, it expects particular types of 
values (although it's still pretty lenient). By design, none of the 
sections in virtstrap are required. This allows you to use virtstrap without
much thought. However, once you're done being lazy and not setting up your 
project's repeatable environment, here are the sections you can set.

- *project*: Defines the project name. By default the project name is
  inferred from it's parent directory. Set this if you'd like it to ensure
  consistency no matter where it is located.

- *requirements*: Defines the requirements for the project.


Profiles
--------

One additional, and powerful, part of VEfile's structure is it's ability to use
profiles. In virtstrap, a profile is a particular type of environment you'd
like to setup. These types of environments could be something like
*development*, *testing*, *staging*, *production*, etc. Virtstrap makes little
assumptions about the names you with to use for profiles. The *development*
profile is the single exception. Virtstrap will always use the *development*
profile if you do not specify a different profile. The reason for this is that
most of your time with virtstrap will be spent developing code, so it should be
simple.

In order to define profiles, VEfile utilizes YAML's concept of documents. Each
document in a YAML file is separated by a ``---``. The first document in the
VEfile is always the default profile. This profile is always used regardless of
the currently chosen profile. Every document after that must define a section
``profile`` whose value will be used as the profile name. Here's an
example of a VEfile that uses profiles:

.. code-block:: yaml
    
    ################################################
    # This section is the default profile
    # it is ALWAYS used. So don't put anything here
    # that isn't absolutely necessary on every
    # environment
    ################################################
    project: tobetterus

    requirements:
      - sqlalchemy
      - flask: >=0.7

    some_value: foo
    
    --- # This starts a new document (therefore a new profile)
    #########################################
    # This profile is the development profile
    # as defined by the section directly
    # below this comment
    #########################################
    profile: development
    
    # Lists and dictionaries always append the other profile's data
    # when profiles are combined
    requirements:
      - ipython

    # If it isn't a list or dictionary it's value 
    # is overridden entirely.
    # So the value of some_value if you use the 
    # development profile will be 'bar'
    some_value: bar

    ---
    profile: production

    requirements:
      - python-memcached
      - mysql-python


The VEfile above defines 3 profiles: *default*, *development*, and 
*production*.
