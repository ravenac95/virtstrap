Non-standard environment file locations
---------------------------------------

This example is used for regression testing. When using a non-standard location
for the virtstrap directory sourcing the directory will fail if the .vs.env is
missing from the root directory. Originally, this was what was wanted, but it
was later realized that it could be a nuisance. This example has multiple
internal directories to simulate the non-standard environment.

Version 0.3.8 or greater is required for this example to work.

To run just as expected for the test, do this in the ``project`` directory::
    
    $ vstrap init --virtstrap-dir=../env
    $ rm .vs.env # This will be a symlink
    $ source quickactivate # This should not fail

Have fun!
