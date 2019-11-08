# Licensed under a 3-clause BSD style license - see LICENSE.rst
import uuid
import os
import sys
import re
import Ska.ftp
import tempfile
import pyyaks.logger
import pytest

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
    Confirm that Ska.ftp does not throw attribute errors when deleted.
    """
    lucky = Ska.ftp.SFTP('lucky', logger=logger)
    # Delete the paramiko session (without explicitly closing in this test case)
    del lucky.ftp
    del lucky
    # Should see no errors in stderr when deleting the lucky object
    out, err = capfd.readouterr()
    assert err == ''


def test_parse_netrc():
    cwd = os.path.dirname(__file__)
    netrc = Ska.ftp.parse_netrc(os.path.join(cwd, 'netrc'))
    assert netrc == {'test1': {'account': None,
                               'login': 'test1_login',
                               'password': 'test1_password'},
                     'test2': {'account': 'test2_account',
                               'login': 'test2_login',
                               'password': 'test2_password'}}


def test_parse_netrc_fail():
    with pytest.raises(IOError):
        Ska.ftp.parse_netrc('does not exist')
