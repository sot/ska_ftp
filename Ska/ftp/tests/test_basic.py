# Licensed under a 3-clause BSD style license - see LICENSE.rst
import uuid
import os
import random
from pathlib import Path
import Ska.ftp
import tempfile
import pyyaks.logger
import pytest

logger = pyyaks.logger.get_logger()

NETRC = Ska.ftp.parse_netrc()
LUCKY = 'lucky.cfa.harvard.edu'


def roundtrip(FtpClass, logger=None):
    user = NETRC[LUCKY]['login']
    homedir = ('/home/' if FtpClass is Ska.ftp.SFTP else '/') + user
    lucky = FtpClass(LUCKY, logger=logger)
    lucky.cd(homedir)
    files_before = lucky.ls()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile_in = Path(tmpdir, 'tmpfile_in')
        tmpfile_out = Path(tmpdir, 'tmpfile_out')
        text = ''.join(random.choices('abcdefghijklmno', k=100))
        with open(tmpfile_in, 'w') as fh:
            fh.write(text)

        lucky.put(tmpfile_in, f'{homedir}/remote_test_file')
        lucky.get('remote_test_file', tmpfile_out)
        lucky.delete('remote_test_file')

        files_after = lucky.ls()
        lucky.close()

        orig = open(tmpfile_in).read()
        roundtrip = open(tmpfile_out).read()

    assert files_before == files_after
    assert orig == roundtrip


def test_roundtrip():
    # roundtrip(FtpClass=Ska.ftp.FTP, logger=logger)  # legacy of non-secure ftp
    roundtrip(FtpClass=Ska.ftp.SFTP, logger=logger)


def test_roundtrip_no_logger():
    # roundtrip(FtpClass=Ska.ftp.FTP)
    roundtrip(FtpClass=Ska.ftp.SFTP)


def test_sftp_mkdir_rmdir_rename():
    user = NETRC[LUCKY]['login']
    homedir = '/home/{}'.format(user)
    lucky = Ska.ftp.SFTP(LUCKY, logger=logger)
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
    lucky = Ska.ftp.SFTP(LUCKY, logger=logger)
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


def test_no_user_no_passwd():
    with pytest.raises(ValueError, match='must provide both user and passwd'):
        Ska.ftp.SFTP('--host-not-in-netrc--')
