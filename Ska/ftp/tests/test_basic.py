import uuid
import os
import sys
import re
import Ska.ftp
import tempfile
import pyyaks.logger

logger = pyyaks.logger.get_logger()

NETRC = Ska.ftp.parse_netrc()
USER = NETRC['lucky']['login']


def roundtrip(FtpClass, logger=None):
    homedir = ('/home/' if FtpClass is Ska.ftp.SFTP else '/') + USER
    lucky = FtpClass('lucky', logger=logger)
    lucky.cd(homedir)
    files_before = lucky.ls()

    tmpfile = tempfile.NamedTemporaryFile()

    local_filename = os.path.join(os.environ['HOME'], '.cshrc')
    lucky.put(local_filename, '{}/remote_cshrc'.format(homedir))
    lucky.get('remote_cshrc', tmpfile.name)
    lucky.delete('remote_cshrc')

    files_after = lucky.ls()
    lucky.close()

    orig = open(local_filename).read()
    roundtrip = open(tmpfile.name).read()

    assert files_before == files_after
    assert orig == roundtrip


def test_roundtrip():
    # roundtrip(FtpClass=Ska.ftp.FTP, logger=logger)  # legacy of non-secure ftp
    roundtrip(FtpClass=Ska.ftp.SFTP, logger=logger)


def test_roundtrip_no_logger():
    # roundtrip(FtpClass=Ska.ftp.FTP)
    roundtrip(FtpClass=Ska.ftp.SFTP)


def test_sftp_mkdir_rmdir_rename():
    homedir = '/home/{}'.format(USER)
    lucky = Ska.ftp.SFTP('lucky', logger=logger)
    lucky.cd(homedir)

    tmpdir = str(uuid.uuid4())  # random remote dir name
    lucky.mkdir(tmpdir)
    assert tmpdir in lucky.ls()
    lucky.rmdir(tmpdir)
    assert tmpdir not in lucky.ls()

    lucky.mkdir(tmpdir)
    new = tmpdir + '-new'
    lucky.rename(tmpdir, new)
    assert new in lucky.ls()
    assert tmpdir not in lucky.ls()
    lucky.rmdir(new)

    lucky.close()


def test_delete_when_ftp_session_already_gone(capfd):
    """
    Confirm that Ska.ftp does not end up with a recursive delete if the
    paramiko ftp instance is removed before the Ska.ftp object is deleted
    """
    lucky = Ska.ftp.SFTP('lucky', logger=logger)
    # Delete the paramiko session (without explicitly closing in this test case)
    del lucky.ftp
    # Set the recursion limit
    # If Ska.ftp this hasn't been fixed to
    # avoid attribute recursion when deleting the Ska.ftp object
    # this prevents a failed test from taking a very long time.
    sys.setrecursionlimit(100)
    # And then delete the object.
    # The missing ftp attribute should raise an AttributeError, but it
    # is printed to stderr by __del__ instead of being raised
    del lucky
    out, err = capfd.readouterr()
    assert re.search('attr missing from Ska.ftp object', err) is not None
