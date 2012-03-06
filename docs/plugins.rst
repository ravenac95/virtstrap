.. _plugins:

Plugin Development
==================

.. note::
    This part of the documentation is extremely sparse and will be updated very
    soon.

One of the main goals of virtstrap is to provide a simple way to create plugins
that can extend the functions of virtstrap for each project. Plugins can add
functionality using two different objects:

- *Command* - A Command is any new command that you'd like to add to the
  command line interface

- *Hook* - A Hook is essentially an event listener. The hooks listen for 
  events that occur during a command. The default events for almost every
  command is 'before' and 'after'. As a convention, commands should declare the
  events they call.
