import pytest
import ska_ftp


@pytest.fixture()
def parsed_netrc():
    return ska_ftp.parse_netrc()
