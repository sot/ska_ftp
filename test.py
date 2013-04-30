import os
import Ska.ftp
import tempfile
import pyyaks.logger

logger = pyyaks.logger.get_logger()


def roundtrip(logger=None):
    lucky = Ska.ftp.FTP('lucky', logger=logger)
    lucky.cd('/taldcroft')
    files_before = lucky.ls()

    tmpfile = tempfile.NamedTemporaryFile()

    local_filename = os.path.join(os.environ['HOME'], '.cshrc')
    lucky.put(local_filename, '/taldcroft/remote_cshrc')
    lucky.get('remote_cshrc', tmpfile.name)
    lucky.delete('remote_cshrc')

    files_after = lucky.ls()
    lucky.close()

    orig = open(local_filename).read()
    roundtrip = open(tmpfile.name).read()

    assert files_before == files_after
    assert orig == roundtrip


def test_roundtrip():
    roundtrip(logger)


def test_roundtrip_no_logger():
    roundtrip()
