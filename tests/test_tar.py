import os
import Ska.ftp
import tarfile
import cPickle as pickle
from cStringIO import StringIO

import pytest

os.chdir(os.path.dirname(__file__))

NETRC = Ska.ftp.parse_netrc()
USER = NETRC['lucky']['login']


# Here for legacy, perhaps change to a different ftp host
@pytest.mark.skipif(True, reason='Lucky no longer supports ftp')
def test_tar():
    lucky = Ska.ftp.FTP('lucky')
    lucky.cd('/{}'.format(USER))
    files_before = lucky.ls()

    tar_put_fh = StringIO()
    with tarfile.open(mode='w:gz', fileobj=tar_put_fh) as tar_put:
        tar_put.add('test_tar.py')
        tar_put.add('test_tar.py')

    obj = {'cmd': 'test',
           'tar': tar_put_fh.getvalue()}

    obj_fh_put = StringIO()
    pickle.dump(obj, obj_fh_put, protocol=-1)

    remotefile = 'test.pkl'
    obj_fh_put.seek(0)
    lucky.storbinary('STOR ' + remotefile, obj_fh_put)

    obj_fh_get = StringIO()
    lucky.retrbinary('RETR ' + remotefile, obj_fh_get.write)

    lucky.delete(remotefile)
    files_after = lucky.ls()

    assert files_before == files_after
    assert obj_fh_put.getvalue() == obj_fh_get.getvalue()

    lucky.close()

    obj_fh_get.seek(0)
    obj_get = pickle.load(obj_fh_get)
    tar = tarfile.open(mode='r', fileobj=StringIO(obj_get['tar']))

    assert tar.getnames() == ['test_tar.py', 'test_tar.py']

    test_basic = tar.extractfile('test_tar.py').read()
    assert test_basic == open('test_tar.py').read()
