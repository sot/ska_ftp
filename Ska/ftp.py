"""
Light wrapper around Python ftplib to make it easier to use.  Just adds a few
convenience methods to ftplib.FTP class: ls(), ls_full(), put(), get(), and
cd().  Also supports using a .netrc file which is parsed internally.
"""

import os
import ftplib
import contextlib
import time
import random
import string
import cPickle as pickle
from cStringIO import StringIO
import hmac
from configobj import ConfigObj

HOST = os.environ['HOSTNAME']


class FtpConfig(object):
    cfgfiles = ['.skaftp', os.environ['HOME'] + '/.skaftp']

    @property
    def cfg(self):
        if not hasattr(self, '_cfg'):
            for cfgfile in self.cfgfiles:
                if os.exists(cfgfile):
                    self._cfg = ConfigObj(cfgfile)
                    break
            else:
                self._cfg = ConfigObj()
                self._cfg['ftphost'] = 'lucky'
                self._cfg['rsync_dirs'] = []

        return self._cfg

CFG = FtpConfig()


def parse_netrc(netrcfile=None):
    """Get default user and password for an FTP server by parsing a .netrc
    file.

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
    def __init__(self, ftphost, user=None, passwd=None, netrcfile=None):
        auths = parse_netrc(netrcfile)
        if ftphost in auths:
            if user is None:
                user = auths[ftphost]['login']
            if passwd is None:
                passwd = auths[ftphost]['password']
        args = []
        if user is not None:
            args.append(user)
            # Password requires that a user was specified
            if passwd is not None:
                args.append(passwd)
        ftplib.FTP.__init__(self, ftphost)
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
        with open(localfile, 'rb') as fh:
            self.storbinary('STOR ' + remotefile, fh)

    def get(self, remotefile, localfile=None):
        """Get the ``remotefile`` from the FTP server as ``localfile`` on the
        local host.

        :param remotefile: file name on remote FTP host
        :param localfile: file name  on local host (default=remotefile)
        """
        if localfile is None:
            localfile = os.path.basename(remotefile)
        with open(localfile, 'wb') as fh:
            self.retrbinary('RETR ' + remotefile, fh.write)


class Server(object):
    def __init__(self, ftphost='lucky', maxiter=None, sleep=2):
        self.ftphost = ftphost
        self.iter = maxiter
        self.sleep = sleep
        with contextlib.closing(FTP(self.ftphost)) as self.ftp:
            self.netrc = parse_netrc()[ftphost]
            self.ftp.cd('/taldcroft/skaftp')
            self.run_server()

    def run_server(self):
        ftp = self.ftp
        while True:
            for rfile in ftp.ls():
                rhost, rsize, rhmac = rfile.split(':')
                rsize = int(rsize)
                if rhost == HOST or rhost == '':
                    size = ftp.size(rfile)
                    if rsize == size:
                        self.handler(rfile, rhmac)

            if self.iter is not None:
                self.iter -= 1
                if self.iter <= 0:
                    break
            time.sleep(self.sleep)

    def handler(self, rfile, rhmac):
        request_str = StringIO()
        self.ftp.retrbinary('RETR ' + rfile, request_str.write)
        request_str = request_str.getvalue()
        try:
            request = pickle.loads(request_str)
        except:
            # ill-formed.  Error message?
            print 'Failed to parse pickle for {}'.format(rfile)
            return

        lhmac = hmac.new(request_str, self.netrc['password'])
        if lhmac.hexdigest() != rhmac:
            print 'Mismatch between retrieved HMAC and filename HMAC'
            return

        print request
        self.ftp.delete(rfile)


def _randstr(size):
    chars = string.ascii_letters + string.digits
    lenchars = len(chars)
    randints = (random.randrange(0, lenchars) for x in xrange(size))
    randchars = (chars[i] for i in randints)
    return ''.join(randchars)


def put_request(request={'cmd': 'test'}, rhost='',
                ftphost='lucky', netrcfile=None):
    netrc = parse_netrc(netrcfile)[ftphost]

    request = request.copy()
    randstr = _randstr(128)
    request['randstr'] = randstr  # guarantee HMAC is unique
    request['rhost'] = rhost
    request['host'] = HOST
    request['ftphost'] = ftphost
    request_str = pickle.dumps(request, protocol=-1)

    lhmac = hmac.new(request_str, netrc['password'])
    size = len(request_str)

    request_str_fh = StringIO(request_str)
    rfile = ':'.join([rhost, str(size), lhmac.hexdigest()])
    with contextlib.closing(FTP(ftphost)) as ftp:
        ftp.cd('/taldcroft/skaftp')
        ftp.storbinary('STOR ' + rfile, request_str_fh)
