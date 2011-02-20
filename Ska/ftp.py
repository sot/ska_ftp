"""
Light wrapper around Python ftplib to make it easier to use.  Just adds a few
convenience methods to ftplib.FTP class: ls(), ls_full(), put(), get(), and cd().
Also supports using a .netrc file which is parsed internally.
"""

import os
import ftplib
import contextlib

def parse_netrc(netrcfile=None):
    """Get default user and password for an FTP server by parsing a .netrc file.

    The returned object is a dict with a key for each ``machine`` defined in
    the netrc file.  The corresponding value is another dict containing all the
    key/value pairs defined for that machine.

    Note that the ``default`` token in the .netrc file is not parsed by this
    routine.  See ``man netrc`` for information on the format of this file.

    :param netrcfile: name of the netrc file (default=~/.netrc)
    :returns: dict of configuration dicts
    """
    netrc = dict()
    if netrcfile is None:
        netrcfile = os.path.join(os.environ['HOME'], '.netrc')
    try:
        for line in open(netrcfile):
            try:
                key, val = line.split()
            except:
                machine = None
            else:
                if key == 'machine':
                    machine = val
                    netrc[machine] = dict()
                else:
                    netrc[machine][key] = val
    except IOError:
        pass
    return netrc

class FTP(ftplib.FTP):
    """Initialize object for simpler ftp operations.

    The FTP object has an attribute ``ftp`` which is the actual ftplib.FTP()
    object.  This can be used for operations not supported by this class.

    :param host: ftp host name
    :param user: user name (default=netrc value or anonymous)
    :param passwd: password (default=netrc value or anonymous@ )
    :param netrcfile: netrc file name (default=~/.netrc)
    """
    def __init__(self, host, user=None, passwd=None, netrcfile=None):
        auths = parse_netrc(netrcfile)
        if host in auths:
            if user is None:
                user = auths[host]['login']
            if passwd is None:
                passwd = auths[host]['password']
        args = []
        if user is not None:
            args.append(user)
            # Password requires that a user was specified
            if passwd is not None:
                args.append(passwd)
        ftplib.FTP.__init__(self, host)
        self.login(*args)
        self.ftp = self  # for back compatibility with initial release

    def cd(self, dirname):
        """Change to specified directory ``dirname``.

        :param dirname: directory name
        """
        self.cwd(dirname)

    def ls(self, dirname='', *args):
        """List contents of directory ``dirname`` via NLST command.

        :param dirname: directory name
        :returns: list of file and/or directory names
        """
        return self.nlst(dirname, *args)

    def ls_full(self, dirname='', *args):
        """List full contents of directory ``dirname``.

        :param dirname: directory name
        :returns: list of full FTP output for LIST command
        """
        return self.dir(dirname, *args)

    def put(self, localfile, remotefile=None):
        """Put the ``localfile`` to the FTP server as ``remotefile``.

        :param localfile: file name  on local host
        :param remotefile: file name on remote FTP host (default=localfile)
        """
        if remotefile is None:
            remotefile = os.path.basename(localfile)
        with contextlib.closing(open(localfile, 'rb')) as fh:
            self.storbinary('STOR ' + remotefile, fh)

    def get(self, remotefile, localfile=None):
        """Get the ``remotefile`` from the FTP server as ``localfile`` on the local host.

        :param remotefile: file name on remote FTP host 
        :param localfile: file name  on local host (default=remotefile)
        """
        if localfile is None:
            localfile = os.path.basename(remotefile)
        with contextlib.closing(open(localfile, 'wb')) as fh:
            self.retrbinary('RETR ' + remotefile, fh.write)

