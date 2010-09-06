import os
import Ska.ftp
import tempfile

from nose.tools import *

def test_roundtrip():
    lucky = Ska.ftp.FTP('lucky')
    lucky.cd('/taldcroft')
    files_before = lucky.ls()

    tmpfile = tempfile.NamedTemporaryFile()
    
    local_filename = os.path.join(os.environ['HOME'], '.cshrc')
    lucky.put(local_filename, '/taldcroft/remote_cshrc')
    lucky.get('remote_cshrc', tmpfile.name)
    lucky.ftp.delete('remote_cshrc')

    files_after = lucky.ls()
    lucky.close()

    orig = open(local_filename).read()
    roundtrip = open(tmpfile.name).read()

    assert_equal(files_before, files_after)
    assert_equal(orig, roundtrip)
