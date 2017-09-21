# Licensed under a 3-clause BSD style license - see LICENSE.rst
from setuptools import setup

from Ska.ftp import __version__

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='Ska.ftp',
      author='Tom Aldcroft',
      description='Light wrapper around Python ftplib and paramiko.SFTPClient',
      author_email='taldcroft@cfa.harvard.edu',
      url='http://cxc.harvard.edu/mta/ASPECT/tool_doc/pydocs/Ska.ftp.html',
      version=__version__,
      zip_safe=False,
      packages=['Ska', 'Ska.ftp', 'Ska.ftp.tests'],
      package_data={'Ska.ftp.tests': ['netrc']},
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
