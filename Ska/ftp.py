"""
Light wrapper around Python ftplib to make it easier to use.  Just adds a few
convenience methods to ftplib.FTP class: ls(), ls_full(), put(), get(), and cd().
Also supports using a .netrc file which is parsed internally.
"""

import os
import warnings
import ftplib
import contextlib

__version__ = '0.4.1'


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


class SFTP(object):
    """Initialize object for simpler secure-ftp operations.

    The SFTP object has an attribute ``ftp`` which is the actual paramiko.SFTPClient
    object.  This can be used for operations not supported by this class.

    :param host: sftp host name
    :param user: user name (default=netrc value or anonymous)
    :param passwd: password (default=netrc value or anonymous@ )
    :param netrcfile: netrc file name (default=~/.netrc)
    :param logger: logger object (e.g. pyyaks.logger.get_logger())
    """
    def __init__(self, host, user=None, passwd=None, netrcfile=None, logger=None):
        import Crypto.pct_warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', Crypto.pct_warnings.PowmInsecureWarning)
            import paramiko

        auths = parse_netrc(netrcfile)
        if host in auths:
            if user is None:
                user = auths[host]['login']
            if passwd is None:
                passwd = auths[host]['password']

        transport = paramiko.Transport((host, 22))
        transport.connect(username=user, password=passwd)
        self.ftp = paramiko.SFTPClient.from_transport(transport)

        self.logger = logger
        if self.logger:
            self.logger.info('Ska.ftp: log in to {} as {}'.format(host, user))

    def __del__(self):
        """
        Delete object
        """
        self.ftp.close()

    def cd(self, dirname):
        """Change to specified directory ``dirname``.

        :param dirname: directory name
        """
        if self.logger:
            self.logger.info('Ska.ftp: cd {}'.format(dirname))
        self.ftp.chdir(dirname)

    def ls(self, dirname='.'):
        """List contents of directory ``dirname`` via NLST command.

        :param dirname: directory name
        :returns: list of file and/or directory names
        """
        if self.logger:
            self.logger.info('Ska.ftp: ls {}'.format(dirname))
        return self.ftp.listdir(dirname)

    def ls_full(self, dirname='.'):
        """List full contents of directory ``dirname``.

        :param dirname: directory name
        :returns: list of full FTP output for LIST command
        """
        if self.logger:
            self.logger.info('Ska.ftp: ls {}'.format(dirname))
        return [x.longname for x in self.ftp.listdir_attr(dirname)]

    def put(self, localfile, remotefile=None, callback=None, confirm=True):
        """Put the ``localfile`` to the FTP server as ``remotefile``.

        :param localfile: file name  on local host
        :param remotefile: file name on remote FTP host (default=localfile)
        :param callback: optional callback function that accepts bytes transferred so far
        :param confirm: confirm file size after transfer
        """
        if remotefile is None:
            remotefile = os.path.basename(localfile)
        if self.logger:
            self.logger.info('Ska.ftp: put {} as {}'.format(localfile, remotefile))
        self.ftp.put(localfile, remotefile, callback=callback, confirm=confirm)

    def get(self, remotefile, localfile=None, callback=None):
        """Get the ``remotefile`` from the FTP server as ``localfile`` on the local host.

        :param remotefile: file name on remote FTP host
        :param localfile: file name  on local host (default=remotefile)
        """
        if localfile is None:
            localfile = os.path.basename(remotefile)
        if self.logger:
            self.logger.info('Ska.ftp: get {} as {}'.format(remotefile, localfile))
        self.ftp.get(remotefile, localfile, callback=callback)

    def mkdir(self, remotedir):
        """Make remote directory

        :param remotedir: dir name on remote FTP host
        """
        if self.logger:
            self.logger.info('Ska.ftp: mkdir {}'.format(remotedir))
        self.ftp.mkdir(remotedir)

    def rename(self, oldpath, newpath):
        """Rename remote ``oldpath`` to ``newpath``

        :param oldpath: old path on remote
        :param newpath: new path on remote
        """
        if self.logger:
            self.logger.info('Ska.ftp: rename {} {}'.format(oldpath, newpath))
        self.ftp.rename(oldpath, newpath)

    def delete(self, path):
        """Delete ``path`` file

        :param path: path on remote to delete
        """
        if self.logger:
            self.logger.info('Ska.ftp: delete {}'.format(path))
        self.ftp.remove(path)

    def rmdir(self, path):
        """Delete ``path`` directory

        :param path: path on remote to delete
        """
        if self.logger:
            self.logger.info('Ska.ftp: rmdir {}'.format(path))
        self.ftp.rmdir(path)

    def __getattr__(self, attr):
        """
        Fall through to SFTPClient methods, and fail if not found.
        """
        val = getattr(self.ftp, attr)
        if self.logger:
            self.logger.info('Ska.ftp: {}'.format(attr))
        return val


class FTP(ftplib.FTP):
    """Initialize object for simpler ftp operations.

    The FTP object has an attribute ``ftp`` which is the actual ftplib.FTP()
    object.  This can be used for operations not supported by this class.

    :param host: ftp host name
    :param user: user name (default=netrc value or anonymous)
    :param passwd: password (default=netrc value or anonymous@ )
    :param netrcfile: netrc file name (default=~/.netrc)
    :param logger: logger object (e.g. pyyaks.logger.get_logger())
    """
    def __init__(self, host, user=None, passwd=None, netrcfile=None, logger=None):
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
        self.logger = logger
        if self.logger:
            self.logger.info('Ska.ftp: log in to {} as {}'.format(host, user))

    def cd(self, dirname):
        """Change to specified directory ``dirname``.

        :param dirname: directory name
        """
        if self.logger:
            self.logger.info('Ska.ftp: cd {}'.format(dirname))
        self.cwd(dirname)

    def ls(self, dirname='', *args):
        """List contents of directory ``dirname`` via NLST command.

        :param dirname: directory name
        :returns: list of file and/or directory names
        """
        if self.logger:
            self.logger.info('Ska.ftp: ls {} {}'.format(dirname, ' '.join(str(x) for x in args)))
        return self.nlst(dirname, *args)

    def ls_full(self, dirname='', *args):
        """List full contents of directory ``dirname``.

        :param dirname: directory name
        :returns: list of full FTP output for LIST command
        """
        if self.logger:
            self.logger.info('Ska.ftp: ls {} {}'.format(dirname, ' '.join(str(x) for x in args)))
        return self.dir(dirname, *args)

    def put(self, localfile, remotefile=None):
        """Put the ``localfile`` to the FTP server as ``remotefile``.

        :param localfile: file name  on local host
        :param remotefile: file name on remote FTP host (default=localfile)
        """
        if remotefile is None:
            remotefile = os.path.basename(localfile)
        if self.logger:
            self.logger.info('Ska.ftp: put {} as {}'.format(localfile, remotefile))
        with contextlib.closing(open(localfile, 'rb')) as fh:
            self.storbinary('STOR ' + remotefile, fh)

    def get(self, remotefile, localfile=None):
        """Get the ``remotefile`` from the FTP server as ``localfile`` on the local host.

        :param remotefile: file name on remote FTP host
        :param localfile: file name  on local host (default=remotefile)
        """
        if localfile is None:
            localfile = os.path.basename(remotefile)
        if self.logger:
            self.logger.info('Ska.ftp: get {} as {}'.format(remotefile, localfile))
        with contextlib.closing(open(localfile, 'wb')) as fh:
            self.retrbinary('RETR ' + remotefile, fh.write)
