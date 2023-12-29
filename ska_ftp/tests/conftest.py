import pytest
import ska_ftp

@pytest.fixture()
def NETRC():
    return ska_ftp.parse_netrc()
