Initialize current directory with virtstrap::
    
    vstrap init 

Initialize directory ``foo`` with virtstrap::

    vstrap init foo

Create a virtstrap project using the ``basic`` template::
    
    vstrap init -t basic

Run the current virtstrap.py in current directory::
    
    vstrap up 
    vstrap update
    vstrap up .
    vstrap update .

Run the virtstrap.py in directory ``foo``::

    vstrap update foo

Upgrade virtstrap to latest version in current directory
it may print warnings about the upgrade::

    vstrap upgrade-script 

Upgrade virtstrap to latest version in directory ``foo``::

    vstrap upgrade-script
