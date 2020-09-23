:mod:`Ska.ftp`
======================

.. automodule:: Ska.ftp.ftp

Example
----------
::

    import os
    import Ska.ftp

    lucky = Ska.ftp.FTP('lucky')

    lucky.cd('/taldcroft')
    print lucky.ls()

    local_filename = os.path.join(os.environ['HOME'], '.cshrc')
    lucky.put(local_filename, '/taldcroft/remote_cshrc')
    lucky.get('remote_cshrc')
    lucky.delete('remote_cshrc')
    lucky.close()

    orig = open('remote_cshrc').read()
    roundtrip = open(local_filename).read()
    if orig != roundtrip:
        print "File corruption during round trip to FTP server"
    os.remove('remote_cshrc')

Netrc file
------------
The user netrc file (typically ~/.netrc) can be used to determine the username and
password for a particular FTP server.  This file *must* be set to be readable
only by the user for a minimal level of security, e.g.
::

  chmod 600 ~/.netrc

An example ~/.netrc file is::

  machine  lucky.cfa.harvard.edu
  login    taldcroft
  password not_mY_pass1word

Classes
--------

.. autoclass:: FTP
   :members:

Functions
----------

.. autofunction:: parse_netrc


