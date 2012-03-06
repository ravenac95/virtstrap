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
any real specifications. However, once you're done being lazy and not setting
up your project's repeatable environment, here are the sections you can set.

- *project_name*: Defines the project name. By default the project name is
  inferred from a projects root directory name. Set this if you'd like it to
  ensure consistency no matter where it is located.

- *requirements*: Defines the requirements for the project. This is the most
  useful section and one that you will probably use most. Requirements are
  explained in the next section, :ref:`vefile-requirements`

- *plugins*: Defines the plugins just like you would define requirements. The
  suggested way to define plugins is declaration **Style 1** (explained in 
  :ref:`vefile-requirements`)

  .. note::
    The freezing of these requirements will be handled differently in the
    future. At this time there is no freezing of the plugin requirements, 
    this will be changed soon once a proper solution is determined.

.. _vefile-requirements:

The "requirements" Section
--------------------------

The requirements section of the VEfile allow you to define your project's
dependencies. Currently there are three styles of dependency declaration. 

1. *Package name* - This is the simplest declaration. All you do is use the
   package name so your VEfile would look like this:

   .. code-block:: yaml

        requirements:
          - some_package # Syntax
          - flask        # Example

2. *Package name with version specification* - This declaration allows you to
   specify a version or a range of versions. The syntax is similar to defining
   a just a package name, but it separates the specification string from the
   package name by a colon. See here:

   .. code-block:: yaml

        requirements:
          - some_package: "some_spec"  # Syntax
          - flask: ">=0.7"             # Example
          - requests: "<=1.0"          # Another example


   ``some_spec`` can be any specification that is allowed by python's 
   distutils.

3. *Package name with urls* - This declaration is the most complex and is 
   meant to be used when you'd like to grab a package from a repository. The
   syntax may seem verbose for those used to pip's requirement syntax, but it
   is meant to be read more easily and hopefully more usable as well. See
   here:
   
   .. code-block:: yaml

        requirements:
          - some_package2:              # Syntax for normal urls
            - url_to_package_tar_or_zip

          - some_package1:              # Syntax for VCS
            - vcs_type+url_to_repo      # vcs_type must be git|bzr|hg|svn
            - editable: true            # This is optional and makes
                                        # a package editable

          - requests:                   # Example1 (normal url)
            - https://github.com/kennethreitz/requests/tarball/v0.10.6

          - flask:                      # Example2 (VCS url)
            - git+https://github.com/mitsuhiko/flask
            - editable: true

   Those familiar with pip will see that the syntax isn't too far off. The 
   basic syntax for urls is one of two different types: the VCS url or a 
   normal url. A VCS url **must** be preceded by a type, which is any of the
   following: git, hg, bzr, or svn. The normal url must point to a tar, zip, 
   or a local directory.

Here's a full example of a requirements section that installs ``flask``,
``requests``, ``virtstrap-core``, and ``virtstrap-local``.
   
.. code-block:: yaml

    requirements:
      - flask
      - requests: ">=0.7"
      - virtstrap-core:
        - git+https://github.com/ravenac95/virtstrap-core.git
        - editable: true
      - virtstrap-local:
        - https://github.com/ravenac95/virtstrap-local/tarball/v0.3.0

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
      - flask: ">=0.7"

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

To use profiles all you have to do is specify the ``--profiles`` options on the
command line interface. You do this like so::

    $ vstrap [command] --profiles=production,development

The line about will use both the production and the development profile. So the
list of requirements installed will be ``sqlalchemy``, ``flask``, ``ipython``,
``python-memcached``, and ``mysql-python``. In addition, if you request for the
value ``some_value`` you will get the value ``bar``, but that's only really 
useful if you're developing a plugin for virtstrap.

VEfile Suggestions
------------------

These are some suggestions when creating a VEfile.

- Use spaces instead of tabs (this is pretty much a suggestion for everything 
  you write).
- Use 2 spaces for each tab level. This makes VEfiles a bit easier to read.
- Try not to specify exact versions for requirements in the VEfile. It is most
  powerful when you do not do that. Virtstrap is able to lock all the
  requirement versions so you can repeat your environment on each machine. 
- Don't specify absolute file URL's. This makes your project less repeatable.
