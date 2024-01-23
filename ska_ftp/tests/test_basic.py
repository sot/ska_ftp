# Licensed under a 3-clause BSD style license - see LICENSE.rst
import uuid
import os
import random
from pathlib import Path
import ska_ftp
import tempfile
import pyyaks.logger
import pytest

logger = pyyaks.logger.get_logger()

LUCKY = "lucky.cfa.harvard.edu"


def roundtrip(user_netrc, ftp_cls, logger=None):
    user = user_netrc[LUCKY]["login"]
    homedir = ("/home/" if ftp_cls is ska_ftp.SFTP else "/") + user
    lucky = ftp_cls(LUCKY, logger=logger)
    lucky.cd(homedir)
    files_before = lucky.ls()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile_in = Path(tmpdir, "tmpfile_in")
        tmpfile_out = Path(tmpdir, "tmpfile_out")
        text = "".join(random.choices("abcdefghijklmno", k=100))
        with open(tmpfile_in, "w") as fh:
            fh.write(text)

        lucky.put(tmpfile_in, f"{homedir}/remote_test_file")
        lucky.get("remote_test_file", tmpfile_out)
        lucky.delete("remote_test_file")

        files_after = lucky.ls()
        lucky.close()

        orig = open(tmpfile_in).read()
        roundtrip = open(tmpfile_out).read()

    assert files_before == files_after
    assert orig == roundtrip


def test_roundtrip(parsed_netrc):
    # roundtrip(ftp_cls=ska_ftp.FTP, logger=logger)  # legacy of non-secure ftp
    roundtrip(parsed_netrc, ftp_cls=ska_ftp.SFTP, logger=logger)


def test_roundtrip_no_logger(parsed_netrc):
    # roundtrip(ftp_cls=ska_ftp.FTP)
    roundtrip(parsed_netrc, ftp_cls=ska_ftp.SFTP)


def test_sftp_mkdir_rmdir_rename(parsed_netrc):
    user = parsed_netrc[LUCKY]["login"]
    homedir = "/home/{}".format(user)
    lucky = ska_ftp.SFTP(LUCKY, logger=logger)
    lucky.cd(homedir)

    tmpdir = str(uuid.uuid4())  # random remote dir name
    lucky.mkdir(tmpdir)
    assert tmpdir in lucky.ls()
    lucky.rmdir(tmpdir)
    assert tmpdir not in lucky.ls()

    lucky.mkdir(tmpdir)
    new = tmpdir + "-new"
    lucky.rename(tmpdir, new)
    assert new in lucky.ls()
    assert tmpdir not in lucky.ls()
    lucky.rmdir(new)

    lucky.close()


def test_delete_when_ftp_session_already_gone(capfd):
    """
    Confirm that ska_ftp does not throw attribute errors when deleted.
    """
    lucky = ska_ftp.SFTP(LUCKY, logger=logger)
    # Delete the paramiko session (without explicitly closing in this test case)
    del lucky.ftp
    del lucky
    # Should see no errors in stderr when deleting the lucky object
    out, err = capfd.readouterr()
    assert err == ""


def test_parse_netrc():
    cwd = os.path.dirname(__file__)
    my_netrc = ska_ftp.parse_netrc(os.path.join(cwd, "netrc"))
    assert my_netrc["test2"] == {
        "account": "test2_account",
        "login": "test2_login",
        "password": "test2_password",
    }

    # test1 has no account and different versions of netrc return
    # this as either None or ''.  Unlikely to be an issue in practice.
    assert my_netrc["test1"]["account"] in [None, ""]
    assert my_netrc["test1"]["login"] == "test1_login"
    assert my_netrc["test1"]["password"] == "test1_password"


def test_parse_netrc_fail():
    with pytest.raises(IOError):
        ska_ftp.parse_netrc("does not exist")


def test_no_user_no_passwd():
    with pytest.raises(ValueError, match="must provide both user and passwd"):
        ska_ftp.SFTP("--host-not-in-netrc--")
