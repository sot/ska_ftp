import uuid
import os
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


def test_ftp_session_already_gone():
    lucky = Ska.ftp.SFTP('lucky', logger=logger)
    # explicitly close paramiko channel, socket, and session
    lucky.ftp.sock.get_transport().close()
    lucky.ftp.sock.close()
    lucky.ftp.close()
    # delete ftp session
    del lucky.ftp
    # explicitly run __del__ method
    lucky.__del__()
